import os
import zipfile
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from src.utils.logger import logger
from src.utils.error import AgriNoteError, LoginError


class AgriNoteScraper:
    def __init__(self, page):
        self.page = page

    def login(self, user_id, password):
        self.page.goto("https://agri-note.jp/b/login/")
        self.page.locator('input[type="text"]').first.fill(user_id)
        self.page.locator('input[type="password"]').fill(password)
        self.page.get_by_role("button", name="ログイン").click()

        try:
            # 成功
            self.page.wait_for_selector("#headerHamburgerMenu", timeout=10000)
        except PlaywrightTimeoutError:
            # 失敗
            if self.page.locator("p._1n3hn89z").is_visible():
                raise LoginError(
                    "メールアドレス、アカウントID、またはパスワードが一致しません。"
                )
            else:
                raise AgriNoteError(
                    "ログインに失敗し、予期しない画面が表示されました。"
                )

    def download_report(self):
        def handle_dialog(dialog):
            logger.info(f"標準アラート出現: {dialog.message}")
            dialog.accept()  # OKボタンを押下

        # 1. ページ移動
        self.page.goto("https://agri-note.jp/b/export.html#/top")

        # 2. 「作業記録」を選択
        self.page.locator("li").get_by_text("作業記録").click()

        # 3. 期間指定とエクセル形式を選択
        self.page.get_by_label("全期間").check()
        self.page.get_by_label("Excel").check()

        # 4. ページに対してリスナーをセット
        self.page.on("dialog", handle_dialog)

        # 5. 生成ボタンを押下
        self.page.get_by_role("button", name="生成").click()

        # 6. ダウンロードリンクが出現するのを待つ
        download_link = self.page.get_by_role("link", name="ダウンロード")
        download_link.wait_for(state="visible", timeout=120000)

        # 7. ファイルのダウンロードを実行
        with self.page.expect_download(timeout=120000) as download_info:
            download_link.click(timeout=120000)

        download = download_info.value

        # 8. zip保存先
        download_path = os.path.join("/tmp", download.suggested_filename)
        download.save_as(download_path)

        return self._extract_excel(download_path, target_keyword="作業者")

    def _extract_excel(self, zip_path: str, target_keyword: str) -> str:
        """ZIPを解凍して特定のエクセルを抽出"""
        # 解凍先
        extract_dir = "/tmp/extracted"
        os.makedirs(extract_dir, exist_ok=True)

        # ファイル名指定
        target_keyword = "作業者"

        # 7. Zipを開いて中身をチェック
        with zipfile.ZipFile(zip_path, "r") as z:
            # Excelファイル（.xlsx）を探して抽出
            for file_info in z.infolist():
                # 文字化けを直して名前を確認
                filename = self._fix_encoding(file_info.filename)

                if target_keyword in filename and filename.endswith(".xlsx"):
                    excel_path = os.path.join(extract_dir, filename)
                    with z.open(file_info) as src, open(excel_path, "wb") as dst:
                        dst.write(src.read())

                    return excel_path  # Excelが見つかったらそのパスを返す
        raise AgriNoteError(
            f"ZIP内にキーワード'{target_keyword}'を含むExcelがみつかりませんでした"
        )

    def _fix_encoding(self, raw_name):
        try:
            return raw_name.encode("cp437").decode("cp932")
        except (UnicodeDecodeError, UnicodeEncodeError):
            # テスト時やUTF-8で保存されている場合はそのまま返す
            return raw_name
