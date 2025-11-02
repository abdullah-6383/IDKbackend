# Backend - Information Trust Analysis System

This folder contains the backend components for the Information Trust Analysis System.

## 🏗️ Structure

```
backend/
├── server.py              # Main FastAPI server (port 8000)
├── dummy_server.py        # Dummy data server (port 8001) 
├── main.py               # Core analysis logic
├── debate.py             # Debate orchestrator
├── start_backend.py      # Startup script for both servers
├── requirements.txt      # Python dependencies
├── config.json          # Configuration file
├── rules.txt            # Analysis rules
├── data/                # Input/output data files
├── api/                 # API related files
├── search_results/      # Search results storage
└── relevant_*.json      # Sample data files
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start backend services:**
   ```bash
   python start_backend.py
   ```

   Or start them separately:
   ```bash
   # Terminal 1 - Dummy Server (port 8001)
   python dummy_server.py
   
   # Terminal 2 - API Server (port 8000)  
   python server.py
   ```

3. **Frontend Connection:**
   - Backend provides API endpoints only
   - Frontend must be served separately from `../frontend/`
   - Backend serves on `http://localhost:8000` 
   - Frontend should connect to this URL

## 🔧 Servers

### API Server (port 8000)
- Provides REST API endpoints
- Handles analysis requests
- Proxies requests to dummy server
- **No longer serves frontend files**
- Endpoint: `http://localhost:8000`

### Dummy Server (port 8001)
- Serves sample data from JSON files
- Provides test data for development
- Endpoint: `http://localhost:8001`

## 📝 Key Files

- **server.py**: Main FastAPI application server
- **dummy_server.py**: Test data server for development
- **main.py**: Core relevance search system
- **debate.py**: Debate orchestration logic
- **relevant_*.json**: Sample data for testing

## 🌐 API Endpoints

### API Server
- `GET /` - API information and available endpoints
- `GET /load-sample-data` - Load sample data from dummy server
- `POST /process` - Start analysis
- `GET /results` - Get analysis results
- `POST /debate` - Start debate
- `GET /health` - Health check

### Dummy Server  
- `GET /data/sample-input` - Get sample input data
- `GET /data/perspectives/all` - Get all perspective data
- `GET /data/perspectives/{perspective}` - Get specific perspective
- `GET /health` - Health check

## 🔗 CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (Frontend development)
- `http://127.0.0.1:3000`
- `http://localhost:8080` (Alternative frontend port)
- `http://127.0.0.1:8080`

For production, update the CORS origins in `server.py`.