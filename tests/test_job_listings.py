"""
Tests for Job Listing Accuracy and Display.
Verifies that all job positions are loaded from the backend with accurate details.
"""

from playwright.sync_api import Page, expect


def test_job_listings_display_correctly(page: Page, base_url: str):
    """
    Verify that the job listings page renders all positions with title,
    salary, experience, location, department, and description.
    """
    page.goto(f"{base_url}/index.html")

    # Assert page title and logo
    expect(page).to_have_title("Career Portal - Open Positions")
    expect(page.locator('[data-testid="portal-logo"]')).to_be_visible()

    # Wait for positions grid to load
    job_cards = page.locator('[data-testid^="job-card-"]')
    expect(job_cards).to_have_count(4)

    # Verify first job: Senior QA Automation Engineer
    qa_card = page.locator('[data-testid="job-card-qa-eng-101"]')
    expect(qa_card).to_be_visible()
    expect(qa_card.locator('[data-testid="job-title"]')).to_have_text("Senior QA Automation Engineer")
    expect(qa_card.locator('[data-testid="job-salary"]')).to_have_text("$130,000 - $160,000 / year")
    expect(qa_card.locator('[data-testid="job-experience"]')).to_have_text("5+ years")
    expect(qa_card.locator('[data-testid="job-location"]')).to_have_text("Remote / New York, NY")
    expect(qa_card.locator('[data-testid="job-department"]')).to_have_text("Quality Engineering")
    expect(qa_card.locator('[data-testid="apply-btn-qa-eng-101"]')).to_be_visible()

    # Verify open positions counter
    expect(page.locator('[data-testid="jobs-count"]')).to_have_text("4 open positions")


def test_job_search_filter(page: Page, base_url: str):
    """
    Verify that typing keywords into the search input dynamically filters the job listings.
    """
    page.goto(f"{base_url}/index.html")

    search_input = page.locator('[data-testid="search-input"]')
    expect(search_input).to_be_visible()

    # Search for QA
    search_input.fill("QA")
    job_cards = page.locator('[data-testid^="job-card-"]')
    expect(job_cards).to_have_count(1)
    expect(page.locator('[data-testid="job-card-qa-eng-101"]')).to_be_visible()

    # Clear and search for non-matching term
    search_input.fill("NonExistentRoleXYZ")
    expect(page.locator('[data-testid="no-jobs-found"]')).to_be_visible()
    expect(page.locator('[data-testid="jobs-count"]')).to_have_text("0 open positions")
