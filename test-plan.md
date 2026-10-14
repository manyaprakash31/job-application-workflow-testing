# Test Plan: Job Application Workflow Testing

## 1. Overview & Objectives
This test plan defines the testing strategy for the Job Application Workflow. The application allows candidates to browse open jobs, view position details and compensation, and apply by submitting their contact information and resume.

The goals of this testing effort are to verify:
- Accurate presentation of job listings, compensation, and qualifications.
- Proper input validation on all application fields (client-side and server-side).
- Strict duplicate submission prevention (verifying UI feedback and database record counts).
- System resilience during network failures, server errors (HTTP 500), and slow network responses.
- Consistent functionality across modern browsers (Chromium, Firefox, WebKit).

---

## 2. Scope

### In Scope
- **Job Listings:** Card rendering (title, department, location, salary range, experience, description), keyword search, and open positions count.
- **Job Details & Navigation:** Routing to `/job.html?id=<id>`, displaying full descriptions and qualification lists, back-navigation to the directory, and handling non-existent job IDs.
- **Application Submission:** Form fields (name, email, phone, resume upload, portfolio URL, cover note), required-field enforcement, email regex validation, phone format validation, and allowed resume extensions (`.pdf`, `.docx`, `.doc`, `.txt`).
- **Data Integrity & Duplicate Detection:** Rejecting duplicate applications for the same job matching an existing email or phone number; ensuring only a single record is persisted.
- **Error Handling:** Client feedback and database isolation during HTTP 500 server errors, network dropouts, and in-flight loading states.
- **Cross-Browser Verification:** Running the automated workflow tests across Chromium, Firefox, and WebKit.

### Out of Scope
- User account creation, candidate login, and password management.
- Recruiter administration panels and applicant tracking system (ATS) candidate workflows.
- Live email delivery via SMTP.
- Performance load testing beyond latency simulation.

---

## 3. Test Approach & Setup

### Approach
- **End-to-End UI Automation:** Built with **Playwright** and **pytest** using explicit `data-testid` selectors to avoid brittle locator strategies.
- **Backend API Checks:** Tests make direct HTTP requests to `/api/applications` to verify that database state matches user actions (e.g. verifying that duplicate attempts or server errors create zero extra records).
- **Test Isolation:** A pytest fixture resets application data via `POST /api/reset` before every test run.
- **Fault Simulation:** Edge cases like network aborts are simulated using Playwright's `route.abort('failed')` API, while server errors and delays are triggered via backend simulation parameters.

### Test Environment
- **OS:** Windows 11 / cross-platform compatible
- **Python:** 3.12
- **Tools:** pytest 9.1.1, Playwright 1.64.0, pytest-html 4.2.0
- **Browsers:** Chromium (Headless Shell 156.0), Firefox (157.0), WebKit (27.2)
- **Application Host:** Localhost (`127.0.0.1:8000`)

---

## 4. Entry & Exit Criteria

### Entry Criteria
1. Application server and frontend assets are runnable locally.
2. Python virtual environment is set up with Playwright browser binaries installed.
3. Test fixtures (sample resume PDF, invalid binary test file) are in place.

### Exit Criteria
1. 100% pass rate on all automated test suites.
2. Duplicate submission prevention confirmed at both the UI and database store level.
3. Resilience tests confirm zero orphaned records during network or server failures.
4. Cross-browser suite passes across Chromium, Firefox, and WebKit.
5. All documented test cases in `test-cases.csv` are executed with actual results recorded.
6. HTML test execution report is generated.

---

## 5. Risk Assessment & Mitigations

| Risk | Likelihood | Impact | Mitigation |
| :--- | :---: | :---: | :--- |
| **Duplicate submissions via rapid double clicks** | Medium | High | UI disables the submit button immediately upon click; backend rejects duplicate email/job combinations with HTTP 409 Conflict. |
| **Flaky assertions due to async DOM rendering** | Medium | Medium | Used Playwright's auto-waiting `expect(locator)` assertions instead of static sleep delays. |
| **Test data pollution across consecutive runs** | High | High | Implemented an autouse fixture calling `POST /api/reset` before every test case. |
| **Candidate data loss on server failure** | Low | Medium | Form inputs remain populated when errors occur so candidates can retry without re-typing. |
| **Cross-browser rendering differences** | Low | Medium | Executed end-to-end tests across Chromium, Firefox, and WebKit. |

---

## 6. Priorities & Justification

- **P0 (Critical):** Application submission happy path, duplicate submission prevention, and required-field validation. Failure here blocks the core hiring workflow.
- **P1 (High):** Job listings accuracy, details routing, email formatting, phone validation, and server/network error handling.
- **P2 (Medium):** Keyword search filter, allowed file extension enforcement, in-flight button disabling, and page refresh state.
- **P3 (Low):** Optional field validations (portfolio URL syntax, cover note length).

---

## 7. Browser Compatibility Strategy
- **Chromium:** Default browser for full regression runs (covers Chrome, Edge, Brave).
- **Firefox:** Covers Gecko rendering engine.
- **WebKit:** Covers Safari rendering engine on desktop and mobile.
- Tests can be targeted by browser via `--browser-name [chromium|firefox|webkit]`. A dedicated cross-browser test file (`test_cross_browser.py`) automatically runs across all three browsers via pytest parametrization.

---

## 8. Assumptions & Limitations
- The mock server uses an in-memory data store for clean portability without database dependencies.
- Resume files are validated by extension and upload presence.
- Email delivery is simulated via UI reference ID generation.
