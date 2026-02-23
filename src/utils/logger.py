import logging

# ルートロガーを取得
logger = logging.getLogger()

# ログレベルの設定（環境変数から取るか、デフォルトをINFOに）
log_level = "INFO"
logger.setLevel(log_level)
