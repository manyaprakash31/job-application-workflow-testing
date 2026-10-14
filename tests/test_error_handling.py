"""
Tests for Error Handling, Network Failures, Slow Responses, and Resilience.
Verifies error messaging and ensures failed requests never create records in the database.
"""

import json
import os
import urllib.request
from playwright.sync_api import Page, expect

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
SAMPLE_RESUME = os.path.join(FIXTURES_DIR, "sample_resume.pdf")


def fetch_backend_applications(base_url: str) -> list:
    """Helper to query all applications currently in backend."""
    with urllib.request.urlopen(f"{base_url}/api/applications") as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("applications", [])


def test_server_error_500_handling(page: Page, base_url: str):
    """
    Verify that when the backend returns a 500 Internal Server Error:
    1. The UI displays an error alert with appropriate error guidance.
    2. Zero records are created in the backend application database.
    3. The submit button is re-enabled so the candidate can retry.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    # Fill form
    page.locator('[data-testid="input-fullname"]').fill("Devon Smith")
    page.locator('[data-testid="input-email"]').fill("devon.smith@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-777-8888")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    # Enable 500 error simulation via QA checkbox
    page.locator('[data-testid="simulate-error-checkbox"]').check()

    # Submit
    page.locator('[data-testid="btn-submit"]').click()

    # Verify error alert banner is visible
    error_banner = page.locator('[data-testid="submission-error"]')
    expect(error_banner).to_be_visible()
    expect(page.locator('#error-heading')).to_contain_text("Server Error (500)")
    expect(page.locator('#error-message-text')).to_contain_text("The application server failed to process the submission")

    # Verify submit button is re-enabled for retry
    expect(page.locator('[data-testid="btn-submit"]')).to_be_enabled()

    # Verify zero records were created in the database
    records = fetch_backend_applications(base_url)
    assert len(records) == 0, f"Expected 0 records on 500 error, found {len(records)}"


def test_network_failure_handling(page: Page, base_url: str):
    """
    Verify that when a client-side network disconnect / failure occurs during request:
    1. Playwright intercepts and aborts the network call.
    2. The UI catches the network error and displays a clear network error message.
    3. Zero application records are created.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    # Intercept and abort API call to simulate network loss
    page.route("**/api/applications", lambda route: route.abort("failed"))

    # Fill valid form
    page.locator('[data-testid="input-fullname"]').fill("Elena Rostova")
    page.locator('[data-testid="input-email"]').fill("elena.rostova@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-333-2222")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    page.locator('[data-testid="btn-submit"]').click()

    # Verify network error message displayed
    error_banner = page.locator('[data-testid="submission-error"]')
    expect(error_banner).to_be_visible()
    expect(page.locator('#error-heading')).to_contain_text("Network Error")
    expect(page.locator('#error-message-text')).to_contain_text("Unable to connect to the server")

    # Verify submit button is re-enabled
    expect(page.locator('[data-testid="btn-submit"]')).to_be_enabled()

    # Verify zero records saved
    records = fetch_backend_applications(base_url)
    assert len(records) == 0


def test_slow_response_and_in_flight_button_state(page: Page, base_url: str):
    """
    Verify behavior under slow network response:
    1. During submission flight, button is disabled and text indicates in-progress state.
    2. Once request finishes, success banner appears and record is created.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    page.locator('[data-testid="input-fullname"]').fill("Fiona Gallagher")
    page.locator('[data-testid="input-email"]').fill("fiona.g@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-999-1111")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    # Enable 3-second delay simulation
    page.locator('[data-testid="simulate-delay-checkbox"]').check()

    # Click submit
    submit_btn = page.locator('[data-testid="btn-submit"]')
    submit_btn.click()

    # Verify button immediately becomes disabled with loading text
    expect(submit_btn).to_be_disabled()
    expect(submit_btn).to_have_text("Submitting application...")

    # Wait for completion (timeout 8s to accommodate 3s delay)
    success_banner = page.locator('[data-testid="submission-success"]')
    expect(success_banner).to_be_visible(timeout=8000)

    # Verify record created
    records = fetch_backend_applications(base_url)
    assert len(records) == 1
    assert records[0]["fullName"] == "Fiona Gallagher"
