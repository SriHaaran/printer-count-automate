from playwright.sync_api import Page

from config.settings import PRINTER_BASE_URL, LOGIN_USER, LOGIN_PASS

def _all_contexts(page: Page):
    return [page] + list(page.frames)

def _first_visible_locator(ctx, selectors):
    for sel in selectors:
        try:
            loc = ctx.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                return loc.first
        except Exception:
            continue
    return None

def _click_login_link(page: Page):
    candidates = [
        'a:has-text("Login")',
        'text=Login',
        'a[href*="login"]',
        'a[href*="Login"]',
        'a[title*="Login"]',
    ]

    page.wait_for_timeout(2000)

    for ctx in _all_contexts(page):
        for sel in candidates:
            try:
                loc = ctx.locator(sel)
                if loc.count() == 0:
                    continue

                for i in range(loc.count()):
                    item = loc.nth(i)
                    if item.is_visible():
                        item.click(timeout=5000)
                        page.wait_for_timeout(2000)
                        return
            except Exception:
                continue

    raise RuntimeError("Login link/button not found on landing page.")

def _find_login_context(page: Page):
    username_selectors = [
        'input[name="userid"]',
        'input[name="userId"]',
        'input[name="login_user"]',
        'input[type="text"]',
    ]

    for ctx in _all_contexts(page):
        for sel in username_selectors:
            try:
                loc = ctx.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    return ctx
            except Exception:
                continue

    raise RuntimeError("Login form not found on page or frames.")

def _click_text_in_any_context(page: Page, text_value: str) -> bool:
    for ctx in _all_contexts(page):
        try:
            loc = ctx.get_by_text(text_value, exact=False)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click(timeout=5000)
                page.wait_for_timeout(2000)
                return True
        except Exception:
            continue
    return False

def login_and_go_history(page: Page):
    page.goto(PRINTER_BASE_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    _click_login_link(page)

    login_ctx = _find_login_context(page)

    username_loc = _first_visible_locator(login_ctx, [
        'input[name="userid"]',
        'input[name="userId"]',
        'input[name="login_user"]',
        'input[type="text"]',
    ])
    password_loc = _first_visible_locator(login_ctx, [
        'input[name="password"]',
        'input[name="login_pass"]',
        'input[type="password"]',
    ])
    login_button = _first_visible_locator(login_ctx, [
        'input[type="submit"]',
        'input[type="button"][value="Login"]',
        'button:has-text("Login")',
        'input[value="Login"]',
    ])

    if username_loc is None:
        raise RuntimeError("Username input not found.")
    if login_button is None:
        raise RuntimeError("Login submit button not found.")

    username_loc.fill(LOGIN_USER)
    if password_loc is not None:
        password_loc.fill(LOGIN_PASS)

    login_button.click()
    page.wait_for_timeout(3000)

    if not _click_text_in_any_context(page, "Print Job/Stored File"):
        raise RuntimeError("Menu 'Print Job/Stored File' not found.")

    if not _click_text_in_any_context(page, "Printer: Print Jobs"):
        raise RuntimeError("'Printer: Print Jobs' not found.")

    if not _click_text_in_any_context(page, "Go to [Printer Job History]"):
        raise RuntimeError("'Go to [Printer Job History]' not found.")

    page.wait_for_timeout(3000)

def find_history_frame(page: Page):
    for frame in page.frames:
        try:
            if "jobHistory.cgi" in (frame.url or ""):
                return frame
        except Exception:
            continue

    for frame in page.frames:
        try:
            loc = frame.locator("table.reportListCommon")
            if loc.count() > 0:
                return frame
        except Exception:
            continue

    try:
        if page.locator("table.reportListCommon").count() > 0:
            return page
    except Exception:
        pass

    raise RuntimeError("History frame not found.")