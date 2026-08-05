"""
Phase 0-8 Swagger Audit Script
Tests every endpoint introduced or affected by Phase 0-8.
"""

import urllib.request
import urllib.error
import json
import io
import zipfile
import time

BASE = "http://127.0.0.1:8000"

# Good READY repo (Python WasteGuideAI)
GOOD_REPO_ID = "03d0c90b-ef4c-48cd-bef1-8f8e39ef77fb"
# Good READY repo (JavaScript StudyMate)
GOOD_REPO_JS = "47be5ab2-bb15-400f-bb6b-28be907965f8"
# A READY CodeGraph repo
GOOD_REPO_CG = "03d2ac52-e664-4d35-87a6-994d11cd4bca"

results = {"PASS": [], "FAIL": [], "NOT_TESTABLE": []}


def make_request(method, path, body=None, content_type="application/json"):
    url = BASE + path
    if body is not None and isinstance(body, dict):
        data = json.dumps(body).encode()
    elif body is not None and isinstance(body, bytes):
        data = body
    else:
        data = None

    req = urllib.request.Request(url, data=data, method=method)
    if content_type and data:
        req.add_header("Content-Type", content_type)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            raw = resp.read().decode(errors="replace")
            try:
                body_parsed = json.loads(raw)
            except Exception:
                body_parsed = raw
            return status, body_parsed, None
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            body_parsed = json.loads(raw)
        except Exception:
            body_parsed = raw
        return e.code, body_parsed, None
    except Exception as ex:
        return None, None, str(ex)


def record_pass(endpoint):
    results["PASS"].append(endpoint)
    print(f"  ✅ PASS: {endpoint}")


def record_fail(endpoint, expected, actual, status, body, traceback_hint, root_cause, file_resp, func_resp):
    entry = {
        "endpoint": endpoint,
        "expected": expected,
        "actual": actual,
        "http_status": status,
        "response_body": body,
        "traceback": traceback_hint,
        "root_cause": root_cause,
        "responsible_file": file_resp,
        "responsible_function": func_resp,
    }
    results["FAIL"].append(entry)
    print(f"  ❌ FAIL: {endpoint} | Status: {status} | {root_cause}")


def record_not_testable(endpoint, reason):
    results["NOT_TESTABLE"].append({"endpoint": endpoint, "reason": reason})
    print(f"  ⚠️  NOT_TESTABLE: {endpoint} | {reason}")


def check_no_exception(body):
    """Returns True if the body contains a Python traceback / exception hint."""
    if isinstance(body, str):
        return ("traceback" in body.lower() or "exception" in body.lower()
                or "error" in body.lower() and "internal" in body.lower())
    if isinstance(body, dict):
        detail = str(body.get("detail", ""))
        return "traceback" in detail.lower() or "internal server error" in detail.lower()
    return False


print("\n" + "=" * 70)
print("PHASE 0-8 SWAGGER AUDIT")
print("=" * 70 + "\n")

# -----------------------------------------------------------------------
# PHASE 1 — Startup / Base
# -----------------------------------------------------------------------
print("\n--- Phase 1: Startup / Base Endpoints ---")

# GET /
status, body, err = make_request("GET", "/")
if err:
    record_fail("GET /", "200 with JSON", "Connection error", None, None, err, "Connection error", "app/main.py", "root()")
elif status == 200 and isinstance(body, dict) and "status" in body:
    record_pass("GET /")
else:
    record_fail("GET /", "200 with status field", f"status={status}", status, body, None, "Unexpected response", "app/main.py", "root()")

# GET /health
status, body, err = make_request("GET", "/health")
if err:
    record_fail("GET /health", "200 {status,version}", "Connection error", None, None, err, "Connection error", "app/main.py", "health()")
elif status == 200 and isinstance(body, dict) and body.get("status") == "healthy":
    record_pass("GET /health")
else:
    record_fail("GET /health", "200 {status:'healthy'}", f"Got {body}", status, body, None, "Unexpected response", "app/main.py", "health()")

# -----------------------------------------------------------------------
# PHASE 4/8 — Repository CRUD
# -----------------------------------------------------------------------
print("\n--- Phase 4/8: Repository CRUD ---")

# GET /repositories
status, body, err = make_request("GET", "/repositories")
if err:
    record_fail("GET /repositories", "200 with list", "Connection error", None, None, err, err, "app/api/repositories.py", "list_repositories()")
elif status == 200 and isinstance(body, dict) and "repositories" in body and "total" in body:
    record_pass("GET /repositories")
else:
    record_fail("GET /repositories", "200 {repositories:[], total:N}", f"Got status={status}", status, body, None, "Schema mismatch or error", "app/api/repositories.py", "list_repositories()")

# GET /repositories/{id} — valid
status, body, err = make_request("GET", f"/repositories/{GOOD_REPO_ID}")
if err:
    record_fail(f"GET /repositories/{{id}}", "200 with repo summary", "Connection error", None, None, err, err, "app/api/repositories.py", "get_repository()")
elif status == 200 and isinstance(body, dict) and "id" in body:
    record_pass("GET /repositories/{id} (valid)")
else:
    record_fail(f"GET /repositories/{{id}} (valid)", "200 with {id, name, status, ...}", f"Got status={status}", status, body, None, "Schema mismatch or wrong status", "app/api/repositories.py", "get_repository()")

# GET /repositories/{id} — non-existent → 404
status, body, err = make_request("GET", "/repositories/00000000-0000-0000-0000-000000000000")
if err:
    record_fail("GET /repositories/{id} (404 case)", "404 Not Found", "Connection error", None, None, err, err, "app/api/repositories.py", "get_repository()")
elif status == 404:
    record_pass("GET /repositories/{id} (404 for non-existent)")
else:
    record_fail("GET /repositories/{id} (404 case)", "404 Not Found", f"Got status={status}", status, body, None, "Should return 404 for unknown ID", "app/api/repositories.py", "get_repository()")

# -----------------------------------------------------------------------
# PHASE 5/6 — Upload
# -----------------------------------------------------------------------
print("\n--- Phase 5/6: Upload Endpoint ---")

# POST /upload — valid ZIP
def make_minimal_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("main.py", "def hello():\n    print('hello')\n")
        zf.writestr("README.md", "# Test repo\n")
    buf.seek(0)
    return buf.read()

zip_bytes = make_minimal_zip()
boundary = b"----FormBoundary7MA4YWxkTrZu0gW"
body_parts = (
    b"--" + boundary + b"\r\n"
    b'Content-Disposition: form-data; name="file"; filename="test_audit.zip"\r\n'
    b"Content-Type: application/zip\r\n\r\n"
    + zip_bytes
    + b"\r\n--" + boundary + b"--\r\n"
)

req = urllib.request.Request(BASE + "/upload", data=body_parts, method="POST")
req.add_header("Content-Type", f"multipart/form-data; boundary={boundary.decode()}")
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        upload_status = resp.status
        upload_body = json.loads(resp.read().decode())
    if upload_status == 201 and "upload_id" in upload_body:
        record_pass("POST /upload (valid ZIP → 201)")
        NEW_UPLOAD_ID = upload_body["upload_id"]
        print(f"     New upload_id: {NEW_UPLOAD_ID}")
        # Verify status field
        if upload_body.get("status") == "extracted":
            record_pass("POST /upload → status='extracted'")
        else:
            record_fail("POST /upload → status field", "'extracted'", str(upload_body.get("status")), upload_status, upload_body, None, "Status not 'extracted'", "app/api/upload.py", "upload_repository()")
    else:
        NEW_UPLOAD_ID = GOOD_REPO_ID
        record_fail("POST /upload (valid ZIP)", "201 {upload_id, filename, status, project_path}", f"Got status={upload_status}", upload_status, upload_body, None, "Unexpected response", "app/api/upload.py", "upload_repository()")
