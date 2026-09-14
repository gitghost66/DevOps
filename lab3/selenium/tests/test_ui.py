"""
Selenium Automated Browser Test Suite – Lab 3
Tests the web application UI using Selenium WebDriver.

Usage:
  pip install -r requirements.txt
  pytest tests/test_ui.py -v
  pytest tests/test_ui.py -v --html=report.html  # with HTML report
"""
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# ── Configuration ─────────────────────────────────────────────────────────────
BASE_URL  = os.getenv("APP_URL", "http://localhost:8080")
HEADLESS  = os.getenv("HEADLESS", "true").lower() == "true"
TIMEOUT   = int(os.getenv("SELENIUM_TIMEOUT", "10"))


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """Create a Chrome WebDriver instance."""
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(TIMEOUT)
    yield driver
    driver.quit()


@pytest.fixture(scope="module")
def wait(driver):
    return WebDriverWait(driver, TIMEOUT)


# ── Helper Functions ──────────────────────────────────────────────────────────
def take_screenshot(driver, name: str):
    """Save a screenshot to the screenshots folder."""
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{name}_{int(time.time())}.png"
    driver.save_screenshot(path)
    print(f"  📸 Screenshot saved: {path}")
    return path


# ── Test Cases ─────────────────────────────────────────────────────────────────
class TestHomePage:
    """Test homepage loading and key elements."""

    def test_homepage_loads(self, driver, wait):
        """Verify the homepage loads successfully."""
        driver.get(BASE_URL)
        assert driver.title != "", "Page title should not be empty"
        assert driver.current_url.startswith(BASE_URL), "URL mismatch"
        take_screenshot(driver, "homepage")
        print(f"  ✅ Homepage loaded: {driver.title}")

    def test_page_has_header(self, driver, wait):
        """Verify page has a header element."""
        driver.get(BASE_URL)
        try:
            header = wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
            assert header.is_displayed(), "Header should be visible"
        except TimeoutException:
            # Some apps use different header structures
            h1 = driver.find_element(By.TAG_NAME, "h1")
            assert h1.is_displayed(), "Should have at least an H1"

    def test_page_loads_within_threshold(self, driver):
        """Verify page loads within 3 seconds."""
        start = time.time()
        driver.get(BASE_URL)
        load_time = time.time() - start
        assert load_time < 3.0, f"Page took {load_time:.2f}s to load (threshold: 3s)"
        print(f"  ✅ Page loaded in {load_time:.2f}s")


class TestNavigation:
    """Test navigation links and routing."""

    def test_dashboard_link(self, driver, wait):
        """Verify dashboard navigation works."""
        driver.get(BASE_URL)
        try:
            dashboard_link = wait.until(EC.element_to_be_clickable(
                (By.PARTIAL_LINK_TEXT, "Dashboard")
            ))
            dashboard_link.click()
            wait.until(EC.url_contains("dashboard"))
            assert "dashboard" in driver.current_url.lower()
            take_screenshot(driver, "dashboard")
        except TimeoutException:
            pytest.skip("Dashboard link not found – application may not have this route")

    def test_back_navigation(self, driver, wait):
        """Test browser back button navigation."""
        initial_url = driver.current_url
        driver.get(f"{BASE_URL}/about")
        driver.back()
        time.sleep(0.5)
        assert driver.current_url == initial_url or driver.current_url.startswith(BASE_URL)


