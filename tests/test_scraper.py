
import os
from unittest.mock import MagicMock
import zipfile

import pytest
from dotenv import load_dotenv
from src.core.browser import BrowserManager
from src.core.scraper import AgriNoteScraper
from src.utils.error import LoginError

# .envファイルから環境変数を読み込む
load_dotenv()

def test_download_success():
    user_id = os.getenv("AGRI_NOTE_ID")
    password = os.getenv("AGRI_NOTE_PASS")

    if not user_id or not password:
        pytest.skip("AGRI_NOTE_ID or AGRI_NOTE_PASS is not set.")

    with BrowserManager(headless=True) as browser:
        context = browser.new_context()
        page = context.new_page()
        scraper = AgriNoteScraper(page)

        # ログイン実行
        scraper.login(user_id, password)

        # 実行：ダウンロード処理を呼び出す
        # 戻り値としてExcelのフルパスが返ってくることを期待
        excel_path = scraper.download_report()

        # 検証：ファイルが実在するか
        assert os.path.exists(excel_path)
        assert excel_path.endswith(".xlsx")

def test_login_failure_raises_error():
        
    with BrowserManager(headless=True) as browser:
        page = browser.new_page()
        scraper = AgriNoteScraper(page)

        # 1. 検証: ちゃんとエラーが発生するか？
        with pytest.raises(LoginError) as excinfo:
            scraper.login("wrong-id", "wrong-pass")
        
        # 2. 検証: エラーメッセージの中身をチェック
        assert "一致しません" in str(excinfo.value)    

def test_extract_excel_from_zip(tmp_path):
    """ZIPから特定のエクセルを正しく抽出できるかテスト"""
    scraper = AgriNoteScraper(MagicMock()) # 偽ブラウザ

    # 1. テスト用ZIPをtmpディレクトリに作成
    zip_path = tmp_path / "test.zip"
    excel_filename = "作業記録２ 作業者.xlsx"

    # ダミーのExcel内容
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr(excel_filename, b"dummy excel content")

    # 2. スクレイパー解凍ロジック
    result_path = scraper._extract_excel(str(zip_path), target_keyword="作業者")

    # 3. 検証
    assert os.path.exists(result_path)
    assert "作業者" in result_path
