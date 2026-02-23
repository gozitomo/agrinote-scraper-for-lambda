# agrinote-scraper-for-lambda
アグリノートから作業記録エクセルをダウンロードし、GoogleSpreadSheetとして保存する
（保存後Slack通知する処理については別途GASで実装）

## 処理の流れ（Architecture）
本システムは以下のステップでデータを処理します。
TDDを考慮して、各工程は疎結合に設計。

1. **連携1（スラックから）**:  Slackからボタン押下によりscraper用Lambdaに連携、Slackにレスポンスを返す
1. **連携2（定時実行）**:  EventBridgeにより毎日21時にscraper用Lambdaを起動
1. **Scrape**: `Playwright` を使用してアグリノートから生データを取得
1. **Format**: 取得データを`Pandas` で整形し、スプレッドシート用の行列形式に変換
1. **Load**: `gspread` を介してGoogleSheetsAPIで書き込み

## フォルダ構成
```text
.
|-- src/
|   |-- app_slack.py    # Slackからのリクエストをscraperに繋ぐ（event, contextを渡す）
|   |-- app_scraper.py  # Lambdaエントリポイント（event, contextを受け取る）
|   |-- core/           # 主要ロジック（Scraper, Formatter, Browser管理）
|   |-- adapters/       # 外部接続（Spreadsheet連携、Slack通知）
|   |-- utils/          # 共通処理（Logger, Config）
|-- tests/              # pytestによるテストコード
|-- docker/             # Lambda環境用Dockerfile
|-- README.md
```

## 開発フロー（TDD）
本プロジェクトはテスト駆動開発を採用しています。新機能の実装やロジックの修正時は、以下の順序で進めます。
1. tests/ 内に期待する挙動のテストを書く（失敗を確認）。
1. src/ 内に最小限の実装を行う。
1. テストをパスさせ、必要に応じてリファクタリングする。

## テスト実行
```bash
uv run pytest
```

## 環境変数
実行には以下の環境変数が必要です。
- AGRI_NOTE_ID: アグリノートログインID
- AGRI_NOTE_PASS: アグリノートパスワード
- SPREADSHEET_ID: 出力先スプレッドシートID
- SERVICE_ACCOUNT_JSON: GoogleサービスアカウントのJSON文字列



