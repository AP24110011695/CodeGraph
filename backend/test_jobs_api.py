import urllib.request
import json
import urllib.error
import time

def check_endpoint(method, url, data=None):
    print(f"Testing {method} {url}...")
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        
        response = urllib.request.urlopen(req)
        print(f"  Status: {response.getcode()}")
        try:
            print(f"  Response: {json.loads(response.read().decode())}")
        except:
            print(f"  Response: {response.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}")
        try:
            print(f"  Response: {json.loads(e.read().decode())}")
        except:
            pass
    except Exception as e:
        print(f"  Error: {e}")

def test_jobs_api():
    base_url = "http://127.0.0.1:8000"
    
    # 1. POST /jobs/analyze/test-upload
    check_endpoint("POST", f"{base_url}/jobs/analyze/test-upload", data={})
    
    # 2. GET /jobs
    check_endpoint("GET", f"{base_url}/jobs")
    
    # 3. GET /jobs/queue/status
    check_endpoint("GET", f"{base_url}/jobs/queue/status")
    
    # 4. GET /jobs/test-job-id
    check_endpoint("GET", f"{base_url}/jobs/test-job-id")

if __name__ == "__main__":
    test_jobs_api()
