import os
import pytest
from backend.app.core import sqlite_client

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """本物のSQLiteファイルを使用してテスト環境を構築します。"""
    test_db = "backend/test_games.db"
    # 既存のテストDBがあれば削除
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # 環境変数をテスト用DBに切り替え (sqlite_clientが参照するように)
    os.environ["DATABASE_URL"] = test_db
    
    sqlite_client.init_database()
    yield
    
    # テスト終了後にクリーンアップ
    if os.path.exists(test_db):
        os.remove(test_db)
