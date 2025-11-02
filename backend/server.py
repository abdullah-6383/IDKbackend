"""
FastAPI API server for Information Trust Analysis System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import uvicorn
import requests
from typing import Dict, Any
import asyncio
from datetime import datetime

# Import your analysis classes
try:
    from main import RelevanceSearchSystem
    from debate import DebateOrchestrator
except ImportError as e:
    print(f"Warning: Could not import analysis modules: {e}")
    RelevanceSearchSystem = None
    DebateOrchestrator = None

app = FastAPI(title="Information Trust Analysis System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy server configuration
DUMMY_SERVER_URL = "http://localhost:8001"

# CORS configuration for separate frontend hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class AnalysisInput(BaseModel):
    topic: str
    text: str = ""
    significance_score: float = 0.8

class DummyServerRequest(BaseModel):
    perspective: str = "all"

class AnalysisStatus(BaseModel):
    status: str
    message: str
    progress: float = 0.0

# Global state
current_analysis = None
analysis_results = []

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Information Trust Analysis System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "load_sample": "/load-sample-data", 
            "process": "/process",
            "results": "/results",
            "debate": "/debate",
            "status": "/status"
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Return a simple favicon to prevent 404 errors"""
    return HTTPException(status_code=204, detail="No favicon")

@app.get("/load-sample-data")
async def load_sample_data():
    """Load sample data from dummy server for the frontend"""
    print(f"[DEBUG] load_sample_data endpoint called")
    print(f"[DEBUG] Attempting to connect to dummy server at: {DUMMY_SERVER_URL}")
    
    try:
        print(f"[DEBUG] Making request to: {DUMMY_SERVER_URL}/data/sample-input")
        
        # Get sample input data from dummy server
        input_response = requests.get(f"{DUMMY_SERVER_URL}/data/sample-input", timeout=5)
        print(f"[DEBUG] Sample input response status: {input_response.status_code}")
        
        if input_response.status_code != 200:
            raise HTTPException(status_code=input_response.status_code, detail=f"Dummy server returned {input_response.status_code} for sample input")
        
        sample_input = input_response.json()
        print(f"[DEBUG] Sample input data: {sample_input}")
        
        # Get all perspectives data to show count
        print(f"[DEBUG] Making request to: {DUMMY_SERVER_URL}/data/perspectives/all")
        perspectives_response = requests.get(f"{DUMMY_SERVER_URL}/data/perspectives/all", timeout=5)
        print(f"[DEBUG] Perspectives response status: {perspectives_response.status_code}")
        
        total_items = 0
        if perspectives_response.status_code == 200:
            perspectives_data = perspectives_response.json()
            total_items = perspectives_data.get("total_search_items", 0)
            print(f"[DEBUG] Total items found: {total_items}")
        
        result = {
            "status": "success",
            "message": f"Sample data loaded from dummy server ({total_items} perspective items available)",
            "topic": sample_input.get("topic", ""),
            "text": sample_input.get("text", ""),
            "significance_score": sample_input.get("significance_score", 0.8),
            "total_search_items": total_items,
            "timestamp": sample_input.get("timestamp", datetime.now().isoformat())
        }
        
        print(f"[DEBUG] Returning result: {result}")
        return result
        
    except requests.RequestException as e:
        print(f"[ERROR] HTTP request error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Cannot connect to dummy server: {str(e)}")
    except Exception as e:
        print(f"[ERROR] General error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/process")
