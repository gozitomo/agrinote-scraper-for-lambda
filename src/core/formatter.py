import pandas as pd


class AgriNoteFormatter:
    def format(self, df: pd.DataFrame) -> pd.DataFrame:
        """ダウンロードしたエクセルデータを解析・整形する"""
        df = df.dropna(how="all")

        # timedelta型の列を探して、HH:MM 形式の文字列に変換
        for col in df.columns:
            if pd.api.types.is_timedelta64_dtype(df[col]):
                df[col] = df[col].dt.total_seconds() / 3600
                df[col] = df[col].round(2)

        return df

    def clean_for_sheets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Google Sheetsへの書き込み用にDataFrameの欠損値を空文字に変更"""

        df = df.copy()
        df = df.map(lambda x: "" if pd.isna(x) else str(x))

        return df
