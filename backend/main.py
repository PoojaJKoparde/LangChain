#!/usr/bin/env python
import sqlite3
import json
import os
from datetime import datetime
from langchain_ollama import ChatOllama
from tabulate import tabulate

# -----------------------------
# 1️⃣ Initialize Ollama LLM
# -----------------------------
llm = ChatOllama(
    model="phi3:mini",
    temperature=0,
    timeout=60
)

# -----------------------------
# 2️⃣ Connect to SQLite DB
# -----------------------------
DB_NAME = "test_db.sqlite"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_list = [row[0] for row in cursor.fetchall()]
print("Available tables:", table_list)

# -----------------------------
# 3️⃣ Chat history file
# -----------------------------
HISTORY_FILE = "chat_history.json"

# Load old history if exists
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            chat_history = json.load(f)
    except:
        chat_history = []
else:
    chat_history = []

# -----------------------------
# 4️⃣ Execute SQL safely
# -----------------------------
def execute_sql_query(sql):
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            return "No results found."

        headers = [desc[0] for desc in cursor.description]
        return tabulate(rows[:10], headers=headers, tablefmt="grid")

    except Exception as e:
        return f"Error: {e}"

# -----------------------------
# 5️⃣ English → SQL (CLEAN)
# -----------------------------
def english_to_sql(question):
    prompt = f"""
You are a SQLite expert.

Database tables:
{table_list}

Rules:
- Use ONLY existing tables & columns
- NO markdown
- NO explanations
- Return ONLY valid SQLite SQL

User question:
{question}
"""
    response = llm.invoke(prompt)

    sql = response.content.strip()

    # 🔥 REMOVE MARKDOWN (CRITICAL FIX)
    sql = sql.replace("```sql", "").replace("```", "").strip()

    print("DEBUG SQL:", sql)  # helpful for learning
    return sql

# -----------------------------
# 6️⃣ Detect DB questions (FAST)
# -----------------------------
def is_sql_question(text):
    keywords = [
        "show", "list", "count", "total", "number",
        "employees", "albums", "customers",
        "tracks", "artists", "invoice", "genre"
    ]
    return any(k in text.lower() for k in keywords)

# -----------------------------
# 7️⃣ Chat loop
# -----------------------------
print("\nAI Learning Assistant (type 'exit' to quit)\n")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "exit":
        break

    try:
        if is_sql_question(user_input):
            sql = english_to_sql(user_input)
            answer = execute_sql_query(sql)
        else:
            answer = llm.invoke(user_input).content

        print("AI:", answer)

        # Save chat
        chat_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": answer
        })

        # Write immediately (NO data loss)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print("Error:", e)

# -----------------------------
# 8️⃣ Cleanup
# -----------------------------
conn.close()
print(f"\n✅ Chat history saved to {os.path.abspath(HISTORY_FILE)}")
