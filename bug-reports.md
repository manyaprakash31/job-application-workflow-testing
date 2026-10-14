# Bug Reports & Defect Log

## 1. Defect Reporting Template

The following template is used for logging defects found during testing:

```markdown
### [BUG-ID] Short, descriptive bug title

- **Severity:** Critical / Major / Minor / Trivial
- **Priority:** P0 (Blocker) / P1 (High) / P2 (Medium) / P3 (Low)
- **Environment:**
  - OS: Windows 11 / macOS / Linux
  - Browser: Chromium 156.0 / Firefox 157.0 / WebKit 27.2
  - URL / Component: e.g. /job.html?id=qa-eng-101
- **Preconditions:** Initial system state before executing steps
- **Steps to Reproduce:**
  1. Go to ...
  2. Enter ...
  3. Click ...
- **Test Data Used:** Specific input values, filenames, or payloads
- **Expected Result:** What should happen based on requirements
- **Actual Result:** What actually happened (include error messages or console logs)
- **Screenshot / Evidence:** File reference or path in reports/screenshots/
- **Status:** Open / In Progress / Resolved / Verified Closed
```

---

## 2. Test Execution Findings & Defect Summary

During the execution of the 20 automated tests and exploratory testing across **Chromium**, **Firefox**, and **WebKit**, no functional defects or regressions were found in the current application build:

1. **Job Directory & Navigation:** All 4 positions display correct compensation, requirements, and location metadata. Keyword search and details navigation work without errors.
2. **Form Validation:** All required fields, whitespace-only names, single-character boundary inputs, invalid email patterns, invalid phone numbers, and unapproved file extensions are properly rejected.
3. **Duplicate Prevention:** Submitting an application with an already registered email or phone for the same position displays a warning banner and is rejected with an HTTP 409 status code. Database record verification confirms only one record exists.
4. **Error Handling:** Simulated HTTP 500 errors and network aborts display clear error feedback to the user and commit zero records to the database.

**Active Defects:** 0  
**Resolved in this Build:** Case-insensitive file extension check was verified to properly handle mixed-case extensions (`.PDF`, `.Docx`).

---

## 3. Example Defect Report (Reference)

For reference, here is an example of a defect logged during earlier exploratory testing:

### [BUG-001] File extension validation was case-sensitive for uppercase extensions

- **Severity:** Minor
- **Priority:** P2
- **Environment:** Windows 11, Chromium 156.0, `/job.html?id=qa-eng-101`
- **Preconditions:** User is on the job application form.
- **Steps to Reproduce:**
  1. Fill all valid fields (name, email, phone).
  2. Select a valid PDF file named with uppercase extension: `resume.PDF`.
  3. Click "Submit Application".
- **Test Data Used:** File named `resume.PDF`
- **Expected Result:** The file should be accepted since `.pdf` is an allowed format.
- **Actual Result:** The form displayed an error: *"Resume must be a .pdf, .docx, .doc, or .txt file"*.
- **Root Cause:** Client validation used `.endsWith()` without converting the filename to lowercase first.
- **Status:** Verified Closed (Resolved by using `fileName.toLowerCase().endsWith()`).
