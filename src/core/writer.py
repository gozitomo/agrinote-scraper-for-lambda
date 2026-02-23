import json
import os

from dotenv import load_dotenv
import gspread
import pandas as pd

from src.utils.logger import logger
from src.utils.error import WriteError

# .envファイルから環境変数を読み込む
load_dotenv()


class SpreadSheetWriter:
    def __init__(self):
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.sa_json = os.getenv("SERVICE_ACCOUNT_JSON")
        if not self.spreadsheet_id or not self.sa_json:
            raise WriteError("環境変数の取得に失敗しました")

        self._ws = None

    def _get_worksheet(self):
        """必要になった時だけ接続、2回目はキャッシュを返す"""
        if self._ws is not None:
            return self._ws

        try:
            # 1回目だけの処理
            gc = gspread.service_account_from_dict(json.loads(self.sa_json))
            sh = gc.open_by_key(self.spreadsheet_id)
            # シート名は「作業記録」
            self.ws = sh.worksheet("作業記録")

            return self.ws
        except Exception as e:
            raise WriteError(f"GoogleSpreadsheetへの接続に失敗しました: {e}")

    def read_all(self) -> pd.DataFrame:
        """キャッシュされたワークシートを使う"""
        ws = self._get_worksheet()
        """既存スプレッドシートをDataFrameとして読み込む"""
        try:
            logger.info("スプレッドシートからデータ取得中...")
            data = ws.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"読込に失敗しました: {e}")
            return pd.DataFrame()  # 失敗の時は空のDFを返す

    def write_all(self, df: pd.DataFrame):
        """キャッシュされたワークシートを使う"""
        ws = self._get_worksheet()
        """シートを空にしてDataFrameの内容を書き込む"""
        try:
            logger.info(f"スプレッドシートを更新中...（{len(df)}行）")

            # 1. シートをクリア
            ws.clear()

            # 2. DataFrameを作成
            df = df.map(lambda x: "" if pd.isna(x) else str(x))
            values = [df.columns.values.tolist()] + df.values.tolist()

            # 2. 一括アップデート
            ws.update(values)
            logger.info("書込が完了しました")
        except Exception as e:
            raise WriteError(f"書込に失敗しました: {e}")
