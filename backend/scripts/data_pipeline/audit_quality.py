import sqlite3
import pandas as pd
import sys

def audit_database(db_path, threshold=5.0):
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM games", conn)
        total = len(df)
        missing = df.isnull().mean() * 100
        
        print(f"--- Database Audit Report ---")
        print(f"Total entries: {total}")
        print(f"Missing data ratio (%):\n{missing}")
        
        # 閾値チェック
        high_missing = missing[missing > threshold]
        if not high_missing.empty:
            print(f"\n[ALERT] Quality Alert: Columns exceeding {threshold}% missing data:")
            print(high_missing)
            sys.exit(1) # 監査失敗として終了
        else:
            print("\n[OK] Quality standards met.")
            sys.exit(0)
    except Exception as e:
        print(f"Audit failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    audit_database("backend/games.db")
