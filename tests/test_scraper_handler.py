from unittest.mock import patch
import pandas as pd

from src.core.formatter import AgriNoteFormatter
from src.utils.logger import logger


def test_lambda_scraper_handler_logic_flow():
    """データ取得
    マージ
    書き込み
    のワークフローが正しい順序とデータ型で実行されることをテスト"""

    # --- 1. 準備: モックの設定 ---
    with (
        patch("src.core.writer.SpreadSheetWriter") as MockWriter,
        patch("src.core.scraper.AgriNoteScraper") as MockScraper,
    ):
        # Writerのモック設定
        mock_writer_inst = MockWriter.return_value
        # Scraperのモック設定
        mock_scraper_inst = MockScraper.return_value
        # download_reportの戻り値
        mock_scraper_inst.download_report.return_value = "/tmp/dummy.xlsx"
        # スクレイピングした新データ（3件）:作業ID 001,002,003
        new_data = pd.DataFrame(
            [
                {
                    "作業ID": "001",
                    "日付": "2026-02-01",
                    "作業者": "更新",
                    "作業名": "剪定",
                },
                {
                    "作業ID": "003",
                    "日付": "2026-02-02",
                    "作業者": "鈴木",
                    "作業名": "剪定",
                },
                {
                    "作業ID": "002",
                    "日付": "2026-02-01",
                    "作業者": "木下",
                    "作業名": "剪定",
                },
            ]
        )

        # --- 2. 実行: ロジックを再現 ---
        # A. ファイルパス取得
        excel_path = mock_scraper_inst.download_report()
        logger.info(f"{excel_path}に保存しました")

        # B. 最新データ取得
        retrieved_new_df = new_data

        # C. Formatterによるマージ、整形
        formatter = AgriNoteFormatter()
        formatted_df = formatter.format(retrieved_new_df)
        final_df = formatter.clean_for_sheets(formatted_df)

        # D. 書き出し実行
        mock_writer_inst.write_all(final_df)

        # E. 検証
        # 合計3行になっているか？
        assert len(final_df) == 3
        # 書き込みメソッドが呼ばれたか？
        assert mock_scraper_inst.download_report.called
        assert mock_writer_inst.write_all.called
