from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://quotes.toscrape.com/login")
    page.wait_for_load_state("networkidle")
    page.fill("#username", "admin")
    page.fill("#password", "123456")
    page.click("input[type='submit']")
    input("Press Enter to close the browser...")
    browser.close()