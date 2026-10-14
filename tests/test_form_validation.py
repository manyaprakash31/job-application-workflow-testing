"""
Tests for Application Form Field Validation.
Verifies client-side validation rules for required fields, formatting, and boundaries.
"""

import os
from playwright.sync_api import Page, expect

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
SAMPLE_RESUME = os.path.join(FIXTURES_DIR, "sample_resume.pdf")
INVALID_FILE = os.path.join(FIXTURES_DIR, "invalid_file.exe")


def test_empty_required_fields_validation(page: Page, base_url: str):
    """
    Verify submitting an empty form triggers validation error messages on all required fields:
    Full Name, Email Address, Phone Number, and Resume Upload.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    # Click Submit with all fields empty
    submit_btn = page.locator('[data-testid="btn-submit"]')
    submit_btn.click()

    # Verify field error messages are visible with accurate text
    name_error = page.locator('[data-testid="error-fullname"]')
    expect(name_error).to_be_visible()
    expect(name_error).to_contain_text("Full name is required")

    email_error = page.locator('[data-testid="error-email"]')
    expect(email_error).to_be_visible()
    expect(email_error).to_contain_text("Email address is required")

    phone_error = page.locator('[data-testid="error-phone"]')
    expect(phone_error).to_be_visible()
    expect(phone_error).to_contain_text("Phone number is required")

    resume_error = page.locator('[data-testid="error-resume"]')
    expect(resume_error).to_be_visible()
    expect(resume_error).to_contain_text("Resume file upload is required")

    # Verify input elements have error CSS class
    expect(page.locator('[data-testid="input-fullname"]')).to_have_class("form-control input-error")
    expect(page.locator('[data-testid="input-email"]')).to_have_class("form-control input-error")

    # Verify success banner is not shown
    expect(page.locator('[data-testid="submission-success"]')).not_to_be_visible()


def test_whitespace_only_name_rejected(page: Page, base_url: str):
    """
    Verify entering only whitespace characters in Full Name is rejected as empty.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    page.locator('[data-testid="input-fullname"]').fill("     ")
    page.locator('[data-testid="input-email"]').fill("jane.doe@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-019-2834")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    page.locator('[data-testid="btn-submit"]').click()

    name_error = page.locator('[data-testid="error-fullname"]')
    expect(name_error).to_be_visible()
    expect(name_error).to_contain_text("Full name is required")


def test_name_minimum_length_boundary(page: Page, base_url: str):
    """
    Verify entering a single character in Full Name violates the minimum 2-character requirement.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    page.locator('[data-testid="input-fullname"]').fill("J")
    page.locator('[data-testid="input-email"]').fill("jane.doe@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-019-2834")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    page.locator('[data-testid="btn-submit"]').click()

    name_error = page.locator('[data-testid="error-fullname"]')
    expect(name_error).to_be_visible()
    expect(name_error).to_contain_text("Full name must be between 2 and 100 characters")


def test_invalid_email_format_rejected(page: Page, base_url: str):
    """
    Verify entering an invalid email format (e.g. missing @ or domain) displays an error.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    page.locator('[data-testid="input-fullname"]').fill("Jane Doe")
    page.locator('[data-testid="input-email"]').fill("not-a-valid-email")
    page.locator('[data-testid="input-phone"]').fill("+1 555-019-2834")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    page.locator('[data-testid="btn-submit"]').click()

    email_error = page.locator('[data-testid="error-email"]')
    expect(email_error).to_be_visible()
    expect(email_error).to_contain_text("Please enter a valid email address")


def test_invalid_phone_number_rejected(page: Page, base_url: str):
    """
    Verify entering an incomplete phone number (under 10 digits) is rejected.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    page.locator('[data-testid="input-fullname"]').fill("Jane Doe")
    page.locator('[data-testid="input-email"]').fill("jane.doe@example.com")
    page.locator('[data-testid="input-phone"]').fill("12345")
    page.locator('[data-testid="input-resume"]').set_input_files(SAMPLE_RESUME)

    page.locator('[data-testid="btn-submit"]').click()

    phone_error = page.locator('[data-testid="error-phone"]')
    expect(phone_error).to_be_visible()
    expect(phone_error).to_contain_text("Please enter a valid phone number")


def test_invalid_resume_file_extension_rejected(page: Page, base_url: str):
    """
    Verify uploading a file with an unapproved extension (.exe) is rejected by validation.
    """
    page.goto(f"{base_url}/job.html?id=qa-eng-101")

    page.locator('[data-testid="input-fullname"]').fill("Jane Doe")
    page.locator('[data-testid="input-email"]').fill("jane.doe@example.com")
    page.locator('[data-testid="input-phone"]').fill("+1 555-019-2834")
    page.locator('[data-testid="input-resume"]').set_input_files(INVALID_FILE)

    page.locator('[data-testid="btn-submit"]').click()

    resume_error = page.locator('[data-testid="error-resume"]')
    expect(resume_error).to_be_visible()
    expect(resume_error).to_contain_text("Resume must be a .pdf, .docx, .doc, or .txt file")
