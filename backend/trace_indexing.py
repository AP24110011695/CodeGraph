import requests
import logging
import tempfile
import zipfile
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a simple test repository
temp_dir = Path('trace_test_repo')
temp_dir.mkdir(exist_ok=True)

(temp_dir / 'main.py').write_text('''
def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
''')

(temp_dir / 'utils.py').write_text('''
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
''')

(temp_dir / 'config.py').write_text('''
DATABASE_URL = "sqlite:///app.db"
DEBUG = True
''')

# Create ZIP
zip_path = Path('trace_test.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in temp_dir.rglob('*'):
        if file.is_file():
            arcname = file.relative_to(temp_dir)
            zipf.write(file, arcname)

print(f'Created test ZIP: {zip_path}')

# Upload to local backend
base_url = "http://localhost:8000"
files = {"file": ("trace_test.zip", open("trace_test.zip", "rb"), "application/zip")}

print("Uploading test repository to local backend...")
response = requests.post(f"{base_url}/upload", files=files)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

upload_id = response.json()["upload_id"]
print(f"Upload ID: {upload_id}")

# Monitor the indexing status with detailed tracing
state_url = f"{base_url}/repository-state/{upload_id}"
index_url = f"{base_url}/index/{upload_id}"

print("\n=== DETAILED INDEXING PIPELINE TRACE ===\n")

for i in range(120):  # Monitor for 120 seconds
    try:
        # Get repository state
        state_response = requests.get(state_url)
        state = state_response.json()
        
        # Get index status
        index_response = requests.get(index_url)
        index = index_response.json()
        
        print(f"Step {i+1}:")
        print(f"  Repository State: {state.get('state')}")
        print(f"  Progress: {state.get('progress')}%")
        print(f"  Current Stage: {state.get('current_stage')}")
        print(f"  Index Status: {index.get('status')}")
        print(f"  Total Chunks: {index.get('statistics', {}).get('chunks', 0)}")
        print(f"  Total Embeddings: {index.get('statistics', {}).get('embeddings', 0)}")
        
        if state.get('state') == 'READY':
            print("\n=== INDEXING COMPLETED SUCCESSFULLY ===")
            break
        elif state.get('state') == 'FAILED':
            print(f"\n=== INDEXING FAILED ===")
            print(f"Failure Reason: {state.get('failure_reason')}")
            break
        elif state.get('state') == 'CANCELLED':
            print(f"\n=== INDEXING CANCELLED ===")
            break
        elif state.get('state') is None:
            print(f"\n=== STATE IS NULL - REPOSITORY MAY NOT EXIST ===")
            break
        
        time.sleep(2)
    except Exception as e:
        print(f"Error at step {i+1}: {e}")
        import traceback
        traceback.print_exc()
        break
else:
    print("\n=== INDEXING TIMED OUT AFTER 120 SECONDS ===")

# Cleanup
import os
import shutil
try:
    os.remove("trace_test.zip")
except:
    pass
try:
    shutil.rmtree("trace_test_repo")
except:
    pass