import base64
import hashlib
import hmac
import json
import os

import requests
import boto3
import urllib

from src.utils.logger import logger

SLACK_SIGNING_SECRET = os.getenv("SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("BOT_TOKEN")
# Lambda2の関数名
SCRAPER_NAME = "pgfarm-agrinote-data-sync"


def verify_slack_signature(event):
    # 署名検証
    headers = event.get("headers", {})
    timestamp = headers.get("x-slack-request-timestamp")
    signature = headers.get("x-slack-signature")
    if not timestamp or not signature:
        return False
    body = event.get("body", "")
    base_string = f"v0:{timestamp}:{body}".encode("utf-8")
    my_signature = f"v0={
        hmac.new(
            SLACK_SIGNING_SECRET.encode('utf-8'), base_string, hashlib.sha256
        ).hexdigest()
    }"

    return hmac.compare_digest(my_signature, signature)


def handler(event, context):

    # SlackのInteractivityは"payload=..."という形式で届くのでパースが必要
    body_raw = event.get("body", "")
    if event.get("isBase64Encoded"):
        body_raw = base64.b64decode(body_raw).decode("utf-8")
    if not body_raw:
        return {"statusCode": 200, "body": "Empty body"}

    try:
        if body_raw.startswith("payload="):
            parsed = urllib.parse.parse_qs(body_raw)
            body = json.loads(parsed["payload"][0])
        else:
            body = json.loads(body_raw)
    except Exception as e:
        logger.error(
            f"ERROR: Failed to parse JSON. RequestID: {context.aws_request_id} Body: {body_raw}"
        )
        logger.error(f"Error detail: {e}")
        return {"statusCode": 200, "body": "ok"}

    # 1. URL検証（challenge）
    if body.get("type") == "url_verification":
        return {"statusCode": 200, "body": body.get("challenge")}

    # 2. ボタン押下（Interactivity）の処理
    if body.get("type") == "block_actions":
        action_id = body["actions"][0].get("action_id")
        user_id = body["user"]["id"]

        if action_id == "start_scraping_event":
            logger.info(f"ボタン検知{user_id}のためにLambda2を起動")

            # Lambda2を起動（非同期）
            lambda_client = boto3.client("lambda")
            payload = {"user_id": user_id, "source": "slack_button"}

            lambda_client.invoke(
                FunctionName=SCRAPER_NAME,
                InvocationType="Event",
                Payload=json.dumps(payload),
            )

            return {"statusCode": 200, "body": ""}

        # 3. 通常のイベント（ホーム画面を開いた時）
        if "event" in body:
            slack_event = body["event"]
            if slack_event.get("type") == "app_home_opened":
                publish_home_view(slack_event.get("user"))

        return {"statusCode": 200, "body": "ok"}

    return {"statusCode": 200, "body": "ok"}


def publish_home_view(user_id):
    """Slackのホーム画面を描画する"""
    url = "https://slack.com/api/views.publish"

    # 画面のデザイン（Block Kit）
    view = {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚜 アグリノート・スクレイパー管理パネル",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "ボタンを押すとスクレイピングを開始します。\n結果は完了次第、DMでお知らせします。",
                },
            },
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚀 スクレイピング開始"},
                        "style": "primary",
                        "action_id": "start_scraping_event",  # このIDを後で使います
                    }
                ],
            },
        ],
    }

    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {"user_id": user_id, "view": view}

    res = requests.post(url, headers=headers, json=payload)
    logger.info(f"Publish view response: {res.text}")
