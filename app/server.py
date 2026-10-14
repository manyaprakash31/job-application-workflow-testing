"""
Mock Job Application Portal Backend Server
Provides REST API endpoints and static file serving for testing.
"""

import json
import os
import re
import sys
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# Default port
PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initial mock job listings
INITIAL_JOBS = [
    {
        "id": "qa-eng-101",
        "title": "Senior QA Automation Engineer",
        "department": "Quality Engineering",
        "location": "Remote / New York, NY",
        "salary": "$130,000 - $160,000 / year",
        "experience": "5+ years",
        "description": "Lead our automation testing strategy, design scalable Playwright test frameworks, and ensure high test coverage across web workflows.",
        "requirements": [
            "5+ years of experience in test automation using Python and Playwright/Selenium",
            "Strong understanding of CI/CD pipeline integration and HTML test reporting",
            "Experience testing complex frontend workflows and REST APIs",
            "Familiarity with cross-browser compatibility and responsive UI testing"
        ]
    },
    {
        "id": "fullstack-102",
        "title": "Full Stack Software Engineer",
        "department": "Core Platform",
        "location": "San Francisco, CA (Hybrid)",
        "salary": "$140,000 - $175,000 / year",
        "experience": "3+ years",
        "description": "Build high-throughput web applications with modern frontend and backend frameworks, architecting scalable features for global users.",
        "requirements": [
            "3+ years of experience with Python, TypeScript, and modern web frameworks",
            "Proficient in relational database schema design and RESTful APIs",
            "Commitment to clean architecture, automated testing, and code quality"
        ]
    },
    {
        "id": "devops-103",
        "title": "DevOps / Infrastructure Engineer",
        "department": "Cloud Infrastructure",
        "location": "Austin, TX (On-site)",
        "salary": "$135,000 - $165,000 / year",
        "experience": "4+ years",
        "description": "Manage infrastructure reliability, automate container deployments, and implement robust observability and security standards.",
        "requirements": [
            "4+ years configuring containerized workloads using Docker and Kubernetes",
            "Hands-on experience with Terraform, Cloud orchestration, and GitHub Actions",
            "Strong scripting skills in Python and Bash"
        ]
    },
    {
        "id": "uiux-104",
        "title": "Product Designer (UI/UX)",
        "department": "Design Systems",
        "location": "Remote (US/Canada)",
        "salary": "$110,000 - $135,000 / year",
        "experience": "3+ years",
        "description": "Create intuitive, accessible user interfaces and design systems for enterprise workflows and candidate portals.",
        "requirements": [
            "3+ years designing web application flows and high-fidelity prototypes in Figma",
            "Solid grasp of WCAG 2.1 accessibility guidelines and responsive design",
            "Experience collaborating closely with QA and Frontend engineering teams"
        ]
    }
]

# Thread-safe in-memory storage for applications
applications_db = []


