from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import json
import os
import torch
import spacy
import datetime

print("🚀 Flask app is starting...")

app = Flask(__name__)
CORS(app)

# Load spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli.download import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Load knowledge base
DATA_FILE = os.path.join(os.path.dirname(__file__), "output.json")

try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
except Exception as e:
    print("❌ Error loading knowledge base:", e)
    raw_data = []

# Prepare corpus and metadata
documents = []
metadata = []
for item in raw_data:
    if isinstance(item, dict):
        full_text = " ".join(
            [str(x) for x in item.get("description", []) or []] +
            [str(x) for x in item.get("headings", []) or []] +
            [str(item.get("title", ""))]
        )
        documents.append(full_text)
        metadata.append(item)

# Load Sentence Transformer
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
doc_embeddings = model.encode(documents, convert_to_tensor=True, normalize_embeddings=True)

# Main Query Endpoint
@app.route("/api/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "") if request.json else ""
    if not question.strip():
        return jsonify({"error": "Question is empty"}), 400

    # 🔍 Extract keywords using spaCy
    doc = nlp(question)
    extracted_keywords = [ent.text for ent in doc.ents] or [token.text for token in doc if token.pos_ in ["NOUN", "PROPN", "ADJ"]]

    # 🔎 Semantic Search
    query_embedding = model.encode(question, convert_to_tensor=True, normalize_embeddings=True)
    query_tensor = query_embedding.unsqueeze(0) if isinstance(query_embedding, torch.Tensor) else torch.tensor(query_embedding).unsqueeze(0)
    doc_tensor = doc_embeddings if isinstance(doc_embeddings, torch.Tensor) else torch.tensor(doc_embeddings)
    scores = util.cos_sim(query_tensor, doc_tensor)[0]

    # 🏆 Get Top K matches (remove duplicates)
    top_k = 3
    top_indices = list(dict.fromkeys(torch.topk(scores, k=top_k + 3).indices.tolist()))[:top_k]

    results = []
    for idx in top_indices:
        result = metadata[idx]
        matched_text = documents[idx]
        image_urls = result.get("images", []) or ["https://via.placeholder.com/300?text=No+Image"]

        result_dict = {
            "title": result.get("title", "No Title"),
            "description": result.get("description", []),
            "images": image_urls,
            "files": result.get("files", []),
            "url": result.get("url"),
            "summary": matched_text[:300] + "..." if len(matched_text) > 300 else matched_text,
            "keywords": extracted_keywords
        }
        results.append(result_dict)

    # 📝 Log the query
    log_query(question, extracted_keywords)

    return jsonify({
        "query": question,
        "extracted_keywords": extracted_keywords,
        "results": results
    })

# 🔮 Suggestion Endpoint (optional)
@app.route("/api/suggest", methods=["POST"])
def suggest():
    text = request.json.get("text", "") if request.json else ""
    doc = nlp(text)
    keywords = [ent.text for ent in doc.ents] or [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    return jsonify({"keywords": keywords})

# 📊 Query Logger
def log_query(question, keywords):
    log_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "question": question,
        "keywords": keywords
    }
    log_file = os.path.join(os.path.dirname(__file__), "logs.json")

    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_data)

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print("⚠️ Logging failed:", e)

# 🟢 Run server
if __name__ == "__main__":
    print("✅ Flask app running at http://127.0.0.1:5000")
    app.run(debug=True)