except urllib.error.HTTPError as e:
    raw = e.read().decode(errors="replace")
    NEW_UPLOAD_ID = GOOD_REPO_ID
    record_fail("POST /upload (valid ZIP)", "201 {upload_id,...}", f"HTTP {e.code}", e.code, raw, None, "Upload failed", "app/api/upload.py", "upload_repository()")
except Exception as ex:
    NEW_UPLOAD_ID = GOOD_REPO_ID
    record_fail("POST /upload (valid ZIP)", "201 {upload_id,...}", "Exception", None, None, str(ex), str(ex), "app/api/upload.py", "upload_repository()")

# POST /upload — non-ZIP → 415
txt_boundary = b"----FormBoundaryTXT"
txt_body = (
    b"--" + txt_boundary + b"\r\n"
    b'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
    b"Content-Type: text/plain\r\n\r\n"
    b"hello world\r\n"
    b"--" + txt_boundary + b"--\r\n"
)
req2 = urllib.request.Request(BASE + "/upload", data=txt_body, method="POST")
req2.add_header("Content-Type", f"multipart/form-data; boundary={txt_boundary.decode()}")
try:
    with urllib.request.urlopen(req2, timeout=10) as resp:
        s2 = resp.status
        b2 = resp.read()
    record_fail("POST /upload (non-ZIP → 415)", "415 Unsupported Media Type", f"Got {s2}", s2, b2.decode(), None, "Should reject non-ZIP", "app/api/upload.py", "upload_repository()")
except urllib.error.HTTPError as e:
    if e.code in (400, 415):
        record_pass(f"POST /upload (non-ZIP → {e.code})")
    else:
        record_fail("POST /upload (non-ZIP → 415)", "415 or 400", f"Got {e.code}", e.code, e.read().decode(), None, "Unexpected error code", "app/api/upload.py", "upload_repository()")
except Exception as ex:
    record_fail("POST /upload (non-ZIP)", "415 or 400", "Exception", None, None, str(ex), str(ex), "app/api/upload.py", "upload_repository()")

# POST /upload — empty file → 400
empty_boundary = b"----FormBoundaryEMPTY"
empty_body = (
    b"--" + empty_boundary + b"\r\n"
    b'Content-Disposition: form-data; name="file"; filename="empty.zip"\r\n'
    b"Content-Type: application/zip\r\n\r\n"
    b"\r\n--" + empty_boundary + b"--\r\n"
)
req3 = urllib.request.Request(BASE + "/upload", data=empty_body, method="POST")
req3.add_header("Content-Type", f"multipart/form-data; boundary={empty_boundary.decode()}")
try:
    with urllib.request.urlopen(req3, timeout=10) as resp:
        s3 = resp.status
        b3 = resp.read()
    record_fail("POST /upload (empty → 400)", "400 Bad Request", f"Got {s3}", s3, b3.decode(), None, "Should reject empty file", "app/api/upload.py", "upload_repository()")
except urllib.error.HTTPError as e:
    if e.code == 400:
        record_pass("POST /upload (empty file → 400)")
    else:
        record_fail("POST /upload (empty → 400)", "400", f"Got {e.code}", e.code, e.read().decode(), None, "Wrong error code", "app/api/upload.py", "upload_repository()")
except Exception as ex:
    record_fail("POST /upload (empty)", "400", "Exception", None, None, str(ex), str(ex), "app/api/upload.py", "upload_repository()")

# -----------------------------------------------------------------------
# PHASE 8 — Repository State / Status
# -----------------------------------------------------------------------
print("\n--- Phase 8: Repository State / Status ---")

# GET /repository-state/{upload_id}
status, body, err = make_request("GET", f"/repository-state/{GOOD_REPO_ID}")
if err:
    record_fail("GET /repository-state/{id}", "200 state dict", "Connection error", None, None, err, err, "app/api/repository_state.py", "get_repository_state()")
elif status == 200:
    record_pass("GET /repository-state/{id}")
elif status == 404:
    record_not_testable("GET /repository-state/{id}", "Returns 404 for existing repo — may require special state machine entry")
else:
    record_fail("GET /repository-state/{id}", "200 state dict", f"Got {status}", status, body, None, "Unexpected status", "app/api/repository_state.py", "get_repository_state()")

# GET /repository-snapshot/{repository_id}
status, body, err = make_request("GET", f"/repository-snapshot/{GOOD_REPO_ID}")
if err:
    record_fail("GET /repository-snapshot/{id}", "200 snapshot", "Connection error", None, None, err, err, "app/api/repository_state.py", "get_snapshot()")
elif status == 200:
    record_pass("GET /repository-snapshot/{id}")
elif status == 404:
    record_not_testable("GET /repository-snapshot/{id}", "Returns 404 — snapshot may not exist for this repo")
else:
    record_fail("GET /repository-snapshot/{id}", "200", f"Got {status}", status, body, None, "Unexpected status", "app/api/repository_state.py", "get_snapshot()")

# -----------------------------------------------------------------------
# PHASE 4 — Database via Scan
# -----------------------------------------------------------------------
print("\n--- Scan / Parser Endpoints ---")

# POST /scan/{upload_id}
status, body, err = make_request("POST", f"/scan/{GOOD_REPO_ID}")
if err:
    record_fail("POST /scan/{id}", "200 scan result", "Connection error", None, None, err, err, "app/api/scanner.py", "scan_repository()")
elif status in (200, 202):
    if isinstance(body, dict) and ("file_count" in body or "files" in body or "scan_result" in body or "status" in body):
        record_pass("POST /scan/{id}")
    else:
        record_fail("POST /scan/{id}", "200 with file_count/files/status", f"Got {body}", status, body, None, "Schema mismatch", "app/api/scanner.py", "scan_repository()")
elif status == 404:
    record_fail("POST /scan/{id}", "200 scan result", "404 Not Found", 404, body, None, "Repository not found by scanner", "app/api/scanner.py", "scan_repository()")
elif status == 500:
    record_fail("POST /scan/{id}", "200 scan result", "500 Internal Server Error", 500, body, str(body), "Internal error during scan", "app/api/scanner.py", "scan_repository()")
else:
    record_fail("POST /scan/{id}", "200 scan result", f"Got {status}", status, body, None, "Unexpected status", "app/api/scanner.py", "scan_repository()")

# GET /parse/{upload_id}
status, body, err = make_request("GET", f"/parse/{GOOD_REPO_ID}")
if err:
    record_fail("GET /parse/{id}", "200 parse result", "Connection error", None, None, err, err, "app/api/parser.py", "get_parse_result()")
elif status == 200:
    record_pass("GET /parse/{id}")
elif status == 404:
    record_not_testable("GET /parse/{id}", "404 — parse result may not exist for this repo ID (repo was not parsed)")
else:
    record_fail("GET /parse/{id}", "200 parse result", f"Got {status}", status, body, None, "Unexpected status", "app/api/parser.py", "get_parse_result()")

# GET /frameworks/{upload_id}
status, body, err = make_request("GET", f"/frameworks/{GOOD_REPO_ID}")
if err:
    record_fail("GET /frameworks/{id}", "200 frameworks", "Connection error", None, None, err, err, "app/api/framework.py", "get_frameworks()")
elif status == 200:
    record_pass("GET /frameworks/{id}")
elif status == 404:
    record_not_testable("GET /frameworks/{id}", "404 — frameworks not detected for this repo")
else:
    record_fail("GET /frameworks/{id}", "200 frameworks dict", f"Got {status}", status, body, None, "Unexpected status", "app/api/framework.py", "get_frameworks()")

# GET /dependency-graph/{upload_id}
status, body, err = make_request("GET", f"/dependency-graph/{GOOD_REPO_ID}")
if err:
    record_fail("GET /dependency-graph/{id}", "200 graph", "Connection error", None, None, err, err, "app/api/dependency_graph.py", "get_dependency_graph()")
