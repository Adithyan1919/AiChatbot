# frontend/streamlit_app.py

import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000/api/ask"
st.set_page_config(page_title="MOSDAC AI Assistant", layout="wide")

# --- HEADER ---
st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>🌐 MOSDAC AI Assistant</h1>
    <p style='text-align: center;'>Ask questions about the MOSDAC satellite data portal — Get summaries, images, files, and links instantly!</p>
    <hr style="border-top: 1px solid #bbb;">
""", unsafe_allow_html=True)

# --- INPUT FIELD ---
query = st.text_input("🤖 Ask me anything about MOSDAC:", placeholder="e.g., What is INSAT-3D?", key="query_input")

if st.button("🔍 Search"):
    if not query.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("🧠 Thinking... Fetching results..."):
            try:
                response = requests.post(API_URL, json={"question": query})
                if response.status_code != 200:
                    st.error(f"❌ API Error {response.status_code}: {response.text}")
                else:
                    data = response.json()

                    if not data.get("results"):
                        st.warning("⚠️ No relevant results found. Try a different question.")
                    else:
                        st.success(f"✅ Top results for: '{data['query']}'")

                        for i, result in enumerate(data["results"], 1):
                            st.markdown(f"---\n### 🔹 {i}. {result['title']}")
                            st.write("📝 **Summary:**", result["summary"])

                            # Description
                            if result.get("description"):
                                with st.expander("📃 Full Description"):
                                    for line in result["description"]:
                                        st.markdown(f"- {line}")

                            # Images
                            if result.get("images"):
                                st.markdown("🖼️ **Images:**")
                                cols = st.columns(min(len(result["images"]), 4))
                                for col, img_url in zip(cols, result["images"]):
                                    col.image(img_url, use_column_width=True)

                            # Files
                            if result.get("files"):
                                st.markdown("📎 **Files:**")
                                for file_url in result["files"]:
                                    st.markdown(f"- [📥 Download File]({file_url})")

                            # URL
                            if result.get("url"):
                                st.markdown(f"🌐 [Visit Source Page]({result['url']})")

                            # Keywords
                            if result.get("keywords"):
                                st.markdown(f"🔑 **Keywords:** `{', '.join(result['keywords'])}`")

            except Exception as e:
                st.error(f"❌ Failed to fetch results: {e}")
