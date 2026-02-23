import pandas as pd
import numpy as np
from src.core.formatter import AgriNoteFormatter

def test_formatter_cleans_data_for_sheets():
    # 1. 準備:timedeltaを含むダミーのDataFrameを作る
    df = pd.DataFrame({
"日付": ["2026/02/01", "2026/02/01"],
        "作業時間": pd.to_timedelta(["01:30:00", "02:15:00"]), # timedelta型
        "備考": [np.nan, "完了"] # 欠損値あり
    })

    formatter = AgriNoteFormatter()

    # 2. 実行
    formatted_df = formatter.format(df)
    result = formatter.clean_for_sheets(formatted_df)

    # 3. 検証:結果が「ヘッダー＋データ」のリスト形式で、時間は文字列になっているか？
    assert result["作業時間"].iloc[0] == "1.5"
    assert result["作業時間"].iloc[1] == "2.25"
    assert result["備考"].iloc[0] == ""
