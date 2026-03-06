from playwright.sync_api import Page
from config.settings import PRINTER_BASE_URL, LOGIN_USER, LOGIN_PASS

def login_and_go_history(page: Page):
    page.goto(PRINTER_BASE_URL, wait_until="networkidle")
    page.get_by_label("Login User Name").fill(LOGIN_USER)
    page.get_by_label("Login Password").fill(LOGIN_PASS)
    page.get_by_role("button", name="Login").click()
    page.wait_for_load_state("networkidle")

    page.get_by_text("Print Job/Stored File", exact=False).click()
    page.wait_for_load_state("networkidle")

    page.get_by_text("Printer: Print Jobs", exact=False).click()
    page.wait_for_load_state("networkidle")

    page.get_by_text("Go to [Printer Job History]", exact=False).click()
    page.wait_for_load_state("networkidle")

def find_history_frame(page):
    for frame in page.frames:
        if frame.locator("table.reportListCommon").count() > 0:
            return frame
    raise RuntimeError("History frame not found.")