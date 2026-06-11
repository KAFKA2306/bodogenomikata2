import subprocess
import time

def run_loop():
    while True:
        print("--- Iteration Start ---")
        
        # 1. Kaggleからインジェスト
        print("Running Kaggle ingestion...")
        # 実際にデータファイルを配置したらここを有効化する
        # subprocess.run(["python3", "backend/scripts/data_pipeline/ingest_kaggle.py"])
        
        # 2. Audit
        audit = subprocess.run(["python3", "backend/scripts/data_pipeline/audit_quality.py"], capture_output=True)
        
        if audit.returncode == 0:
            print("Audit passed.")
            break # 完了
        else:
            print("Audit failed. Initiating CorrectionAgent...")
            # 3. Self-Correction
            subprocess.run(["python3", "backend/scripts/data_pipeline/correction_agent.py"])
            
        time.sleep(2) 

if __name__ == "__main__":
    run_loop()
