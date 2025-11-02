# Information Trust Analysis System - Frontend

A comprehensive web interface for the Information Trust Analysis System that provides automated fact-checking through AI-powered search, analysis, and debate simulation.

## Features

### 🎯 Four Main Sections

1. **Input Topic** - Enter topics and context for analysis
2. **Process Flow** - Real-time monitoring of analysis steps
3. **Results** - Interactive display of analysis results with filtering
4. **Debate** - AI agents debate information trustworthiness

### 🔍 Input Section
- Topic/statement input with context
- Significance score adjustment
- Sample data loading
- One-click analysis start

### ⚙️ Process Flow Monitoring
- Real-time step-by-step progress tracking
- Visual progress bar
- Live process logs
- Status indicators for each step:
  - Data Input & Configuration
  - Query Enhancement (AI)
  - Google Search (API)
  - Content Extraction (Web Scraping)
  - Relevance Analysis (AI)
  - Trust Score Evaluation (AI)
  - Results Processing
  - AI Debate Simulation
  - Final Verdict

### 📊 Results Dashboard
- Summary cards showing:
  - Total links found
  - Relevant links count
  - Average trust score
  - Processing time
- Interactive filtering by:
  - Perspective (Common/Leftist/Rightist)
  - Trust level (High/Medium/Low)
- Detailed result cards with:
  - Source information
  - Trust scores and badges
  - Relevance confidence
  - Direct source links

### 🗣️ AI Debate Arena
- Two AI agents representing different perspectives
- Real-time debate transcript
- Judge AI provides final verdict
- Visual trust score with color-coded indicator
- Detailed reasoning and key factors

## Technology Stack

### Frontend
- **HTML5** - Semantic structure
- **CSS3** - Modern styling with gradients, animations, flexbox/grid
- **Vanilla JavaScript** - No frameworks, pure JS for performance
- **Font Awesome** - Professional icons
- **Responsive Design** - Mobile-first approach

### Backend Integration
- **FastAPI** - Python web framework
- **RESTful API** - Clean API endpoints
- **JSON** - Data exchange format
- **Real-time Updates** - Process monitoring

## Getting Started

### Prerequisites
```bash
# For backend dependencies
pip install fastapi uvicorn

# For frontend dependencies
cd frontend
npm install
```

### Running the Frontend (Separate Hosting)

1. **Start the frontend server:**
```bash
cd frontend
npm start
```

2. **Start the backend server (in separate terminal):**
```bash
cd backend
python start_backend.py
```

3. **Open your browser:**
```
http://localhost:3000  (Frontend)
http://localhost:8000  (Backend API)
```

### Alternative Startup
- **Windows**: Run `start_frontend.bat` and `start_backend.bat`
- **Linux/Mac**: Run `./start_frontend.sh` and `./start_backend.sh`

### API Endpoints

- `POST /process` - Start analysis
- `GET /results` - Get analysis results
- `POST /debate` - Start debate simulation
- `GET /debate/result` - Get debate results
- `GET /status` - System status
- `GET /health` - Health check
- `GET /data/perspectives/{perspective}` - Get sample data

Backend API available at: `http://localhost:8000`

## Usage Guide

### 1. Input Analysis Topic
1. Navigate to "Input Topic" tab
2. Enter your topic/statement
3. Add optional context
4. Set significance score (0.0-1.0)
5. Click "Start Analysis"

### 2. Monitor Progress
1. System automatically switches to "Process Flow" tab
2. Watch real-time progress through 9 steps
3. View live logs in the terminal section
4. Progress bar shows overall completion

### 3. Review Results
1. Switch to "Results" tab after analysis
2. View summary statistics
3. Apply filters to focus on specific results
4. Click result cards to explore sources
5. Use "View Source" links to verify information

### 4. Run AI Debate
1. Go to "Debate" tab
2. Click "Start Debate" (requires completed analysis)
3. Watch AI agents argue different perspectives
4. See judge's final verdict with trust score
5. Review detailed reasoning

## Features in Detail

### Real-time Process Monitoring
- Each step shows current status (Waiting/Processing/Completed/Error)
- Animated indicators for active processes
- Color-coded status system
- Detailed logging with timestamps

### Interactive Results
- Sortable and filterable results
- Trust score badges with color coding
- Source type indicators
- Relevance confidence scores
- Direct links to original sources

### AI Debate Simulation
- Two distinct AI personalities
- Progressive vs Conservative perspectives
- Real-time message display
- Judge evaluation with scoring
- Final trust percentage with visual indicator

### Responsive Design
- Mobile-friendly interface
- Tablet optimization
- Desktop experience
- Touch-friendly controls
- Adaptive layouts

## Keyboard Shortcuts

- `Ctrl + Enter` - Start analysis
- `Ctrl + D` - Start debate

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Sample Data

The system includes sample data about Charles James Kirk for demonstration purposes. Click "Load Sample" to populate fields with example content.

## Error Handling

- Graceful fallback to demo mode if backend unavailable
- Clear error messages with suggested actions
- Automatic retry mechanisms
- Status indicators for all operations

## Customization

### Styling
Edit `styles.css` to customize:
- Color schemes
- Fonts and typography
- Layout and spacing
- Animations and transitions

### Functionality
Edit `script.js` to modify:
- API endpoints (via config.js)
- Process flow steps
- UI interactions
- Data processing

### Configuration
Edit `config.js` to configure:
- Backend API URLs for different environments
- Feature flags
- UI settings

## Production Deployment

### For GCP Cloud Run:
1. Update `API_BASE_URL` in `script.js`
2. Build and deploy using provided Dockerfile
3. Set environment variables for API keys
4. Configure CORS if needed

### Security Considerations
- API keys should be server-side only
- Enable HTTPS in production
- Implement rate limiting
- Add authentication if needed

## Troubleshooting

### Common Issues:

1. **Analysis not starting:**
   - Check backend server is running
   - Verify API endpoints are accessible
   - Check browser console for errors

2. **Results not displaying:**
   - Ensure analysis completed successfully
   - Check network connectivity
   - Verify JSON data format

3. **Debate not working:**
   - Confirm analysis was run first
   - Check if relevant_*.json files exist
   - Verify debate modules are available

## Support

For issues or questions:
1. Check browser console for errors
2. Review server logs
3. Verify all dependencies installed
4. Test with sample data first