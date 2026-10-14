"""
Tests for Job Details Navigation and Routing.
Verifies that clicking Apply opens the correct job details and back-navigation works.
"""

from playwright.sync_api import Page, expect


def test_job_link_opens_correct_details(page: Page, base_url: str):
    """
    Verify clicking 'Apply Now' on a job card navigates to the details page
    with matching job details, requirements, and application form.
    """
    page.goto(f"{base_url}/index.html")

    # Click Apply for Full Stack Software Engineer (fullstack-102)
    apply_btn = page.locator('[data-testid="apply-btn-fullstack-102"]')
    expect(apply_btn).to_be_visible()
    apply_btn.click()

    # Verify URL updated correctly
    expect(page).to_have_url(f"{base_url}/job.html?id=fullstack-102")

    # Verify details page contents
    expect(page.locator('[data-testid="job-detail-title"]')).to_have_text("Full Stack Software Engineer")
    expect(page.locator('[data-testid="job-detail-department"]')).to_have_text("Core Platform")
    expect(page.locator('[data-testid="job-detail-salary"]')).to_have_text("$140,000 - $175,000 / year")
    expect(page.locator('[data-testid="job-detail-experience"]')).to_have_text("3+ years")
    expect(page.locator('[data-testid="job-detail-requirements"] li')).to_have_count(3)

    # Verify hidden job ID in form is populated
    expect(page.locator('#jobId')).to_have_value("fullstack-102")


def test_back_to_listings_navigation(page: Page, base_url: str):
    """
    Verify that clicking 'Back to all job openings' returns to the main job listings page.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    back_link = page.locator('[data-testid="back-to-jobs"]')
    expect(back_link).to_be_visible()
    back_link.click()

    expect(page).to_have_url(f"{base_url}/index.html")
    expect(page.locator('[data-testid="jobs-grid"]')).to_be_visible()


def test_invalid_job_id_navigation(page: Page, base_url: str):
    """
    Verify navigating to job.html with an invalid/non-existent job ID shows a clean error state.
    """
    page.goto(f"{base_url}/job.html?id=non-existent-job-999")

    expect(page.locator('[data-testid="job-detail-title"]')).to_have_text("Position Not Found")
    expect(page.locator('[data-testid="application-form"]')).not_to_be_visible()
