import urllib.request
import json
import urllib.error

def test_api():
    print("Checking /docs endpoint...")
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8000/docs")
        print(f"/docs status: {req.getcode()}")
        
        req2 = urllib.request.urlopen("http://127.0.0.1:8000/openapi.json")
        data = json.loads(req2.read().decode())
        print("Available endpoints in OpenAPI:")
        for path in data.get("paths", {}):
            print(f"  - {path}")
            
    except urllib.error.URLError as e:
        print(f"Error connecting: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
