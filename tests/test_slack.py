import time

from src.app_scraper import handler

def test_app_slack_invalid_signature():
    # 不一致署名でリクエスト送信
    event = {
        "headers": {
            "x-slack-request-tempstamp": str(int(time.time())),
            "x-slack-signature": "v0=invalid"
        },
        "body": "payload=..."
    }
    response = handler(event, None)
    assert response["statusCode"] == 401