class JobPortalHandler(SimpleHTTPRequestHandler):
    """Custom request handler serving static files and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_json_response(self, status_code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Simulate-Error, X-Simulate-Delay")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """Handle CORS preflight options."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Simulate-Error, X-Simulate-Delay")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # API: Get all jobs
        if path == "/api/jobs":
            self._send_json_response(200, {"jobs": INITIAL_JOBS})
            return

        # API: Get specific job details
        if path.startswith("/api/jobs/"):
            job_id = path.replace("/api/jobs/", "").strip()
            job = next((j for j in INITIAL_JOBS if j["id"] == job_id), None)
            if job:
                self._send_json_response(200, {"job": job})
            else:
                self._send_json_response(404, {"error": f"Job with ID '{job_id}' not found."})
            return

        # API: Get submitted applications (for verification in tests)
        if path == "/api/applications":
            job_id = query.get("jobId", [None])[0]
            if job_id:
                filtered = [a for a in applications_db if a.get("jobId") == job_id]
                self._send_json_response(200, {"applications": filtered, "count": len(filtered)})
            else:
                self._send_json_response(200, {"applications": applications_db, "count": len(applications_db)})
            return

        # API: Health Check
        if path == "/api/health":
            self._send_json_response(200, {
                "status": "healthy",
                "jobs_count": len(INITIAL_JOBS),
                "applications_count": len(applications_db)
            })
            return

        # Serve files from the reports directory
        if path.startswith("/reports/"):
            rel_file = path.replace("/reports/", "").strip()
            reports_dir = os.path.join(os.path.dirname(BASE_DIR), "reports")
            file_path = os.path.join(reports_dir, rel_file)
            if os.path.isfile(file_path):
                self.send_response(200)
                content_type = "text/html; charset=utf-8" if file_path.endswith(".html") else "application/octet-stream"
                self.send_header("Content-Type", content_type)
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self._send_json_response(404, {"error": f"Report file '{rel_file}' not found."})
                return

        # Serve static HTML/CSS/JS files
        if path == "/" or path == "":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # API: Reset applications DB (for test isolation)
        if path == "/api/reset":
            global applications_db
            applications_db.clear()
            self._send_json_response(200, {
                "message": "Application database has been reset.",
                "applications_count": 0
            })
            return

        # API: Submit job application
        if path == "/api/applications":
            # Check for simulated error via header or query param
            simulate_error = self.headers.get("X-Simulate-Error") or query.get("simulate_error", [None])[0]
            if simulate_error:
                try:
                    err_code = int(simulate_error)
                except ValueError:
                    err_code = 500
                self._send_json_response(err_code, {
                    "error": f"Simulated server error {err_code}: The application server failed to process the submission."
                })
                return

            # Check for simulated delay via header or query param
            simulate_delay = self.headers.get("X-Simulate-Delay") or query.get("simulate_delay", [None])[0]
            if simulate_delay:
                try:
                    delay_secs = float(simulate_delay)
                    time.sleep(delay_secs)
                except ValueError:
                    pass

            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json_response(400, {"error": "Missing application payload."})
                return

            try:
                body_raw = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body_raw)
            except Exception as e:
                self._send_json_response(400, {"error": f"Invalid JSON payload: {str(e)}"})
                return

            # Extract fields
            job_id = str(payload.get("jobId", "")).strip()
            full_name = str(payload.get("fullName", "")).strip()
            email = str(payload.get("email", "")).strip()
            phone = str(payload.get("phone", "")).strip()
            resume_name = str(payload.get("resumeFileName", "")).strip()
            cover_note = str(payload.get("coverNote", "")).strip()
            portfolio_url = str(payload.get("portfolioUrl", "")).strip()

            # Server-side validation
            errors = {}

            # Job validation
            job = next((j for j in INITIAL_JOBS if j["id"] == job_id), None)
            if not job:
                errors["jobId"] = f"Invalid Job ID '{job_id}'."

            # Name validation (required, 2-100 chars, cannot be pure whitespace)
            if not full_name:
                errors["fullName"] = "Full name is required."
            elif len(full_name) < 2 or len(full_name) > 100:
                errors["fullName"] = "Full name must be between 2 and 100 characters."

            # Email validation (required, standard email pattern)
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not email:
                errors["email"] = "Email address is required."
            elif not re.match(email_pattern, email):
                errors["email"] = "Please enter a valid email address (e.g. user@example.com)."

            # Phone validation (required, 10-20 chars digits/symbols)
            phone_pattern = r"^\+?[\d\s\-\(\)]{10,20}$"
            if not phone:
                errors["phone"] = "Phone number is required."
            elif not re.match(phone_pattern, phone):
                errors["phone"] = "Please enter a valid phone number (at least 10 digits)."

            # Resume validation (required, must have allowed extension)
            allowed_extensions = (".pdf", ".docx", ".doc", ".txt")
            if not resume_name:
                errors["resume"] = "Resume upload is required."
            elif not any(resume_name.lower().endswith(ext) for ext in allowed_extensions):
                errors["resume"] = "Resume must be a .pdf, .docx, .doc, or .txt file."

            # If validation errors exist, reject submission
            if errors:
                self._send_json_response(422, {
                    "error": "Validation failed",
                    "details": errors
                })
                return

            # Duplicate submission prevention check:
            # Check if an application already exists for this job with the same email or phone number
            is_duplicate = any(
                app["jobId"] == job_id and (
                    app["email"].lower() == email.lower() or app["phone"] == phone
                )
                for app in applications_db
            )

            if is_duplicate:
                self._send_json_response(409, {
                    "error": "Duplicate submission detected",
                    "message": "An application for this position has already been submitted with this email address or phone number."
                })
                return

            # Create new application record
            app_id = f"APP-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            record = {
                "id": app_id,
                "jobId": job_id,
                "jobTitle": job["title"],
                "fullName": full_name,
                "email": email,
                "phone": phone,
                "resumeFileName": resume_name,
                "coverNote": cover_note,
                "portfolioUrl": portfolio_url,
                "submittedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

            applications_db.append(record)

            self._send_json_response(201, {
                "success": True,
                "applicationId": app_id,
                "message": f"Application submitted successfully! Your reference ID is {app_id}.",
                "application": record
            })
            return

        self._send_json_response(404, {"error": "Endpoint not found."})


def run_server(port=PORT):
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, JobPortalHandler)
    print(f"[*] Job Application Portal running on http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
