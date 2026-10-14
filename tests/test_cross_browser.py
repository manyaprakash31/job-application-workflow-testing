"""
Cross-Browser Workflow Tests.
Executes the critical end-to-end job application workflow across Chromium, Firefox, and WebKit.
"""

import os
import pytest
from playwright.sync_api import Page, expect

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
SAMPLE_RESUME = os.path.join(FIXTURES_DIR, "sample_resume.pdf")


@pytest.mark.parametrize("browser", ["chromium", "firefox", "webkit"], indirect=True)
def test_cross_browser_full_application_workflow(page: Page, base_url: str, browser):
    """
    Execute full end-to-end application workflow in Chromium, Firefox, and WebKit:
    1. Navigate to listings page.
    2. Click Apply on a job card.
    3. Fill form and upload resume.
    4. Submit and verify confirmation.
    """
    # 1. Job Listings
    page.goto(f"{base_url}/index.html")
    expect(page.locator('[data-testid="job-card-qa-eng-101"]')).to_be_visible()

    # 2. Navigate to Details
    page.locator('[data-testid="apply-btn-qa-eng-101"]').click()
    expect(page).to_have_url(f"{base_url}/job.html?id=qa-eng-101")
    expect(page.locator('[data-testid="job-detail-title"]')).to_have_text("Senior QA Automation Engineer")

    # 3. Fill Form
    page.locator('[data-testid="input-fullname"]').fill("Marcus Vance")
    page.locator('[data-testid="input-email"]').fill("m.vance@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-678-1234")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    # 4. Submit
    page.locator('[data-testid="btn-submit"]').click()

    # 5. Verify Success
    success_banner = page.locator('[data-testid="submission-success"]')
    expect(success_banner).to_be_visible()
    expect(page.locator('[data-testid="application-id"]')).to_be_visible()
