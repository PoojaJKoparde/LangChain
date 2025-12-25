import pandas as pd
import sqlite3
import os

DB_NAME = "test_db.sqlite"
CSV_FOLDER = "csv_db"   # must match folder name

conn = sqlite3.connect(DB_NAME)

for file in os.listdir(CSV_FOLDER):
    if file.endswith(".csv"):
        table_name = file.replace(".csv", "").replace(" ", "_").lower()
        file_path = os.path.join(CSV_FOLDER, file)

        try:
            df = pd.read_csv(file_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ Loaded {file} → table '{table_name}'")
        except Exception as e:
            print(f"❌ Failed {file}: {e}")

conn.close()
print("🎉 All CSV files loaded into SQLite")
