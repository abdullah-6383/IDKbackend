#!/usr/bin/env python3
"""
Backend-only startup script for Information Trust Analysis System
Run this to start only the backend services (API server + dummy server)
"""
import subprocess
import sys
import time
import threading
import os

def run_dummy_server():
    """Run the dummy server in a separate process"""
    print("🟡 Starting Dummy Server (port 8001)...")
    try:
        subprocess.run([sys.executable, "dummy_server.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n🟡 Dummy server stopped")

def run_api_server():
    """Run the API server in a separate process"""
    print("🟢 Starting API Server (port 8000)...")
    try:
        subprocess.run([sys.executable, "server.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n🟢 API server stopped")

def main():
    print("🚀 Starting Information Trust Analysis Backend (API Only)")
    print("=" * 60)
    print("📝 Frontend should be served separately")
    print("   Frontend: npm start (from frontend folder)")
    print("   Backend:  python start_backend.py (this script)")
    print("=" * 60)
    
    # Check if we're in the backend directory
    if not os.path.exists("server.py") or not os.path.exists("dummy_server.py"):
        print("❌ Error: Please run this script from the backend directory")
        print("   cd backend && python start_backend.py")
        sys.exit(1)
    
    print("\n🔧 Starting backend services...")
    
    # Start dummy server in background thread
    dummy_thread = threading.Thread(target=run_dummy_server, daemon=True)
    dummy_thread.start()
    
    # Give dummy server time to start
    time.sleep(2)
    
    # Start API server (this will block until Ctrl+C)
    try:
        run_api_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down backend services...")
        print("✅ Backend stopped")

if __name__ == "__main__":
    main()