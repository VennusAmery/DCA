from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://legal.dca.gob.gt/", timeout=60000)

    # espera real a que cargue el visor
    page.wait_for_timeout(8000)

    # captura pantalla COMPLETA
    page.screenshot(path="dca_page.png", full_page=True)

    browser.close()