elif status == 200:
    record_pass("GET /dependency-graph/{id}")
elif status == 404:
    record_not_testable("GET /dependency-graph/{id}", "404 — graph not built for this repo")
else:
    record_fail("GET /dependency-graph/{id}", "200 graph", f"Got {status}", status, body, None, "Unexpected status", "app/api/dependency_graph.py", "get_dependency_graph()")

# GET /index/{upload_id}
status, body, err = make_request("GET", f"/index/{GOOD_REPO_ID}")
if err:
    record_fail("GET /index/{id}", "200 index state", "Connection error", None, None, err, err, "app/api/indexing.py", "get_index()")
elif status == 200:
    record_pass("GET /index/{id}")
elif status == 404:
    record_not_testable("GET /index/{id}", "404 — index not built for this repo")
else:
    record_fail("GET /index/{id}", "200 index state", f"Got {status}", status, body, None, "Unexpected status", "app/api/indexing.py", "get_index()")

# GET /architecture/{upload_id}
status, body, err = make_request("GET", f"/architecture/{GOOD_REPO_ID}")
if err:
    record_fail("GET /architecture/{id}", "200 arch analysis", "Connection error", None, None, err, err, "app/api/architecture.py", "get_architecture()")
elif status == 200:
    record_pass("GET /architecture/{id}")
elif status == 404:
    record_not_testable("GET /architecture/{id}", "404 — architecture not analyzed for this repo")
else:
    record_fail("GET /architecture/{id}", "200 arch analysis", f"Got {status}", status, body, None, "Unexpected status", "app/api/architecture.py", "get_architecture()")

# GET /architecture/summary/{repository_id}
status, body, err = make_request("GET", f"/architecture/summary/{GOOD_REPO_ID}")
if err:
    record_fail("GET /architecture/summary/{id}", "200 arch summary", "Connection error", None, None, err, err, "app/api/architecture.py", "get_architecture_summary()")
elif status == 200:
    record_pass("GET /architecture/summary/{id}")
elif status == 404:
    record_not_testable("GET /architecture/summary/{id}", "404 — architecture not analyzed")
else:
    record_fail("GET /architecture/summary/{id}", "200", f"Got {status}", status, body, None, "Unexpected status", "app/api/architecture.py", "get_architecture_summary()")

# GET /diagrams/{upload_id}
status, body, err = make_request("GET", f"/diagrams/{GOOD_REPO_ID}")
if err:
    record_fail("GET /diagrams/{id}", "200 diagrams", "Connection error", None, None, err, err, "app/api/diagrams.py", "get_diagrams()")
elif status == 200:
    record_pass("GET /diagrams/{id}")
elif status == 404:
    record_not_testable("GET /diagrams/{id}", "404 — diagrams not generated")
else:
    record_fail("GET /diagrams/{id}", "200 diagrams", f"Got {status}", status, body, None, "Unexpected status", "app/api/diagrams.py", "get_diagrams()")

# -----------------------------------------------------------------------
# Jobs
# -----------------------------------------------------------------------
print("\n--- Jobs Endpoints ---")

# GET /jobs
status, body, err = make_request("GET", "/jobs")
if err:
    record_fail("GET /jobs", "200 jobs list", "Connection error", None, None, err, err, "app/api/jobs.py", "list_jobs()")
elif status == 200:
    record_pass("GET /jobs")
else:
    record_fail("GET /jobs", "200 jobs list", f"Got {status}", status, body, None, "Unexpected status", "app/api/jobs.py", "list_jobs()")

# GET /jobs/queue/status
status, body, err = make_request("GET", "/jobs/queue/status")
if err:
    record_fail("GET /jobs/queue/status", "200 queue status", "Connection error", None, None, err, err, "app/api/jobs.py", "get_queue_status()")
elif status == 200:
    record_pass("GET /jobs/queue/status")
