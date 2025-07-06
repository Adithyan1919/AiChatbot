# AI Chatbot - MOSDAC

A semantic search chatbot for MOSDAC (Megha-Tropiques Satellite Data Analysis Centre) website data.

## Project Structure

```
ai-chatbot/
├── backend/           # Flask API server
│   ├── app.py        # Main Flask application
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
└── mosdac-chatbot/   # Scraped data
    └── mosdac_scraper/
        └── output.json
```

## Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn

## Setup Instructions

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd ai-chatbot/backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the Flask backend:
   ```bash
   python app.py
   ```

   The backend will start on `http://localhost:5000`

### 2. Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd ai-chatbot/frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

   The frontend will start on `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. You'll see the MOSDAC Chatbot interface
3. Type your question in the input field
4. Click "Ask" to get a response based on the scraped MOSDAC website data

## Features

- **Semantic Search**: Uses sentence transformers for intelligent question matching
- **Rich Responses**: Returns titles, descriptions, images, files, and PDF text
- **Real-time**: Instant responses from the backend API
- **Modern UI**: Clean React interface with loading states

## API Endpoints

- `POST /api/ask` - Submit a question and get a response
  - Request body: `{"question": "your question here"}`
  - Response: JSON with title, description, images, files, pdf_text, and url

## Troubleshooting

1. **Backend won't start**: Make sure all dependencies are installed and the virtual environment is activated
2. **Frontend can't connect to backend**: Ensure the Flask server is running on port 5000
3. **No data loading**: Check that `output.json` exists in the `mosdac-chatbot/mosdac_scraper/` directory
4. **Port conflicts**: If ports 3000 or 5000 are in use, the servers will automatically try the next available port

## Data Source

The chatbot uses data scraped from the MOSDAC website, stored in `output.json`. This file contains structured data including:
- Page titles
- Descriptions
- Headings
- Images
- Files
- PDF text content
- URLs 