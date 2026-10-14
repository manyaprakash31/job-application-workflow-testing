"""
Pytest configuration and shared fixtures for Job Application Workflow Testing.
Manages mock server lifecycle, browser contexts, test isolation, and reporting.
"""

import os
import socket
import sys
import threading
import time
import urllib.request
import pytest
from playwright.sync_api import sync_playwright

# Add app directory to sys.path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(PROJECT_DIR, "app")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from server import JobPortalHandler, ThreadingHTTPServer


def get_free_port():
    """Find an available port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def server():
    """Start the mock application server in a background thread for the test session."""
    port = get_free_port()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), JobPortalHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{port}"

    # Wait for server to become healthy
    ready = False
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"{base_url}/api/health", timeout=1) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.05)

    if not ready:
        raise RuntimeError("Failed to start mock application server.")

    yield base_url

    httpd.shutdown()
    httpd.server_close()


@pytest.fixture(scope="session")
def base_url(server):
    """Return the base URL of the active test server."""
    return server


@pytest.fixture(autouse=True)
def reset_application_state(base_url):
    """Ensure clean test isolation by resetting submitted applications before each test."""
    req = urllib.request.Request(f"{base_url}/api/reset", data=b"{}", method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 200
    yield


def pytest_addoption(parser):
    """Add command line options for browser selection."""
    parser.addoption(
        "--browser-name",
        action="store",
        default="chromium",
        help="Browser to run tests against: chromium, firefox, webkit, or all"
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run tests in headed browser mode"
    )


@pytest.fixture(scope="session")
def playwright_instance():
    """Initialize Playwright instance for the session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture
def browser(request, playwright_instance):
    """Launch the appropriate browser based on CLI option or param."""
    browser_name = getattr(request, "param", request.config.getoption("--browser-name"))
    if browser_name not in ["chromium", "firefox", "webkit"]:
        browser_name = "chromium"

    is_headed = request.config.getoption("--headed")
    browser_type = getattr(playwright_instance, browser_name)
    browser = browser_type.launch(headless=not is_headed)
    yield browser
    browser.close()


@pytest.fixture
def page(browser, request):
    """Create an isolated browser context and page for each test."""
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    yield page

    # Screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name.replace("[", "_").replace("]", "_")
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"fail_{test_name}.png")
        try:
            page.screenshot(path=screenshot_path, full_page=True)
        except Exception:
            pass

    context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test outcome for screenshots."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
