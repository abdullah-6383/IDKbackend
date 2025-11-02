"""
Simplified dummy server for testing - serves sample data from relevant_*.json files
Runs on port 8001 to simulate external data source
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import uvicorn
from datetime import datetime

app = FastAPI(title="Dummy Data Server for Testing")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data on startup
relevant_data = {"common": [], "leftist": [], "rightist": []}

def load_data():
    """Load data from relevant JSON files"""
    global relevant_data
    
    files = {
        "common": "relevant_common.json",
        "leftist": "relevant_leftist.json", 
        "rightist": "relevant_rightist.json"
    }
    
    for perspective, filename in files.items():
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    items = file_data.get('items', [])
                    relevant_data[perspective] = items
                    print(f"✓ Loaded {len(items)} items from {filename}")
            except Exception as e:
                print(f"✗ Error loading {filename}: {e}")
                relevant_data[perspective] = []
        else:
            print(f"✗ File {filename} not found")
            relevant_data[perspective] = []
    
    total = sum(len(items) for items in relevant_data.values())
    print(f"📊 Total items loaded: {total}")

# Load data when server starts
load_data()

@app.get("/")
async def root():
    return {
        "server": "Dummy Data Server",
        "purpose": "Testing Information Trust Analysis System",
        "total_items": sum(len(items) for items in relevant_data.values())
    }

@app.get("/data/sample-input")
async def get_sample_input():
    return {
        "topic": "Charles James Kirk (October 14, 1993 – September 10, 2025)",
        "text": "at the age of 31, Kirk was assassinated by gunshot on September 10, 2025, while speaking at a TPUSA debate at Utah Valley University in Orem, Utah. His assassination garnered international attention and widespread condemnation of political violence. Donald Trump announced that Kirk would be honored posthumously. Since his death, Kirk has been considered an icon of contemporary conservatism.",
        "significance_score": 0.99,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/data/perspectives/all")
async def get_all_perspectives():
    """Get data from all perspectives combined - MUST be defined before /{perspective} route"""
    all_data = {}
    combined_search_items = []
    
    for perspective in ["common", "leftist", "rightist"]:
        items = relevant_data[perspective]
        search_items = []
        
        for item in items:
            if item.get('relevant_links'):
                for link in item['relevant_links']:
                    search_item = {
                        "text": item.get('text', ''),
                        "bias_x": item.get('bias_x', 0.5),
                        "significance_y": item.get('significance_y', 0.5),
                        "combined_score": item.get('combined_score', 0.25),
                        "link_title": link.get('title', ''),
                        "link_url": link.get('link', ''),
                        "link_snippet": link.get('snippet', ''),
                        "trust_score": link.get('trust_score', 0.5),
                        "source_type": link.get('source_type', 'Unknown'),
                        "perspective": perspective
                    }
                    search_items.append(search_item)
                    combined_search_items.append(search_item)
        
        all_data[perspective] = {
            "perspective": perspective,
            "total_items": len(items),
            "search_items": search_items
        }
    
    return {
        "perspectives": all_data,
        "combined_search_items": combined_search_items,
        "total_search_items": len(combined_search_items),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/data/perspectives/{perspective}")
async def get_perspective_data(perspective: str):
    """Get data for a specific perspective - MUST be defined after /all route"""
    if perspective not in relevant_data:
        raise HTTPException(status_code=404, detail=f"Perspective '{perspective}' not found")
    
    items = relevant_data[perspective]
    search_items = []
    
    for item in items:
        if item.get('relevant_links'):
            for link in item['relevant_links']:
                search_items.append({
                    "text": item.get('text', ''),
                    "bias_x": item.get('bias_x', 0.5),
                    "significance_y": item.get('significance_y', 0.5),
                    "combined_score": item.get('combined_score', 0.25),
                    "link_title": link.get('title', ''),
                    "link_url": link.get('link', ''),
                    "link_snippet": link.get('snippet', ''),
                    "trust_score": link.get('trust_score', 0.5),
                    "source_type": link.get('source_type', 'Unknown'),
                    "perspective": perspective
                })
    
    return {
        "perspective": perspective,
        "total_items": len(items),
        "search_items": search_items,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "loaded_perspectives": list(relevant_data.keys()),
        "total_items": sum(len(items) for items in relevant_data.values())
    }

@app.post("/reload")
async def reload():
    load_data()
    return {"message": "Data reloaded", "total_items": sum(len(items) for items in relevant_data.values())}

if __name__ == "__main__":
    print("Starting Dummy Data Server on port 8001")
    uvicorn.run("dummy_server:app", host="0.0.0.0", port=8001, reload=True)