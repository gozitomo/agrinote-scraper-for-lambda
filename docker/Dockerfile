# ビルド用ステージ
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 実行用ステージ
FROM python:3.12-slim-bookworm
WORKDIR /var/task

# 以前のDockerfileから継承:基本パッケージ＋日本語フォント
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-ipafont-gothic \
    fonts-ipafont-mincho \
    # Playwrightの実行に必要な最小限のOSライブラリ（これがないとブラウザが起動しません）
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

    # ビルドステージから仮想環境をコピー
    COPY --from=builder /app/.venv /app/.venv
    ENV PATH="/app/.venv/bin:$PATH"

    # Lambda実行ようにawslambdaricを追加
    RUN pip install awslambdaric

    # アプリコードをコピー
    COPY src/ ./src/

    # Playwrightブラウザの（Chromium）インストール先
    ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
    # Playwrightブラウザのインストール
    RUN playwright install chromium && chmod -R 777 /ms-playwright && rm -rf /var/lib/apt/lists/*
   
    # Lambda用エントリーポイント
    # src/main.pyの中にhandler（evenv, context）が存在
    ENTRYPOINT [ "/app/.venv/bin/python", "-m", "awslambdaric"]
    # 以下はLambda起動時に上書き
    CMD ["src.app_scraper.handler"]