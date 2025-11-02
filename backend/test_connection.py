"""
Test script to verify dummy server and main server connectivity
"""
import requests
import time

def test_dummy_server():
    """Test if dummy server is running and responding"""
    print("=" * 60)
    print("Testing Dummy Server (port 8001)")
    print("=" * 60)
    
    try:
        # Test health endpoint
        print("\n1. Testing /health endpoint...")
        response = requests.get("http://localhost:8001/health", timeout=2)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test sample-input endpoint
        print("\n2. Testing /data/sample-input endpoint...")
        response = requests.get("http://localhost:8001/data/sample-input", timeout=2)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Topic: {data.get('topic', 'N/A')[:50]}...")
        
        # Test perspectives/all endpoint
        print("\n3. Testing /data/perspectives/all endpoint...")
        response = requests.get("http://localhost:8001/data/perspectives/all", timeout=2)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total items: {data.get('total_search_items', 0)}")
        
        print("\n✅ Dummy server is working correctly!\n")
        return True
        
    except requests.ConnectionError:
        print("\n❌ ERROR: Cannot connect to dummy server!")
        print("   Make sure dummy server is running: python dummy_server.py\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        return False

def test_main_server():
    """Test if main server is running and can reach dummy server"""
    print("=" * 60)
    print("Testing Main Server (port 8000)")
    print("=" * 60)
    
    try:
        # Test health endpoint
        print("\n1. Testing /health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=2)
        print(f"   Status: {response.status_code}")
        
        # Test load-sample-data endpoint
        print("\n2. Testing /load-sample-data endpoint...")
        response = requests.get("http://localhost:8000/load-sample-data", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Topic: {data.get('topic', 'N/A')[:50]}...")
            print(f"   Total items: {data.get('total_search_items', 0)}")
            print("\n✅ Main server is working correctly and can reach dummy server!\n")
        else:
            print(f"   Error: {response.text}")
            print("\n❌ Main server responded but with an error\n")
        
        return response.status_code == 200
        
    except requests.ConnectionError:
        print("\n❌ ERROR: Cannot connect to main server!")
        print("   Make sure main server is running: python server.py\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        return False

def test_frontend_flow():
    """Test the complete flow that frontend would use"""
    print("=" * 60)
    print("Testing Complete Frontend Flow")
    print("=" * 60)
    
    try:
        print("\nSimulating 'Load Sample' button click...")
        print("Frontend -> GET http://localhost:8000/load-sample-data")
        
        response = requests.get("http://localhost:8000/load-sample-data", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Data received:")
            print(f"   Topic: {data.get('topic', '')}")
            print(f"   Text length: {len(data.get('text', ''))} characters")
            print(f"   Significance: {data.get('significance_score', 0)}")
            print(f"   Total items: {data.get('total_search_items', 0)}")
            print("\n✅ Frontend flow is working!\n")
            return True
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(f"   Response: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CONNECTIVITY TEST SUITE")
    print("=" * 60 + "\n")
    
    # Test dummy server
    dummy_ok = test_dummy_server()
    time.sleep(1)
    
    # Test main server
    main_ok = test_main_server()
    time.sleep(1)
    
    # Test complete flow
    if dummy_ok and main_ok:
        test_frontend_flow()
    
    print("=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
