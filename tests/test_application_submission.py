"""
Tests for Application Submission and Duplicate Prevention.
Verifies end-to-end submission flow, persistence of records, and strict duplicate rejection.
"""

import json
import os
import urllib.request
from playwright.sync_api import Page, expect

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
SAMPLE_RESUME = os.path.join(FIXTURES_DIR, "sample_resume.pdf")


def fetch_backend_applications(base_url: str, job_id: str = None) -> list:
    """Helper to query the backend application store directly."""
    url = f"{base_url}/api/applications"
    if job_id:
        url += f"?jobId={job_id}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("applications", [])


def test_successful_application_submission(page: Page, base_url: str):
    """
    Verify complete happy-path submission:
    Fills valid details, uploads resume, submits, verifies reference ID,
    and checks that exactly 1 backend record is created.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    # Fill form fields
    page.locator('[data-testid="input-fullname"]').fill("Alice Walker")
    page.locator('[data-testid="input-email"]').fill("alice.walker@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-234-5678")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)
    page.locator('[data-testid="input-portfolio"]').fill("https://github.com/alicewalker-qa")
    page.locator('[data-testid="input-covernote"]').fill("Experienced QA engineer passionate about test automation.")

    # Submit
    page.locator('[data-testid="btn-submit"]').click()

    # Verify success banner
    success_banner = page.locator('[data-testid="submission-success"]')
    expect(success_banner).to_be_visible()
    expect(page.locator('#success-message-text')).to_contain_text("submitted successfully")

    # Verify reference ID is present and formatted
    app_id_el = page.locator('[data-testid="application-id"]')
    expect(app_id_el).to_be_visible()
    ref_id = app_id_el.inner_text()
    assert ref_id.startswith("APP-"), f"Unexpected ID format: {ref_id}"

    # Verify backend persistence: exactly 1 record created with matching data
    records = fetch_backend_applications(base_url, job_id="qa-eng-101")
    assert len(records) == 1, f"Expected 1 record in database, found {len(records)}"
    record = records[0]
    assert record["fullName"] == "Alice Walker"
    assert record["email"] == "alice.walker@example.com"
    assert record["phone"] == "+1 555-234-5678"
    assert record["resumeFileName"] == "sample_resume.pdf"
    assert record["id"] == ref_id


def test_duplicate_submission_prevented(page: Page, base_url: str):
    """
    Verify duplicate submission prevention:
    1. Submit valid application for a position.
    2. Attempt a second submission for the same position with the same candidate email.
    3. Verify duplicate warning alert is rendered.
    4. Query backend store to confirm only 1 application record was stored.
    """
    job_id = "qa-eng-101"
    candidate_email = "b.miller@example.com"

    page.goto(f"{base_url}/job.html?id={job_id}")

    # First submission
    page.locator('[data-testid="input-fullname"]').fill("Bob Miller")
    page.locator('[data-testid="input-email"]').fill(candidate_email)
    page.locator('[data-testid="input-phone"]').fill("+1 555-888-9999")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)
    page.locator('[data-testid="btn-submit"]').click()

    # Verify first submission succeeded
    expect(page.locator('[data-testid="submission-success"]')).to_be_visible()

    records_after_first = fetch_backend_applications(base_url, job_id=job_id)
    assert len(records_after_first) == 1, "Initial application was not saved."

    # Attempt second submission with same email
    page.locator('[data-testid="input-fullname"]').fill("Bob Miller")
    page.locator('[data-testid="input-email"]').fill(candidate_email)
    page.locator('[data-testid="input-phone"]').fill("+1 555-888-9999")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)
    page.locator('[data-testid="btn-submit"]').click()

    # Verify duplicate warning banner is displayed
    error_alert = page.locator('[data-testid="submission-error"]')
    expect(error_alert).to_be_visible()
    expect(page.locator('#error-heading')).to_contain_text("Duplicate Submission Detected")
    expect(page.locator('#error-message-text')).to_contain_text("already been submitted")

    # Confirm database only contains 1 record
    records_after_second = fetch_backend_applications(base_url, job_id=job_id)
    assert len(records_after_second) == 1, (
        f"Expected exactly 1 record in database, but found {len(records_after_second)}"
    )


def test_page_refresh_after_submission(page: Page, base_url: str):
    """
    Verify reloading the page after submission resets the form cleanly
    and does not trigger unintended re-submissions.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    # Submit application
    page.locator('[data-testid="input-fullname"]').fill("Charlie Green")
    page.locator('[data-testid="input-email"]').fill("charlie.green@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-444-3333")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)
    page.locator('[data-testid="btn-submit"]').click()

    expect(page.locator('[data-testid="submission-success"]')).to_be_visible()

    # Refresh the browser
    page.reload()

    # Verify form is clean and success alert is no longer displayed
    expect(page.locator('[data-testid="submission-success"]')).not_to_be_visible()
    expect(page.locator('[data-testid="input-fullname"]')).to_have_value("")
    expect(page.locator('[data-testid="input-email"]')).to_have_value("")

    # Verify exactly 1 record remains in DB
    records = fetch_backend_applications(base_url, job_id="qa-eng-101")
    assert len(records) == 1
