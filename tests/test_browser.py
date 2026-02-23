from src.core.browser import BrowserManager

def test_browser_can_open_page():
    # ブラウザを起動（ローカルで確認必要な場合はheadless=Trueにすること）
    with BrowserManager(headless=True) as browser:
        context = browser.new_context()
        page = context.new_page()

        # 実際にページへ飛んでみる
        page.goto("https://www.google.com")

        # タイトルが取得できればブラウザの動きは正常
        assert "Google" in page.title()