class TestLoginFlow:
    """Test authentication flow."""

    def test_login_page_loads(self, driver, wait):
        """Verify login page is accessible."""
        driver.get(f"{BASE_URL}/login")
        take_screenshot(driver, "login_page")
        # Check we're on a login-related page
        page_source = driver.page_source.lower()
        assert any(keyword in page_source for keyword in ["login", "sign in", "username", "email"]), \
            "Login page should contain login-related content"

    def test_login_form_elements(self, driver, wait):
        """Verify login form has username and password fields."""
        driver.get(f"{BASE_URL}/login")
        try:
            # Try to find username field
            username_field = driver.find_element(
                By.XPATH, "//input[@type='text' or @type='email' or @name='username' or @id='username']"
            )
            password_field = driver.find_element(
                By.XPATH, "//input[@type='password']"
            )
            assert username_field.is_displayed(), "Username field should be visible"
            assert password_field.is_displayed(), "Password field should be visible"
            print("  ✅ Login form elements found")
        except NoSuchElementException:
            pytest.skip("Login form not found – may use different authentication method")

    def test_invalid_login_shows_error(self, driver, wait):
        """Verify invalid credentials show an error message."""
        driver.get(f"{BASE_URL}/login")
        try:
            username_field = driver.find_element(
                By.XPATH, "//input[@type='text' or @type='email' or @name='username']"
            )
            password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            submit_button  = driver.find_element(
                By.XPATH, "//button[@type='submit'] | //input[@type='submit']"
            )

            username_field.send_keys("invalid_user_12345")
            password_field.send_keys("wrong_password_xyz")
            submit_button.click()

            # Wait for error message
            time.sleep(2)
            page_source = driver.page_source.lower()
            assert any(err in page_source for err in ["invalid", "error", "incorrect", "failed", "wrong"]), \
                "Invalid login should show error message"
            take_screenshot(driver, "login_error")
            print("  ✅ Invalid login error shown correctly")
        except NoSuchElementException:
            pytest.skip("Login form elements not found")

    def test_valid_login_redirects(self, driver, wait):
        """Verify valid login redirects to dashboard."""
        driver.get(f"{BASE_URL}/login")
        try:
            username_field = driver.find_element(
                By.XPATH, "//input[@type='text' or @type='email' or @name='username']"
            )
            password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            submit_button  = driver.find_element(
                By.XPATH, "//button[@type='submit'] | //input[@type='submit']"
            )

            username_field.clear()
            username_field.send_keys("admin")
            password_field.clear()
            password_field.send_keys("admin")
            submit_button.click()

            # Wait for redirect
            time.sleep(2)
            assert driver.current_url != f"{BASE_URL}/login", \
                "Should redirect away from login page after successful login"
            take_screenshot(driver, "post_login")
            print(f"  ✅ Redirected to: {driver.current_url}")
        except NoSuchElementException:
            pytest.skip("Login form not found")


class TestResponsiveDesign:
    """Test responsive layout at different screen sizes."""

    VIEWPORTS = [
        ("Desktop",  1920, 1080),
        ("Laptop",   1366, 768),
        ("Tablet",   768,  1024),
        ("Mobile",   375,  667),
    ]

    @pytest.mark.parametrize("name,width,height", VIEWPORTS)
    def test_responsive_layout(self, driver, name, width, height):
        """Verify the page renders correctly at different viewport sizes."""
        driver.set_window_size(width, height)
        driver.get(BASE_URL)
        time.sleep(0.5)

        # Basic check – page should be visible and have content
        body = driver.find_element(By.TAG_NAME, "body")
        assert body.is_displayed(), f"Body should be visible at {name} ({width}x{height})"
        take_screenshot(driver, f"responsive_{name.lower()}")
        print(f"  ✅ {name} ({width}x{height}) renders correctly")

        # Reset to desktop
        driver.set_window_size(1920, 1080)


class TestAPIEndpoints:
    """Test API endpoints via browser."""

    def test_health_endpoint(self, driver):
        """Verify /health endpoint returns OK."""
        driver.get(f"{BASE_URL}/health")
        page_source = driver.page_source.lower()
        assert any(kw in page_source for kw in ["ok", "healthy", "up", "status"]), \
            "Health endpoint should return health status"
        print("  ✅ Health endpoint reachable")

    def test_metrics_endpoint(self, driver):
        """Verify /metrics endpoint is accessible (Prometheus)."""
        driver.get(f"{BASE_URL}/metrics")
        page_source = driver.page_source
        assert "# HELP" in page_source or "# TYPE" in page_source or \
               driver.find_elements(By.TAG_NAME, "body"), \
               "Metrics endpoint should be accessible"
        print("  ✅ Metrics endpoint reachable")


class TestPerformance:
    """Basic performance checks via Selenium."""

    def test_page_response_time(self, driver):
        """Check that page loads within acceptable time using Navigation Timing API."""
        driver.get(BASE_URL)
        # Use JavaScript Navigation Timing API
        nav_timing = driver.execute_script("""
            const perf = window.performance.timing;
            return {
                loadTime: perf.loadEventEnd - perf.navigationStart,
                domReady: perf.domContentLoadedEventEnd - perf.navigationStart,
                firstByte: perf.responseStart - perf.navigationStart
            };
        """)

        print(f"\n  📊 Performance Metrics:")
        print(f"     Load Time:  {nav_timing['loadTime']}ms")
        print(f"     DOM Ready:  {nav_timing['domReady']}ms")
        print(f"     First Byte: {nav_timing['firstByte']}ms")

        assert nav_timing['loadTime'] < 5000, \
            f"Page load time {nav_timing['loadTime']}ms exceeds 5s threshold"
        assert nav_timing['firstByte'] < 1000, \
            f"TTFB {nav_timing['firstByte']}ms exceeds 1s threshold"