async def start_analysis(input_data: AnalysisInput):
    """Start the information trust analysis process"""
    global current_analysis, analysis_results
    
    try:
        # Save input data to file for main.py to process
        input_file_data = {
            "topic": input_data.topic,
            "text": input_data.text,
            "significance_score": input_data.significance_score
        }
        
        # Update data/input.json
        os.makedirs("data", exist_ok=True)
        with open("data/input.json", "w", encoding="utf-8") as f:
            json.dump(input_file_data, f, indent=2, ensure_ascii=False)
        
        if RelevanceSearchSystem:
            # Run analysis in background
            try:
                system = RelevanceSearchSystem()
                results = system.process_all_files()
                system.cleanup()
                
                # Load generated results
                generated_files = []
                for filename in ["relevant_common.json", "relevant_leftist.json", "relevant_rightist.json"]:
                    if os.path.exists(filename):
                        with open(filename, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            generated_files.append(data)
                
                analysis_results = generated_files
                
                return {
                    "status": "completed",
                    "message": "Analysis completed successfully",
                    "generated_files": len(generated_files),
                    "progress": 100.0
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Analysis failed: {str(e)}",
                    "progress": 0.0
                }
        else:
            # Return simulated response if modules not available
            return {
                "status": "simulated",
                "message": "Analysis modules not available, running in demo mode",
                "progress": 100.0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/results")
async def get_results():
    """Get analysis results"""
    global analysis_results
    
    if not analysis_results:
        # Return sample results for demo
        sample_results = [
            {
                "title": "Wikipedia - Charles James Kirk",
                "url": "https://en.wikipedia.org/wiki/Charles_James_Kirk",
                "snippet": "Charles James Kirk (October 14, 1993 – September 10, 2025) was an American political activist...",
                "trust_score": 0.75,
                "source_type": "Encyclopedia",
                "relevance_confidence": 0.95,
                "perspective": "common"
            },
            {
                "title": "Political Violence Analysis",
                "url": "https://example-news.com/kirk-analysis",
                "snippet": "The assassination highlights growing concerns about political violence...",
                "trust_score": 0.68,
                "source_type": "News Media",
                "relevance_confidence": 0.87,
                "perspective": "leftist"
            },
            {
                "title": "Conservative Icon Remembered",
                "url": "https://example-conservative.com/kirk-tribute",
                "snippet": "Charles Kirk's legacy as a conservative voice continues...",
                "trust_score": 0.71,
                "source_type": "Opinion Blog",
                "relevance_confidence": 0.82,
                "perspective": "rightist"
            }
        ]
        return {"results": sample_results}
    
    # Process real results
    processed_results = []
    for file_data in analysis_results:
        for item in file_data.get("items", []):
            for link in item.get("relevant_links", []):
                processed_results.append({
                    "title": link.get("title", ""),
                    "url": link.get("link", ""),
                    "snippet": link.get("snippet", ""),
                    "trust_score": link.get("trust_score", 0.5),
                    "source_type": link.get("source_type", "Unknown"),
                    "relevance_confidence": 0.8,  # Default value
                    "perspective": file_data.get("source_file", "").replace(".json", "").replace("relevant_", "")
                })
    
    return {"results": processed_results}

@app.post("/debate")
async def start_debate():
    """Start the AI debate simulation"""
    try:
        # Create sample relevant files if they don't exist (for demo)
        required_files = ["relevant_common.json", "relevant_leftist.json", "relevant_rightist.json"]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            # Create sample files for demo
            await create_sample_relevant_files()
        
        if DebateOrchestrator:
            try:
                orchestrator = DebateOrchestrator()
                result = orchestrator.conduct_debate(max_rounds=3, min_rounds=1)
                
                return {
                    "status": "completed",
                    "message": "Debate completed successfully",
                    "trust_score": result.get("trust_score", 50),
                    "debate_file": "debate_result.json"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Debate failed: {str(e)}"
                }
        else:
            # Return simulated response
            return {
                "status": "completed",
                "message": "Debate completed in demo mode",
                "trust_score": 55,
                "debate_transcript": [
                    {
                        "agent": "leftist",
                        "message": "The information surrounding Charles Kirk's death appears credible based on Wikipedia (Trust Score: 0.75), but we must consider the systemic issues that may have contributed to this tragedy."
                    },
                    {
                        "agent": "rightist", 
                        "message": "While the core facts are trustworthy, we should focus on established sources rather than speculative claims. The Wikipedia entry provides reliable information."
                    },
                    {
                        "agent": "judge",
                        "message": "Based on the debate analysis, the information receives a trust score of 55%. While the core fact is well-documented through reliable sources like Wikipedia, the circumstances vary significantly."
                    }
                ]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debate failed: {str(e)}")

async def create_sample_relevant_files():
    """Create sample relevant files for demo purposes"""
    sample_common = {
        "topic": "Charles James Kirk (October 14, 1993 – September 10, 2025)",
        "source_file": "common.json",
        "processed_at": datetime.now().isoformat(),
        "total_items": 1,
        "items": [
            {
                "text": "Charles James Kirk political activist information",
                "bias_x": 0.5,
                "significance_y": 0.8,
                "combined_score": 0.4,
                "color": "blue",
                "relevant_links": [
                    {
                        "title": "Wikipedia - Charles James Kirk",
                        "link": "https://en.wikipedia.org/wiki/Charles_James_Kirk", 
                        "snippet": "Political activist and media personality",
                        "trust_score": 0.75,
                        "source_type": "Encyclopedia"
                    }
                ]
            }
        ]
    }
    
    sample_leftist = {
        "topic": "Charles James Kirk (October 14, 1993 – September 10, 2025)",
        "source_file": "leftist.json", 
        "processed_at": datetime.now().isoformat(),
        "total_items": 1,
        "items": [
            {
                "text": "Political violence and systemic issues analysis",
                "bias_x": 0.2,
                "significance_y": 0.9,
                "combined_score": 0.18,
                "color": "red",
                "relevant_links": [
                    {
                        "title": "Analysis of Political Violence",
                        "link": "https://example-leftist.com/analysis",
                        "snippet": "Systemic issues contributing to political violence",
                        "trust_score": 0.68,
                        "source_type": "News Media"
                    }
                ]
            }
        ]
    }
    
    sample_rightist = {
        "topic": "Charles James Kirk (October 14, 1993 – September 10, 2025)",
        "source_file": "rightist.json",
        "processed_at": datetime.now().isoformat(), 
        "total_items": 1,
        "items": [
            {
                "text": "Conservative perspective on the events",
                "bias_x": 0.8,
                "significance_y": 0.9,
                "combined_score": 0.72,
                "color": "blue",
                "relevant_links": [
                    {
                        "title": "Conservative Tribute",
                        "link": "https://example-conservative.com/tribute",
                        "snippet": "Remembering a conservative icon",
                        "trust_score": 0.71,
                        "source_type": "Opinion Blog"
                    }
                ]
            }
        ]
    }
    
    # Write sample files
    with open("relevant_common.json", "w", encoding="utf-8") as f:
        json.dump(sample_common, f, indent=2, ensure_ascii=False)
    
    with open("relevant_leftist.json", "w", encoding="utf-8") as f:
        json.dump(sample_leftist, f, indent=2, ensure_ascii=False)
        
    with open("relevant_rightist.json", "w", encoding="utf-8") as f:
        json.dump(sample_rightist, f, indent=2, ensure_ascii=False)

@app.get("/debate/result")
async def get_debate_result():
    """Get the debate result"""
    try:
        if os.path.exists("debate_result.json"):
            with open("debate_result.json", "r", encoding="utf-8") as f:
                result = json.load(f)
            return result
        else:
            # Return sample debate result
            return {
                "topic": "Sample Topic",
                "trust_score": 55,
                "judgment": "Sample judgment: The information shows mixed reliability based on available sources."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load debate result: {str(e)}")

@app.get("/status")
async def get_status():
    """Get current system status"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "modules_available": {
            "analysis": RelevanceSearchSystem is not None,
            "debate": DebateOrchestrator is not None
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Information Trust Analysis System on port {port}")
    print("Frontend available at: http://localhost:{port}")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )