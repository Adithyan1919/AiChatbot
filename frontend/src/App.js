import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await axios.post("http://localhost:5000/api/ask", {
        question: question,
      });
      setResponse(res.data);
    } catch (err) {
      setResponse({ error: "Server error. Try again later." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>🛰️ MOSDAC Smart Chat</h1>
        <p>Ask any question related to space, satellites, and weather!</p>
      </header>

      <div className="input-group">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="E.g., What is INSAT-3D?"
        />
        <button onClick={askQuestion} disabled={loading}>
          {loading ? "Searching..." : "Ask"}
        </button>
      </div>

      {response?.error && (
        <p className="error-msg">{response.error}</p>
      )}

      {response?.results?.length > 0 && (
        <div className="response">
          <h3>🔍 Top Results</h3>
          <p><strong>Extracted Keywords:</strong> {response.extracted_keywords.join(", ")}</p>

          <div className="results">
            {response.results.map((res, i) => (
              <div className="card" key={i}>
                <img
                  src={res.images[0]}
                  alt="Preview"
                  onError={(e) => (e.target.style.display = "none")}
                />
                <h4>{res.title}</h4>
                <p className="summary">{res.summary}</p>

                {res.description.length > 0 && (
                  <details>
                    <summary>📘 Description</summary>
                    <ul>
                      {res.description.map((d, idx) => (
                        <li key={idx}>{d}</li>
                      ))}
                    </ul>
                  </details>
                )}

                {res.files.length > 0 && (
                  <div className="files">
                    <h5>📁 Files</h5>
                    <ul>
                      {res.files.map((file, idx) => (
                        <li key={idx}>
                          <a href={file} target="_blank" rel="noreferrer">{file}</a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {res.url && (
                  <p>
                    🔗 <a href={res.url} target="_blank" rel="noreferrer">Visit Source</a>
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
