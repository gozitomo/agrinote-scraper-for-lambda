class AgriNoteError(Exception):
    """プロジェクト全体の基本例外"""
    pass

class LoginError(Exception):
    """ログイン失敗時の例外"""
    pass

class ScrapeError(Exception):
    """スクレイピング中に発生する例外"""
    pass

class WriteError(Exception):
    """書き込み中に発生する例外"""
    pass