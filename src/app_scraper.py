import json
import os

from dotenv import load_dotenv
from src.utils.logger import logger

# .envファイルから環境変数を読み込む
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("BOT_TOKEN")


def send_slack_message(channel, text):
    import requests

    """SLACKにメッセージを送信"""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"channel": channel, "text": text}
    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        logger.info(f"Slack notification sent to {channel}")
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")


def handler(event, context):
    """Lambda用ロジック"""
    logger.info(
        f"Execution started. Event source: {event.get('source', 'Manual/Lambda1')}"
        f"RequestID: {context.aws_request_id}"
    )
    """
    lambda2: スクレイパー実行用ハンドラー（テスト版）"""

    # Lambda1から渡される情報、または手動実行時の情報を取得
    user_id = event.get("user_id", "Unknown-User")
    source = event.get("source", "Lambda1-Trigger")

    logger.info(f"Source: {source} | User: {user_id}")

    # 同期ボタンから呼び出したとき
    if source != "eventbridge-scheduled":
        # user_idを使ってメッセージを送信
        send_slack_message(user_id, "アグリノート同期ジョブを開始")

    try:
        # call scraping logic
        run_scraper_workflow()

        # Slack経由の時のみ通知
        if source != "eventbridge-scheduled":
            send_slack_message(
                user_id, "アグリノートからスプレッドシートへの同期が完了しました！"
            )

    except Exception as e:
        logger.error(f"ジョブ失敗: {e}", exc_info=True)
        if user_id:
            send_slack_message(user_id, f"エラー発生！: {e}")
            return
        raise e

    return {"statusCode": 200, "body": json.dumps("Test completed successfully")}


def run_scraper_workflow():
    import pandas as pd
    from src.core.browser import BrowserManager
    from src.core.formatter import AgriNoteFormatter
    from src.core.scraper import AgriNoteScraper
    from src.core.writer import SpreadSheetWriter

    """スクレイピングロジック"""
    writer = SpreadSheetWriter()
    formatter = AgriNoteFormatter()

    # 1. アグリノートから最新データ（.zip）をダウンロードし、（.xlsx）を抽出
    logger.info("1. アグリノートから最新データを取得中...")
    with BrowserManager(headless=True) as browser:
        context = browser.new_context()
        page = context.new_page()
        scraper = AgriNoteScraper(page)
        scraper.login(os.getenv("AGRI_NOTE_ID"), os.getenv("AGRI_NOTE_PASS"))

        excel_path = scraper.download_report()
        new_df = pd.read_excel(excel_path)
        logger.info("1. 完了")

    # 2. LookerStudioで表示できるようformat、文字列変換
    logger.info("2. フォーマット")
    formatted_df = formatter.format(new_df)
    cleaned_df = formatter.clean_for_sheets(formatted_df)
    logger.info("2. 完了")

    # 3. Spreadsheetに保存
    logger.info("3. Spreadsheetに保存")
    writer.write_all(cleaned_df)

    logger.info("all completed!!")


if __name__ == "__main__":
    run_scraper_workflow()
