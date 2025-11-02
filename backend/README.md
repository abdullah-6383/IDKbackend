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

## ☁️ Deploy to Google Cloud Run (with Selenium)

This backend uses Selenium with headless Chromium and Chromedriver. The provided `Dockerfile` installs both and runs FastAPI via Uvicorn on Cloud Run.

Prereqs:
- Google Cloud CLI installed and authenticated
- Project and region set: `gcloud config set project <PROJECT_ID>` and `gcloud config set run/region <REGION>`

Enable APIs:
```powershell
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
```

Create Artifact Registry (Docker):
```powershell
gcloud artifacts repositories create idk-backend --repository-format=docker --location=<REGION>
```

Build and push the image (from the `backend/` folder):
```powershell
gcloud builds submit --tag <REGION>-docker.pkg.dev/<PROJECT_ID>/idk-backend/backend:latest
```

Deploy to Cloud Run:
```powershell
gcloud run deploy idk-backend \
   --image <REGION>-docker.pkg.dev/<PROJECT_ID>/idk-backend/backend:latest \
   --platform managed \
   --allow-unauthenticated \
   --set-env-vars PORT=8080
```

Recommended: move secrets to Secret Manager and inject as env vars:
```powershell
# Create secrets
gcloud secrets create GOOGLE_API_KEY --replication-policy=automatic
echo -n "<YOUR_GOOGLE_API_KEY>" | gcloud secrets versions add GOOGLE_API_KEY --data-file=-

gcloud secrets create SEARCH_ENGINE_ID --replication-policy=automatic
echo -n "<YOUR_CSE_CX>" | gcloud secrets versions add SEARCH_ENGINE_ID --data-file=-

# Re-deploy setting secrets
gcloud run services update idk-backend \
   --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SEARCH_ENGINE_ID=SEARCH_ENGINE_ID:latest
```

Notes:
- Container listens on `$PORT` and `0.0.0.0` (Cloud Run requirement).
- Selenium runs Chrome headless with `--no-sandbox` and `--disable-dev-shm-usage` via code in `main.py`.
- If your frontend will be on a custom domain, update CORS origins or set an env like `FRONTEND_ORIGIN` and handle it in `server.py`.