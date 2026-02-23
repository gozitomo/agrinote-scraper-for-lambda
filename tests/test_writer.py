from unittest.mock import MagicMock, patch
import pandas as pd

from src.adapters.writer import SpreadSheetWriter
from src.utils.logger import logger


def test_spreadsheet_writer_interface():
    # 1. 初期化のテスト
    writer = SpreadSheetWriter()

    assert hasattr(writer, "read_all")
    assert hasattr(writer, "write_all")


def test_spreadsheet_read_all():
    # 1. 初期化のテスト
    writer = SpreadSheetWriter()

    # 2. 全データの読み込み
    df = writer.read_all()

    # 3. 検証
    # 戻り値がpandasのDataFrameであること
    assert isinstance(df, pd.DataFrame)
    # 4. ヘッダーが存在すること
    if not df.empty:
        assert "作業ID" in df.columns
    else:
        logger.info("Sheet is empty, but call succeeded.")


def test_read_all_empty_sheet_handling():
    """シートがからの時もエラーにならず空のDFを返す"""
    # patchを使って、gspreadのサービスアカウント認証をバイパス
    with patch("gspread.service_account_from_dict"):
        writer = SpreadSheetWriter()

        # ワークシートをモックに差し替え
        writer._ws = MagicMock()
        writer._ws.get_all_records.return_value = []

        # 実行
        df = writer.read_all()

        # 検証
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    # TODO: テスト用の空のシートIDを準備するか、モックで再現する
    pass


def test_write_all_logic_with_mock_data():
    """書き込み実行せずに内部ロジック（クリアと更新の呼び出し）をテスト"""
    # 1. 認証部分をモックに、インスタンス化を空振り
    with patch("gspread.service_account_from_dict"):
        writer = SpreadSheetWriter()

        # 2. ワークシートをモックに差し替え
        mock_ws = MagicMock()
        writer._ws = mock_ws

        # 3. テスト用データ準備
        test_df = pd.DataFrame([{"作業ID": "T001", "内容": "テスト"}])

        # 4. 実行
        writer.write_all(test_df)

        # 5. 検証

        # ws.clear()が呼ばれた
        assert mock_ws.clear.called

        # ws.update()が呼ばれた
        expected_values = [["作業ID", "内容"], ["T001", "テスト"]]

        # 第1引数が期待通り
        mock_ws.update.assert_called_with(expected_values)