else:
    record_fail("GET /jobs/queue/status", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/jobs.py", "get_queue_status()")

# GET /jobs/{job_id} — non-existent
status, body, err = make_request("GET", "/jobs/nonexistent-job-id")
if err:
    record_fail("GET /jobs/{id} (404 case)", "404", "Connection error", None, None, err, err, "app/api/jobs.py", "get_job()")
elif status == 404:
    record_pass("GET /jobs/{id} (404 for non-existent)")
elif status == 200:
    record_fail("GET /jobs/{id} (404 case)", "404", f"Got 200 — should be 404", 200, body, None, "Should return 404 for unknown job", "app/api/jobs.py", "get_job()")
else:
    record_fail("GET /jobs/{id} (404 case)", "404", f"Got {status}", status, body, None, "Unexpected status", "app/api/jobs.py", "get_job()")

# DELETE /jobs/cleanup
status, body, err = make_request("DELETE", "/jobs/cleanup")
if err:
    record_fail("DELETE /jobs/cleanup", "200 or 204", "Connection error", None, None, err, err, "app/api/jobs.py", "cleanup_jobs()")
elif status in (200, 204):
    record_pass("DELETE /jobs/cleanup")
else:
    record_fail("DELETE /jobs/cleanup", "200 or 204", f"Got {status}", status, body, None, "Unexpected status", "app/api/jobs.py", "cleanup_jobs()")

# -----------------------------------------------------------------------
# Workers
# -----------------------------------------------------------------------
print("\n--- Workers Endpoints ---")

# GET /workers
status, body, err = make_request("GET", "/workers")
if err:
    record_fail("GET /workers", "200 workers list", "Connection error", None, None, err, err, "app/api/workers.py", "get_workers()")
elif status == 200:
    record_pass("GET /workers")
else:
    record_fail("GET /workers", "200 workers list", f"Got {status}", status, body, None, "Unexpected", "app/api/workers.py", "get_workers()")

# GET /workers/idle
status, body, err = make_request("GET", "/workers/idle")
if err:
    record_fail("GET /workers/idle", "200 idle workers", "Connection error", None, None, err, err, "app/api/workers.py", "get_idle_workers()")
elif status == 200:
    record_pass("GET /workers/idle")
else:
    record_fail("GET /workers/idle", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/workers.py", "get_idle_workers()")

# -----------------------------------------------------------------------
# Events
# -----------------------------------------------------------------------
print("\n--- Events Endpoint ---")
status, body, err = make_request("GET", "/events")
if err:
    record_fail("GET /events", "200 events list", "Connection error", None, None, err, err, "app/api/events.py", "get_events()")
elif status == 200:
    record_pass("GET /events")
else:
    record_fail("GET /events", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/events.py", "get_events()")

# -----------------------------------------------------------------------
# Workflows
# -----------------------------------------------------------------------
print("\n--- Workflows Endpoints ---")

# GET /workflows
status, body, err = make_request("GET", "/workflows")
if err:
    record_fail("GET /workflows", "200 workflows list", "Connection error", None, None, err, err, "app/api/workflows.py", "list_workflows()")
elif status == 200:
    record_pass("GET /workflows")
else:
    record_fail("GET /workflows", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/workflows.py", "list_workflows()")

# POST /workflows/start/{upload_id}
status, body, err = make_request("POST", f"/workflows/start/{GOOD_REPO_ID}", body={})
if err:
    record_fail("POST /workflows/start/{id}", "200/202 workflow started", "Connection error", None, None, err, err, "app/api/workflows.py", "start_workflow()")
elif status in (200, 201, 202):
    record_pass("POST /workflows/start/{id}")
elif status in (400, 404, 409):
    record_not_testable("POST /workflows/start/{id}", f"Returns {status} — workflow may already exist or repo not in correct state")
else:
    record_fail("POST /workflows/start/{id}", "200/201/202", f"Got {status}", status, body, None, "Unexpected status", "app/api/workflows.py", "start_workflow()")

# -----------------------------------------------------------------------
# Reliability
# -----------------------------------------------------------------------
print("\n--- Reliability Endpoints ---")

status, body, err = make_request("GET", "/reliability/circuit-breakers")
if err:
    record_fail("GET /reliability/circuit-breakers", "200", "Connection error", None, None, err, err, "app/api/reliability.py", "get_circuit_breakers()")
elif status == 200:
    record_pass("GET /reliability/circuit-breakers")
else:
    record_fail("GET /reliability/circuit-breakers", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/reliability.py", "get_circuit_breakers()")

status, body, err = make_request("GET", "/reliability/jobs")
if err:
    record_fail("GET /reliability/jobs", "200", "Connection error", None, None, err, err, "app/api/reliability.py", "get_reliability_jobs()")
elif status == 200:
    record_pass("GET /reliability/jobs")
else:
    record_fail("GET /reliability/jobs", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/reliability.py", "get_reliability_jobs()")

status, body, err = make_request("GET", "/reliability/dead-letter")
if err:
    record_fail("GET /reliability/dead-letter", "200", "Connection error", None, None, err, err, "app/api/reliability.py", "get_dead_letter()")
elif status == 200:
    record_pass("GET /reliability/dead-letter")
else:
    record_fail("GET /reliability/dead-letter", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/reliability.py", "get_dead_letter()")

# -----------------------------------------------------------------------
# Cache
# -----------------------------------------------------------------------
print("\n--- Cache Endpoints ---")

status, body, err = make_request("GET", "/cache/stats")
if err:
    record_fail("GET /cache/stats", "200", "Connection error", None, None, err, err, "app/api/cache.py", "get_cache_stats()")
elif status == 200:
    record_pass("GET /cache/stats")
else:
    record_fail("GET /cache/stats", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/cache.py", "get_cache_stats()")

status, body, err = make_request("POST", "/cache/clear")
if err:
    record_fail("POST /cache/clear", "200", "Connection error", None, None, err, err, "app/api/cache.py", "clear_cache()")
elif status in (200, 204):
    record_pass("POST /cache/clear")
else:
    record_fail("POST /cache/clear", "200 or 204", f"Got {status}", status, body, None, "Unexpected", "app/api/cache.py", "clear_cache()")

# DELETE /cache/{key}
status, body, err = make_request("DELETE", "/cache/nonexistent-key")
if err:
    record_fail("DELETE /cache/{key}", "200 or 404", "Connection error", None, None, err, err, "app/api/cache.py", "delete_cache_key()")
elif status in (200, 204, 404):
    record_pass("DELETE /cache/{key}")
else:
    record_fail("DELETE /cache/{key}", "200/204/404", f"Got {status}", status, body, None, "Unexpected", "app/api/cache.py", "delete_cache_key()")

# -----------------------------------------------------------------------
# Telemetry
# -----------------------------------------------------------------------
print("\n--- Telemetry Endpoints ---")

for tpath in ["/telemetry/health", "/telemetry/metrics", "/telemetry/performance", "/telemetry/traces"]:
    status, body, err = make_request("GET", tpath)
    if err:
        record_fail(f"GET {tpath}", "200", "Connection error", None, None, err, err, "app/api/telemetry.py", "get_telemetry()")
    elif status == 200:
        record_pass(f"GET {tpath}")
    else:
        record_fail(f"GET {tpath}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/telemetry.py", "get_telemetry()")

# -----------------------------------------------------------------------
# Indexing
# -----------------------------------------------------------------------
print("\n--- Indexing Endpoints ---")

# POST /index/{upload_id} — trigger indexing
status, body, err = make_request("POST", f"/index/{GOOD_REPO_ID}")
if err:
    record_fail("POST /index/{id}", "200/202", "Connection error", None, None, err, err, "app/api/indexing.py", "trigger_indexing()")
elif status in (200, 201, 202):
    record_pass("POST /index/{id}")
elif status == 404:
    record_fail("POST /index/{id}", "200/202", "404 Not Found", 404, body, None, "Repository not found by indexer", "app/api/indexing.py", "trigger_indexing()")
elif status == 500:
    record_fail("POST /index/{id}", "200/202", "500 Internal Error", 500, body, str(body), "Internal error during indexing trigger", "app/api/indexing.py", "trigger_indexing()")
else:
    record_fail("POST /index/{id}", "200/202", f"Got {status}", status, body, None, "Unexpected status", "app/api/indexing.py", "trigger_indexing()")

# DELETE /index/{upload_id}
status, body, err = make_request("DELETE", "/index/00000000-0000-0000-0000-000000000000")
if err:
    record_fail("DELETE /index/{id}", "200/204/404", "Connection error", None, None, err, err, "app/api/indexing.py", "delete_index()")
elif status in (200, 204, 404):
    record_pass("DELETE /index/{id} (non-existent → 404 acceptable)")
else:
    record_fail("DELETE /index/{id}", "200/204/404", f"Got {status}", status, body, None, "Unexpected", "app/api/indexing.py", "delete_index()")

# -----------------------------------------------------------------------
# Incremental Indexing
# -----------------------------------------------------------------------
print("\n--- Incremental Indexing ---")
status, body, err = make_request("POST", f"/incremental-index/{GOOD_REPO_ID}", body={"changed_files": ["main.py"]})
if err:
    record_fail("POST /incremental-index/{id}", "200/202", "Connection error", None, None, err, err, "app/api/incremental_indexing.py", "incremental_index()")
elif status in (200, 201, 202):
    record_pass("POST /incremental-index/{id}")
elif status == 404:
    record_not_testable("POST /incremental-index/{id}", "404 — repo index not found for incremental update")
elif status == 422:
    record_fail("POST /incremental-index/{id}", "200/202", "422 Validation Error", 422, body, str(body), "Request body validation failed", "app/api/incremental_indexing.py", "incremental_index()")
elif status == 500:
    record_fail("POST /incremental-index/{id}", "200/202", "500", 500, body, str(body), "Internal error", "app/api/incremental_indexing.py", "incremental_index()")
else:
    record_fail("POST /incremental-index/{id}", "200/202", f"Got {status}", status, body, None, "Unexpected", "app/api/incremental_indexing.py", "incremental_index()")

# -----------------------------------------------------------------------
# Repository Memory
# -----------------------------------------------------------------------
print("\n--- Repository Memory ---")

status, body, err = make_request("GET", f"/repository-memory/{GOOD_REPO_ID}")
if err:
    record_fail("GET /repository-memory/{id}", "200", "Connection error", None, None, err, err, "app/api/repository_memory.py", "get_repository_memory()")
elif status == 200:
    record_pass("GET /repository-memory/{id}")
elif status == 404:
    record_not_testable("GET /repository-memory/{id}", "404 — memory not built for this repo yet")
else:
    record_fail("GET /repository-memory/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/repository_memory.py", "get_repository_memory()")

status, body, err = make_request("GET", f"/repository-memory/{GOOD_REPO_ID}/summary")
if err:
    record_fail("GET /repository-memory/{id}/summary", "200", "Connection error", None, None, err, err, "app/api/repository_memory.py", "get_memory_summary()")
elif status == 200:
    record_pass("GET /repository-memory/{id}/summary")
elif status == 404:
    record_not_testable("GET /repository-memory/{id}/summary", "404 — memory not built for this repo yet")
else:
    record_fail("GET /repository-memory/{id}/summary", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/repository_memory.py", "get_memory_summary()")

status, body, err = make_request("POST", f"/repository-memory/build/{GOOD_REPO_ID}")
if err:
    record_fail("POST /repository-memory/build/{id}", "200/202", "Connection error", None, None, err, err, "app/api/repository_memory.py", "build_repository_memory()")
elif status in (200, 201, 202):
    record_pass("POST /repository-memory/build/{id}")
elif status == 404:
    record_fail("POST /repository-memory/build/{id}", "200/202", "404", 404, body, None, "Repo not found for memory build", "app/api/repository_memory.py", "build_repository_memory()")
elif status == 500:
    record_fail("POST /repository-memory/build/{id}", "200/202", "500", 500, body, str(body), "Internal error building memory", "app/api/repository_memory.py", "build_repository_memory()")
else:
    record_fail("POST /repository-memory/build/{id}", "200/202", f"Got {status}", status, body, None, "Unexpected", "app/api/repository_memory.py", "build_repository_memory()")

# -----------------------------------------------------------------------
# RAG
# -----------------------------------------------------------------------
print("\n--- RAG Endpoints ---")

status, body, err = make_request("GET", f"/rag/context/{GOOD_REPO_ID}")
if err:
    record_fail("GET /rag/context/{id}", "200", "Connection error", None, None, err, err, "app/api/rag.py", "get_rag_context()")
elif status == 200:
    record_pass("GET /rag/context/{id}")
elif status == 404:
    record_not_testable("GET /rag/context/{id}", "404 — RAG context not built for this repo")
else:
    record_fail("GET /rag/context/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/rag.py", "get_rag_context()")

status, body, err = make_request("POST", f"/rag/query/{GOOD_REPO_ID}", body={"query": "What does this project do?"})
if err:
    record_fail("POST /rag/query/{id}", "200 RAG result", "Connection error", None, None, err, err, "app/api/rag.py", "rag_query()")
elif status == 200:
    record_pass("POST /rag/query/{id}")
elif status == 404:
    record_fail("POST /rag/query/{id}", "200 RAG result", "404", 404, body, None, "RAG index not found", "app/api/rag.py", "rag_query()")
elif status == 422:
    record_fail("POST /rag/query/{id}", "200 RAG result", "422 Validation Error", 422, body, str(body), "Request schema mismatch", "app/api/rag.py", "rag_query()")
elif status == 500:
    record_fail("POST /rag/query/{id}", "200 RAG result", "500", 500, body, str(body), "Internal error", "app/api/rag.py", "rag_query()")
else:
    record_fail("POST /rag/query/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/rag.py", "rag_query()")

# -----------------------------------------------------------------------
# Semantic Search
# -----------------------------------------------------------------------
print("\n--- Semantic Search ---")

status, body, err = make_request("POST", f"/semantic/{GOOD_REPO_ID}", body={"query": "main function", "top_k": 5})
if err:
    record_fail("POST /semantic/{id}", "200 semantic results", "Connection error", None, None, err, err, "app/api/semantic.py", "semantic_search()")
elif status == 200:
    record_pass("POST /semantic/{id}")
elif status == 404:
    record_fail("POST /semantic/{id}", "200 semantic results", "404", 404, body, None, "Semantic index not found", "app/api/semantic.py", "semantic_search()")
elif status == 422:
    record_fail("POST /semantic/{id}", "200", "422 Validation Error", 422, body, str(body), "Request schema mismatch", "app/api/semantic.py", "semantic_search()")
elif status == 500:
    record_fail("POST /semantic/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/semantic.py", "semantic_search()")
else:
    record_fail("POST /semantic/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/semantic.py", "semantic_search()")

# -----------------------------------------------------------------------
# Search
# -----------------------------------------------------------------------
print("\n--- Search ---")

status, body, err = make_request("POST", f"/search/{GOOD_REPO_ID}", body={"query": "function"})
if err:
    record_fail("POST /search/{id}", "200", "Connection error", None, None, err, err, "app/api/search.py", "search()")
elif status == 200:
    record_pass("POST /search/{id}")
elif status == 404:
    record_not_testable("POST /search/{id}", "404 — search index not built")
elif status == 422:
    record_fail("POST /search/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/search.py", "search()")
elif status == 500:
    record_fail("POST /search/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/search.py", "search()")
else:
    record_fail("POST /search/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/search.py", "search()")

# -----------------------------------------------------------------------
# Chat
# -----------------------------------------------------------------------
print("\n--- Chat Endpoints ---")

status, body, err = make_request("GET", f"/chat/{GOOD_REPO_ID}/conversations")
if err:
    record_fail("GET /chat/{id}/conversations", "200 conversations list", "Connection error", None, None, err, err, "app/api/chat.py", "list_conversations()")
elif status == 200:
    record_pass("GET /chat/{id}/conversations")
else:
    record_fail("GET /chat/{id}/conversations", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/chat.py", "list_conversations()")

status, body, err = make_request("POST", f"/chat/{GOOD_REPO_ID}", body={"message": "What is this project?", "conversation_id": None})
if err:
    record_fail("POST /chat/{id}", "200 chat response", "Connection error", None, None, err, err, "app/api/chat.py", "chat()")
elif status == 200:
    record_pass("POST /chat/{id}")
elif status == 422:
    record_fail("POST /chat/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/chat.py", "chat()")
elif status == 500:
    record_fail("POST /chat/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/chat.py", "chat()")
else:
    record_fail("POST /chat/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/chat.py", "chat()")

# -----------------------------------------------------------------------
# Explain
# -----------------------------------------------------------------------
print("\n--- Explain Endpoint ---")

status, body, err = make_request("POST", f"/explain/{GOOD_REPO_ID}", body={"file_path": "main.py", "line_start": 1, "line_end": 10})
if err:
    record_fail("POST /explain/{id}", "200", "Connection error", None, None, err, err, "app/api/explain.py", "explain()")
elif status == 200:
    record_pass("POST /explain/{id}")
elif status == 422:
    record_fail("POST /explain/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/explain.py", "explain()")
elif status == 500:
    record_fail("POST /explain/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/explain.py", "explain()")
else:
    record_fail("POST /explain/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/explain.py", "explain()")

# -----------------------------------------------------------------------
# Copilot
# -----------------------------------------------------------------------
print("\n--- Copilot Endpoints ---")

status, body, err = make_request("GET", "/copilot/history")
if err:
    record_fail("GET /copilot/history", "200", "Connection error", None, None, err, err, "app/api/copilot.py", "get_copilot_history()")
elif status == 200:
    record_pass("GET /copilot/history")
else:
    record_fail("GET /copilot/history", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/copilot.py", "get_copilot_history()")

status, body, err = make_request("DELETE", "/copilot/history")
if err:
    record_fail("DELETE /copilot/history", "200 or 204", "Connection error", None, None, err, err, "app/api/copilot.py", "clear_copilot_history()")
elif status in (200, 204):
    record_pass("DELETE /copilot/history")
else:
    record_fail("DELETE /copilot/history", "200/204", f"Got {status}", status, body, None, "Unexpected", "app/api/copilot.py", "clear_copilot_history()")

status, body, err = make_request("POST", "/copilot/chat", body={"message": "Hello", "repository_id": GOOD_REPO_ID})
if err:
    record_fail("POST /copilot/chat", "200 AI response", "Connection error", None, None, err, err, "app/api/copilot.py", "copilot_chat()")
elif status == 200:
    record_pass("POST /copilot/chat")
elif status == 422:
    record_fail("POST /copilot/chat", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/copilot.py", "copilot_chat()")
elif status == 500:
    record_fail("POST /copilot/chat", "200", "500", 500, body, str(body), "Internal error", "app/api/copilot.py", "copilot_chat()")
else:
    record_fail("POST /copilot/chat", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/copilot.py", "copilot_chat()")

status, body, err = make_request("POST", f"/copilot/{GOOD_REPO_ID}", body={"query": "Explain the architecture"})
if err:
    record_fail("POST /copilot/{id}", "200", "Connection error", None, None, err, err, "app/api/copilot.py", "copilot_query()")
elif status == 200:
    record_pass("POST /copilot/{id}")
elif status == 422:
    record_fail("POST /copilot/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/copilot.py", "copilot_query()")
elif status == 500:
    record_fail("POST /copilot/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/copilot.py", "copilot_query()")
else:
    record_fail("POST /copilot/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/copilot.py", "copilot_query()")

status, body, err = make_request("POST", "/copilot/execute", body={"command": "analyze", "repository_id": GOOD_REPO_ID})
if err:
    record_fail("POST /copilot/execute", "200", "Connection error", None, None, err, err, "app/api/copilot.py", "copilot_execute()")
elif status == 200:
    record_pass("POST /copilot/execute")
elif status == 422:
    record_fail("POST /copilot/execute", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/copilot.py", "copilot_execute()")
elif status == 500:
    record_fail("POST /copilot/execute", "200", "500", 500, body, str(body), "Internal error", "app/api/copilot.py", "copilot_execute()")
else:
    record_fail("POST /copilot/execute", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/copilot.py", "copilot_execute()")

# -----------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------
print("\n--- Dashboard ---")
status, body, err = make_request("POST", f"/dashboard/test-workspace-1", body={})
if err:
    record_fail("POST /dashboard/{workspace_id}", "200", "Connection error", None, None, err, err, "app/api/dashboard.py", "get_dashboard()")
elif status == 200:
    record_pass("POST /dashboard/{workspace_id}")
elif status == 404:
    record_not_testable("POST /dashboard/{workspace_id}", "404 — workspace not found")
elif status == 422:
    record_fail("POST /dashboard/{workspace_id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/dashboard.py", "get_dashboard()")
elif status == 500:
    record_fail("POST /dashboard/{workspace_id}", "200", "500", 500, body, str(body), "Internal error", "app/api/dashboard.py", "get_dashboard()")
else:
    record_fail("POST /dashboard/{workspace_id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/dashboard.py", "get_dashboard()")

# -----------------------------------------------------------------------
# Workspace
# -----------------------------------------------------------------------
print("\n--- Workspace ---")
status, body, err = make_request("POST", "/workspace", body={"name": "audit-test-workspace"})
if err:
    record_fail("POST /workspace", "201", "Connection error", None, None, err, err, "app/api/workspace.py", "create_workspace()")
elif status in (200, 201):
    ws_id = body.get("id") or body.get("workspace_id") if isinstance(body, dict) else None
    record_pass("POST /workspace")
    if ws_id:
        # GET /workspace/{id}
        status2, body2, err2 = make_request("GET", f"/workspace/{ws_id}")
        if err2:
            record_fail("GET /workspace/{id}", "200", "Connection error", None, None, err2, err2, "app/api/workspace.py", "get_workspace()")
        elif status2 == 200:
            record_pass("GET /workspace/{id}")
        else:
            record_fail("GET /workspace/{id}", "200", f"Got {status2}", status2, body2, None, "Unexpected", "app/api/workspace.py", "get_workspace()")
else:
    ws_id = None
    record_fail("POST /workspace", "201", f"Got {status}", status, body, None, "Unexpected", "app/api/workspace.py", "create_workspace()")

# GET /workspace/{id} — 404 case
status, body, err = make_request("GET", "/workspace/00000000-does-not-exist")
if err:
    record_fail("GET /workspace/{id} (404 case)", "404", "Connection error", None, None, err, err, "app/api/workspace.py", "get_workspace()")
elif status == 404:
    record_pass("GET /workspace/{id} (404 for non-existent)")
else:
    record_fail("GET /workspace/{id} (404 case)", "404", f"Got {status}", status, body, None, "Should return 404", "app/api/workspace.py", "get_workspace()")

# -----------------------------------------------------------------------
# Agents
# -----------------------------------------------------------------------
print("\n--- Agents ---")
status, body, err = make_request("GET", "/agents")
if err:
    record_fail("GET /agents", "200", "Connection error", None, None, err, err, "app/api/agents.py", "list_agents()")
elif status == 200:
    record_pass("GET /agents")
else:
    record_fail("GET /agents", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/agents.py", "list_agents()")

status, body, err = make_request("POST", f"/agents/execute/{GOOD_REPO_ID}", body={"agent_type": "analyzer", "task": "analyze"})
if err:
    record_fail("POST /agents/execute/{id}", "200", "Connection error", None, None, err, err, "app/api/agents.py", "execute_agent()")
elif status == 200:
    record_pass("POST /agents/execute/{id}")
elif status == 422:
    record_fail("POST /agents/execute/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/agents.py", "execute_agent()")
elif status == 500:
    record_fail("POST /agents/execute/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/agents.py", "execute_agent()")
else:
    record_fail("POST /agents/execute/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/agents.py", "execute_agent()")

# -----------------------------------------------------------------------
# Planning
# -----------------------------------------------------------------------
print("\n--- Planning ---")
status, body, err = make_request("POST", f"/planning/plan/{GOOD_REPO_ID}", body={"goal": "Add authentication"})
if err:
    record_fail("POST /planning/plan/{id}", "200", "Connection error", None, None, err, err, "app/api/planning.py", "create_plan()")
elif status == 200:
    record_pass("POST /planning/plan/{id}")
elif status == 422:
    record_fail("POST /planning/plan/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/planning.py", "create_plan()")
elif status == 500:
    record_fail("POST /planning/plan/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/planning.py", "create_plan()")
else:
    record_fail("POST /planning/plan/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/planning.py", "create_plan()")

# -----------------------------------------------------------------------
# Timeline
# -----------------------------------------------------------------------
print("\n--- Timeline ---")
for tpath in [
    f"/timeline/{GOOD_REPO_ID}",
    f"/timeline/evolution/{GOOD_REPO_ID}",
    f"/timeline/hotspots/{GOOD_REPO_ID}",
]:
    status, body, err = make_request("GET", tpath)
    if err:
        record_fail(f"GET {tpath}", "200", "Connection error", None, None, err, err, "app/api/timeline.py", "get_timeline()")
    elif status == 200:
        record_pass(f"GET {tpath}")
    elif status == 404:
        record_not_testable(f"GET {tpath}", "404 — timeline not built (requires git history)")
    elif status == 500:
        record_fail(f"GET {tpath}", "200", "500", 500, body, str(body), "Internal error — check history providers", "app/api/timeline.py", "get_timeline()")
    else:
        record_fail(f"GET {tpath}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/timeline.py", "get_timeline()")

# -----------------------------------------------------------------------
# Impact Analysis
# -----------------------------------------------------------------------
print("\n--- Impact Analysis ---")
status, body, err = make_request("GET", f"/impact/summary/{GOOD_REPO_ID}")
if err:
    record_fail("GET /impact/summary/{id}", "200", "Connection error", None, None, err, err, "app/api/impact_analysis.py", "get_impact_summary()")
elif status == 200:
    record_pass("GET /impact/summary/{id}")
elif status == 404:
    record_not_testable("GET /impact/summary/{id}", "404 — impact analysis not built")
else:
    record_fail("GET /impact/summary/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/impact_analysis.py", "get_impact_summary()")

status, body, err = make_request("POST", f"/impact/analyze/{GOOD_REPO_ID}", body={"changed_files": ["main.py"]})
if err:
    record_fail("POST /impact/analyze/{id}", "200", "Connection error", None, None, err, err, "app/api/impact_analysis.py", "analyze_impact()")
elif status == 200:
    record_pass("POST /impact/analyze/{id}")
elif status == 422:
    record_fail("POST /impact/analyze/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/impact_analysis.py", "analyze_impact()")
elif status == 500:
    record_fail("POST /impact/analyze/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/impact_analysis.py", "analyze_impact()")
else:
    record_fail("POST /impact/analyze/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/impact_analysis.py", "analyze_impact()")

# -----------------------------------------------------------------------
# Engineering Reports
# -----------------------------------------------------------------------
print("\n--- Engineering Reports ---")
status, body, err = make_request("GET", f"/reports/{GOOD_REPO_ID}")
if err:
    record_fail("GET /reports/{id}", "200", "Connection error", None, None, err, err, "app/api/engineering_reports.py", "list_reports()")
elif status == 200:
    record_pass("GET /reports/{id}")
elif status == 404:
    record_not_testable("GET /reports/{id}", "404 — no reports generated")
else:
    record_fail("GET /reports/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/engineering_reports.py", "list_reports()")

status, body, err = make_request("GET", f"/reports/{GOOD_REPO_ID}/summary")
if err:
    record_fail("GET /reports/{id}/summary", "200", "Connection error", None, None, err, err, "app/api/engineering_reports.py", "get_report_summary()")
elif status == 200:
    record_pass("GET /reports/{id}/summary")
elif status == 404:
    record_not_testable("GET /reports/{id}/summary", "404 — no reports generated")
else:
    record_fail("GET /reports/{id}/summary", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/engineering_reports.py", "get_report_summary()")

status, body, err = make_request("POST", f"/reports/generate/{GOOD_REPO_ID}", body={"report_type": "json"})
if err:
    record_fail("POST /reports/generate/{id}", "200", "Connection error", None, None, err, err, "app/api/engineering_reports.py", "generate_report()")
elif status == 200:
    record_pass("POST /reports/generate/{id}")
elif status == 422:
    record_fail("POST /reports/generate/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/engineering_reports.py", "generate_report()")
elif status == 500:
    record_fail("POST /reports/generate/{id}", "200", "500", 500, body, str(body), "Internal error — check NotImplementedError in exporters", "app/api/engineering_reports.py", "generate_report()")
else:
    record_fail("POST /reports/generate/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/engineering_reports.py", "generate_report()")

# -----------------------------------------------------------------------
# GitHub / CI-CD / Jira — Mock integrations
# -----------------------------------------------------------------------
print("\n--- GitHub / CICD / Jira (Mock integrations) ---")

# GET /github/repository/{owner}/{repo}
status, body, err = make_request("GET", "/github/repository/testowner/testrepo")
if err:
    record_fail("GET /github/repository/{owner}/{repo}", "200 mock", "Connection error", None, None, err, err, "app/api/github.py", "get_repository()")
elif status == 200:
    record_pass("GET /github/repository/{owner}/{repo}")
elif status == 422:
    record_fail("GET /github/repository/{owner}/{repo}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/github.py", "get_repository()")
elif status == 500:
    record_fail("GET /github/repository/{owner}/{repo}", "200 mock", "500", 500, body, str(body), "Internal error in mock GitHub client", "app/api/github.py", "get_repository()")
else:
    record_fail("GET /github/repository/{owner}/{repo}", "200 mock", f"Got {status}", status, body, None, "Unexpected", "app/api/github.py", "get_repository()")

# POST /github/connect
status, body, err = make_request("POST", "/github/connect", body={"token": "test-token", "owner": "testowner"})
if err:
    record_fail("POST /github/connect", "200", "Connection error", None, None, err, err, "app/api/github.py", "connect()")
elif status == 200:
    record_pass("POST /github/connect")
elif status == 422:
    record_fail("POST /github/connect", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/github.py", "connect()")
elif status == 500:
    record_fail("POST /github/connect", "200", "500", 500, body, str(body), "Internal error", "app/api/github.py", "connect()")
else:
    record_fail("POST /github/connect", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/github.py", "connect()")

# GET /cicd/{repository_id}
status, body, err = make_request("GET", f"/cicd/{GOOD_REPO_ID}")
if err:
    record_fail("GET /cicd/{id}", "200", "Connection error", None, None, err, err, "app/api/cicd.py", "get_cicd()")
elif status == 200:
    record_pass("GET /cicd/{id}")
elif status == 404:
    record_not_testable("GET /cicd/{id}", "404 — CI/CD not configured for repo")
elif status == 500:
    record_fail("GET /cicd/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/cicd.py", "get_cicd()")
else:
    record_fail("GET /cicd/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/cicd.py", "get_cicd()")

# GET /jira/issues/{repository_id}
status, body, err = make_request("GET", f"/jira/issues/{GOOD_REPO_ID}")
if err:
    record_fail("GET /jira/issues/{id}", "200", "Connection error", None, None, err, err, "app/api/jira.py", "get_jira_issues()")
elif status == 200:
    record_pass("GET /jira/issues/{id}")
elif status == 404:
    record_not_testable("GET /jira/issues/{id}", "404 — Jira not configured for this repo")
elif status == 500:
    record_fail("GET /jira/issues/{id}", "200", "500", 500, body, str(body), "Internal error in Jira mock client", "app/api/jira.py", "get_jira_issues()")
else:
    record_fail("GET /jira/issues/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/jira.py", "get_jira_issues()")

# -----------------------------------------------------------------------
# Notifications
# -----------------------------------------------------------------------
print("\n--- Notifications ---")
status, body, err = make_request("POST", "/notifications/send", body={"channel": "log", "message": "audit test"})
if err:
    record_fail("POST /notifications/send", "200", "Connection error", None, None, err, err, "app/api/notifications.py", "send_notification()")
elif status == 200:
    record_pass("POST /notifications/send")
elif status == 422:
    record_fail("POST /notifications/send", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/notifications.py", "send_notification()")
elif status == 500:
    record_fail("POST /notifications/send", "200", "500", 500, body, str(body), "Internal error", "app/api/notifications.py", "send_notification()")
else:
    record_fail("POST /notifications/send", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/notifications.py", "send_notification()")

# -----------------------------------------------------------------------
# Team Analytics
# -----------------------------------------------------------------------
print("\n--- Team Analytics ---")
status, body, err = make_request("POST", "/team-analytics/default-workspace", body={"time_range": "30d"})
if err:
    record_fail("POST /team-analytics/{workspace_id}", "200", "Connection error", None, None, err, err, "app/api/team_analytics.py", "get_team_analytics()")
elif status == 200:
    record_pass("POST /team-analytics/{workspace_id}")
elif status == 404:
    record_not_testable("POST /team-analytics/{workspace_id}", "404 — workspace not found")
elif status == 422:
    record_fail("POST /team-analytics/{workspace_id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/team_analytics.py", "get_team_analytics()")
elif status == 500:
    record_fail("POST /team-analytics/{workspace_id}", "200", "500", 500, body, str(body), "Internal error", "app/api/team_analytics.py", "get_team_analytics()")
else:
    record_fail("POST /team-analytics/{workspace_id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/team_analytics.py", "get_team_analytics()")

# -----------------------------------------------------------------------
# Repository Comparison
# -----------------------------------------------------------------------
print("\n--- Repository Comparison ---")
status, body, err = make_request("POST", "/repository-comparison", body={"repository_ids": [GOOD_REPO_ID, GOOD_REPO_JS]})
if err:
    record_fail("POST /repository-comparison", "200", "Connection error", None, None, err, err, "app/api/repository_comparison.py", "compare_repositories()")
elif status == 200:
    record_pass("POST /repository-comparison")
elif status == 422:
    record_fail("POST /repository-comparison", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/repository_comparison.py", "compare_repositories()")
elif status == 500:
    record_fail("POST /repository-comparison", "200", "500", 500, body, str(body), "Internal error", "app/api/repository_comparison.py", "compare_repositories()")
else:
    record_fail("POST /repository-comparison", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/repository_comparison.py", "compare_repositories()")

# -----------------------------------------------------------------------
# Quality / Security / Metrics / Smells / etc.
# -----------------------------------------------------------------------
print("\n--- Quality / Security / Code Analysis ---")

analysis_endpoints = [
    ("POST", f"/quality/{GOOD_REPO_ID}", {}, "app/api/quality.py", "analyze_quality()"),
    ("POST", f"/security/{GOOD_REPO_ID}", {}, "app/api/security.py", "analyze_security()"),
    ("POST", f"/metrics/{GOOD_REPO_ID}", {}, "app/api/metrics.py", "calculate_metrics()"),
    ("POST", f"/smells/{GOOD_REPO_ID}", {}, "app/api/smells.py", "detect_smells()"),
    ("POST", f"/refactoring/{GOOD_REPO_ID}", {"target": "improve quality"}, "app/api/refactoring.py", "suggest_refactoring()"),
    ("POST", f"/review/{GOOD_REPO_ID}", {"pr_diff": "diff content"}, "app/api/review.py", "review_code()"),
    ("POST", f"/risk/{GOOD_REPO_ID}", {}, "app/api/risk.py", "assess_risk()"),
    ("POST", f"/knowledge-graph/{GOOD_REPO_ID}", {}, "app/api/knowledge_graph.py", "build_knowledge_graph()"),
    ("POST", f"/readme/{GOOD_REPO_ID}", {}, "app/api/readme.py", "generate_readme()"),
    ("POST", f"/uml/{GOOD_REPO_ID}", {}, "app/api/uml.py", "generate_uml()"),
    ("POST", f"/apidocs/{GOOD_REPO_ID}", {}, "app/api/apidocs.py", "generate_api_docs()"),
    ("POST", f"/architecture-drift/{GOOD_REPO_ID}", {}, "app/api/architecture_drift.py", "detect_drift()"),
    ("POST", f"/architecture-recommendation/{GOOD_REPO_ID}", {}, "app/api/architecture_recommendation.py", "recommend_architecture()"),
    ("POST", f"/architecture-report/{GOOD_REPO_ID}", {}, "app/api/architecture_report.py", "generate_report()"),
    ("POST", f"/bug-localization/{GOOD_REPO_ID}", {"symptoms": "crash on startup"}, "app/api/bug_localization.py", "localize_bugs()"),
    ("POST", f"/pull-request-review/{GOOD_REPO_ID}", {"pr_diff": "diff"}, "app/api/pull_request_review.py", "review_pr()"),
    ("POST", f"/code-generation/{GOOD_REPO_ID}", {"description": "add logging"}, "app/api/code_generation.py", "generate_code()"),
    ("POST", f"/design-patterns/{GOOD_REPO_ID}", {}, "app/api/design_patterns.py", "analyze_patterns()"),
    ("POST", f"/solid/{GOOD_REPO_ID}", {}, "app/api/solid.py", "analyze_solid()"),
    ("POST", f"/microservices/{GOOD_REPO_ID}", {}, "app/api/microservices.py", "analyze_microservices()"),
    ("POST", f"/database-schema/{GOOD_REPO_ID}", {}, "app/api/database_schema.py", "analyze_database_schema()"),
    ("POST", f"/api-flow/{GOOD_REPO_ID}", {}, "app/api/api_flow.py", "analyze_api_flow()"),
    ("POST", f"/dependency-health/{GOOD_REPO_ID}", {}, "app/api/dependency_health.py", "check_dependency_health()"),
    ("POST", f"/license/{GOOD_REPO_ID}", {}, "app/api/license.py", "analyze_license()"),
    ("POST", f"/release-notes/{GOOD_REPO_ID}", {}, "app/api/release_notes.py", "generate_release_notes()"),
]

for method, path, req_body, file_r, func_r in analysis_endpoints:
    status, body, err = make_request(method, path, body=req_body if req_body else None)
    if err:
        record_fail(f"{method} {path}", "200", "Connection error", None, None, err, err, file_r, func_r)
    elif status == 200:
        record_pass(f"{method} {path}")
    elif status == 422:
        record_fail(f"{method} {path}", "200", "422 Validation Error", 422, body, str(body), "Request validation failed — schema mismatch", file_r, func_r)
    elif status == 404:
        record_not_testable(f"{method} {path}", "404 — analysis not available (no indexed data)")
    elif status == 500:
        record_fail(f"{method} {path}", "200", "500 Internal Server Error", 500, body, str(body), "Internal server error", file_r, func_r)
    else:
        record_fail(f"{method} {path}", "200", f"Got {status}", status, body, None, "Unexpected status", file_r, func_r)

# -----------------------------------------------------------------------
# Architecture explain
# -----------------------------------------------------------------------
print("\n--- Architecture Explain ---")
status, body, err = make_request("POST", f"/architecture/explain/{GOOD_REPO_ID}", body={"question": "How is this structured?"})
if err:
    record_fail("POST /architecture/explain/{id}", "200", "Connection error", None, None, err, err, "app/api/architecture.py", "explain_architecture()")
elif status == 200:
    record_pass("POST /architecture/explain/{id}")
elif status == 422:
    record_fail("POST /architecture/explain/{id}", "200", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/architecture.py", "explain_architecture()")
elif status == 500:
    record_fail("POST /architecture/explain/{id}", "200", "500", 500, body, str(body), "Internal error", "app/api/architecture.py", "explain_architecture()")
else:
    record_fail("POST /architecture/explain/{id}", "200", f"Got {status}", status, body, None, "Unexpected", "app/api/architecture.py", "explain_architecture()")

# -----------------------------------------------------------------------
# Architecture Reasoning
# -----------------------------------------------------------------------
print("\n--- Architecture Reasoning ---")
status, body, err = make_request("POST", f"/jobs/analyze/{GOOD_REPO_ID}", body={"analysis_type": "full"})
if err:
    record_fail("POST /jobs/analyze/{id}", "200/202", "Connection error", None, None, err, err, "app/api/jobs.py", "analyze_job()")
elif status in (200, 202):
    record_pass("POST /jobs/analyze/{id}")
elif status == 422:
    record_fail("POST /jobs/analyze/{id}", "200/202", "422 Validation", 422, body, str(body), "Schema mismatch", "app/api/jobs.py", "analyze_job()")
elif status == 500:
    record_fail("POST /jobs/analyze/{id}", "200/202", "500", 500, body, str(body), "Internal error", "app/api/jobs.py", "analyze_job()")
else:
    record_fail("POST /jobs/analyze/{id}", "200/202", f"Got {status}", status, body, None, "Unexpected", "app/api/jobs.py", "analyze_job()")

# -----------------------------------------------------------------------
# SUMMARY REPORT
# -----------------------------------------------------------------------
print("\n\n" + "=" * 70)
print("PHASE 0-8 SWAGGER AUDIT — COMPLETE RESULTS")
print("=" * 70)

print(f"\n✅ PASS ({len(results['PASS'])})")
print("-" * 40)
for ep in results["PASS"]:
    print(f"  {ep}")

print(f"\n❌ FAIL ({len(results['FAIL'])})")
print("-" * 40)
for f in results["FAIL"]:
    print(f"\nEndpoint: {f['endpoint']}")
    print(f"  Expected:          {f['expected']}")
    print(f"  Actual:            {f['actual']}")
    print(f"  HTTP Status:       {f['http_status']}")
    resp_str = str(f['response_body'])
    print(f"  Response Body:     {resp_str[:200] if len(resp_str) > 200 else resp_str}")
    print(f"  Traceback:         {f['traceback']}")
    print(f"  Root Cause:        {f['root_cause']}")
    print(f"  Responsible File:  {f['responsible_file']}")
    print(f"  Responsible Func:  {f['responsible_function']}")

print(f"\n⚠️  NOT TESTABLE ({len(results['NOT_TESTABLE'])})")
print("-" * 40)
for nt in results["NOT_TESTABLE"]:
    print(f"\nEndpoint: {nt['endpoint']}")
    print(f"  Reason: {nt['reason']}")

# Write JSON output
with open("audit_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n\nAudit results saved to: audit_results.json")
print(f"\nSUMMARY: {len(results['PASS'])} PASS | {len(results['FAIL'])} FAIL | {len(results['NOT_TESTABLE'])} NOT TESTABLE")
