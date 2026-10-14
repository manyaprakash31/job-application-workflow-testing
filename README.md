# Job Application Portal - Test Automation Project

This repository contains an automated end-to-end test suite and a local mock application built to test a candidate job application workflow. 

Candidates can browse open positions, filter by keyword, view role requirements, and submit applications with attached resumes. The test suite covers functional requirements, form validation, duplicate submission prevention, network failure handling, server error recovery, and cross-browser execution.

---

## Tech Stack
- **Test Automation:** Python, Playwright, pytest
- **Reporting:** pytest-html
- **Mock Application:** Python (`http.server`), HTML5, CSS3, JavaScript

---

## Project Structure
```text
D:\job-application-workflow-testing/
├── app/
│   ├── index.html            # Job listings directory page
│   ├── job.html              # Job details and application submission form
│   ├── style.css             # Application styles and alert banners
│   ├── app.js                # Frontend rendering, validation, and submission logic
│   └── server.py             # Mock backend REST API and static file server
├── tests/
│   ├── conftest.py           # Pytest fixtures, server lifecycle, browser context setup
│   ├── test_job_listings.py  # Listing accuracy and search filter tests
│   ├── test_job_navigation.py# Details routing, breadcrumbs, and error handling
│   ├── test_form_validation.py# Input validation (required, bounds, email, file types)
│   ├── test_application_submission.py # Submission flow & duplicate prevention
│   ├── test_error_handling.py# HTTP 500 error, network disconnect, and slow responses
│   ├── test_cross_browser.py # Cross-browser test suite (Chromium, Firefox, WebKit)
│   └── fixtures/             # Test files (sample resume PDF, invalid file)
├── reports/
│   └── report.html           # Generated test execution report
├── test-plan.md              # Test plan and strategy documentation
├── test-cases.csv            # Detailed test cases with execution status
├── bug-reports.md            # Defect reporting template and QA status
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
├── SUBMISSION_NOTES.md       # Demo walkthrough notes and trade-off explanations
└── README.md
```

---

## Setup & Installation

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.12)
- Windows / macOS / Linux

### 2. Environment Setup
```powershell
# Navigate to project folder
cd D:\job-application-workflow-testing

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# (Optional) If creating a new virtual environment:
# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# playwright install chromium firefox webkit
```

---

## Running the Mock Application (Manual Testing)
To explore the application manually in your browser:

```powershell
python app/server.py 8000
```
Then open: **http://127.0.0.1:8000**

- Browse available positions and use the search bar to filter.
- Click **Apply Now** to open the application form.
- The form includes checkboxes at the bottom to simulate **HTTP 500 errors** or **3-second network delays** on demand.
- You can access the generated test report directly from the top navigation bar (**QA Test Report**).

---

## Running Automated Tests

### Run All Tests & Generate HTML Report
```powershell
pytest -v --html=reports/report.html --self-contained-html
```

### Run Tests in a Specific Browser
The suite runs against **Chromium** by default. Use `--browser-name` to select a specific browser:
```powershell
# Chromium
pytest -v --browser-name=chromium

# Firefox
pytest -v --browser-name=firefox

# WebKit (Safari engine)
pytest -v --browser-name=webkit
```

### Run Tests in Headed Mode
To watch the browser window during test execution:
```powershell
pytest -v --headed
```

### Run Specific Test Modules
```powershell
# Form validation tests
pytest -v tests/test_form_validation.py

# Submission and duplicate prevention
pytest -v tests/test_application_submission.py

# Error handling and network failure
pytest -v tests/test_error_handling.py

# Cross-browser tests
pytest -v tests/test_cross_browser.py
```

---

## Viewing the Test Report
After running the tests, view the report in any browser:
- Open the local file: `file:///D:/job-application-workflow-testing/reports/report.html`
- Or via PowerShell:
  ```powershell
  Start-Process reports\report.html
  ```
- Or if the app server is running: `http://127.0.0.1:8000/reports/report.html`

---

## Test Execution Summary

The automated suite consists of 20 tests:

| Module | Scope | Tests | Result |
| :--- | :--- | :---: | :---: |
| `test_job_listings.py` | Position listings accuracy, compensation, dynamic filtering | 2 | Passed |
| `test_job_navigation.py` | Details page routing, back navigation, invalid job IDs | 3 | Passed |
| `test_form_validation.py` | Required fields, whitespace names, boundary lengths, email, phone, file extension | 6 | Passed |
| `test_application_submission.py` | Happy path, reference ID generation, duplicate prevention, page refresh | 3 | Passed |
| `test_error_handling.py` | HTTP 500 error handling, network failure (route abort), slow response state | 3 | Passed |
| `test_cross_browser.py` | Workflow execution in Chromium, Firefox, and WebKit | 3 | Passed |
| **Total** | | **20** | **20 Passed (100%)** |

### Duplicate Submission Testing
In `test_duplicate_submission_prevented`:
1. An initial application is submitted and confirmed.
2. A duplicate application with the same email is submitted for the same position.
3. The UI asserts that the duplicate warning banner is shown.
4. The test queries the backend API (`/api/applications`) directly to verify that **only one record was created in the database**.

---

## Assumptions & Limitations
- **In-Memory Storage:** The mock backend stores applications in memory. An `autouse` fixture calls `/api/reset` before each test to guarantee complete test isolation.
- **Resume Validation:** Resumes are validated on the client and server by file extension (`.pdf`, `.docx`, `.doc`, `.txt`) and presence. Binary parsing and OCR are out of scope.
- **Email Notifications:** Submission confirmations and reference IDs are rendered on-screen and returned by the API; no external SMTP service is integrated.
