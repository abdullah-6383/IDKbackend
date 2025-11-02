# Information Trust Analysis System

A comprehensive AI-powered system for analyzing information trustworthiness through automated fact-checking, relevance analysis, and AI debate simulation.

## 🏗️ Project Structure

```
IDK/
├── frontend/              # Frontend application
│   ├── index.html        # Main HTML interface
│   ├── script.js         # JavaScript application logic
│   ├── styles.css        # CSS styling
│   └── README.md         # Frontend documentation
├── backend/              # Backend services
│   ├── server.py         # Main FastAPI server (port 8000)
│   ├── dummy_server.py   # Dummy data server (port 8001)
│   ├── main.py          # Core analysis logic
│   ├── debate.py        # Debate orchestrator
│   ├── start_backend.py # Backend startup script
│   ├── requirements.txt # Python dependencies
│   ├── data/           # Input/output data
│   ├── api/            # API configurations
│   └── README.md       # Backend documentation
└── README.md            # This file
```

## 🚀 Quick Start (Separate Hosting)

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 3. Start Backend Services
```bash
# From backend directory
cd backend
python start_backend.py
```
This starts:
- API Server on `http://localhost:8000`
- Dummy Server on `http://localhost:8001`

### 4. Start Frontend (in a new terminal)
```bash
# From frontend directory
cd frontend
npm start
```
This starts:
- Frontend Server on `http://localhost:3000`

### 5. Access the Application
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`

## 📁 Separate Hosting Benefits

✅ **Independent Deployment**: Deploy frontend and backend to different platforms  
✅ **Scalability**: Scale frontend and backend independently  
✅ **Development**: Frontend and backend teams can work separately  
✅ **CDN Ready**: Frontend can be served from CDN  
✅ **Environment Flexibility**: Different configurations for dev/staging/prod

## Usage

```powershell
python main.py
```

## Configuration

Edit `config.json` to control:
- `links_per_text`: Number of links to get per search (1-10)
- `relevance_threshold`: Minimum confidence for relevance (0.0-1.0)
- `requests_per_minute`: Gemini API rate limit (default: 10)

Edit `data/input.json` to set the topic for relevance filtering.

## How It Works

1. Extracts keywords from `data/input.json` topic
2. Reads text from `data/common.json`, `data/leftist.json`, `data/rightist.json`
3. Enhances each search query with topic keywords
4. Searches Google for each enhanced query
5. Uses Gemini 2.0 Flash to check if links are relevant to the topic
6. Checks trust score for each relevant link
7. Saves results to separate files for each source
8. Automatically handles rate limits to avoid API quota errors

## Output

Creates 3 separate files:
- `relevant_common.json` - All items from common.json
- `relevant_leftist.json` - All items from leftist.json  
- `relevant_rightist.json` - All items from rightist.json

Each file contains:
- Topic and timestamp
- All original items ordered by `combined_score` (bias_x * significance_y) descending
- For each item:
  - Original text, bias_x, significance_y, combined_score, color
  - `relevant_links` array (empty if no relevant links found)
  - For relevant links: title, URL, snippet, trust score, source type

## Rate Limiting

System automatically:
- Monitors API usage to stay under 10 requests per minute
- Waits when approaching rate limit
- Retries with longer delays on quota errors
- Prevents 429 errors

## Requirements

```powershell
pip install -r requirements.txt
```
