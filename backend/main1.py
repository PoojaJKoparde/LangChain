#!/usr/bin/env python
import os
import sqlite3
import json
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# -----------------------------
# 1️⃣ Initialize Ollama LLM
# -----------------------------
llm = ChatOllama(model="phi3:mini", temperature=0)

# -----------------------------
# 2️⃣ Memory storage for chat
# -----------------------------
store = {}

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chat = RunnableWithMessageHistory(llm, get_session_history)

# -----------------------------
# 3️⃣ Load chat history
# -----------------------------
chat_history_json = []
try:
    with open("chat_history.json", "r", encoding="utf-8") as f:
        saved_history = json.load(f)
        history = get_session_history("user1")
        for msg in saved_history:
            history.add_user_message(msg["user"])
            history.add_ai_message(msg["ai"])
        chat_history_json = saved_history
except FileNotFoundError:
    pass

# -----------------------------
# 4️⃣ Connect to SQLite DB
# -----------------------------
DB_NAME = "test_db.sqlite"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_list = [row[0] for row in cursor.fetchall()]
print(f"Available tables in DB: {table_list}")

# -----------------------------
# 5️⃣ Execute SQL safely
# -----------------------------
def execute_sql_query(sql_query: str) -> str:
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        if not results:
            return "No results found."

        # Format results like a table
        formatted = [" | ".join(columns)]
        formatted.append("-" * len(" | ".join(columns)))
        for row in results[:10]:  # first 10 rows
            formatted.append(" | ".join(str(r) for r in row))
        return "\n".join(formatted)
    except Exception as e:
        return f"Error executing SQL: {e}"

# -----------------------------
# 6️⃣ Convert English → SQL (with schema context)
# -----------------------------
def english_to_sql(english_text: str) -> str:
    # Provide LLM with exact table names and instructions
    prompt = f"""
You are a SQL expert for SQLite. Only generate valid SQL queries
based on the following tables: {table_list}.

Convert the following English request to a working SQL query:
'{english_text}'

Return only the SQL query.
"""
    response = chat.invoke(prompt, config={"configurable": {"session_id": "user1"}})
    return response.content.strip()

# -----------------------------
# 7️⃣ Interactive loop
# -----------------------------
print("AI Learning Assistant (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    sql_keywords = ["select", "update", "delete", "insert", "create", "drop"]
    if any(user_input.strip().lower().startswith(k) for k in sql_keywords):
        ai_reply = execute_sql_query(user_input)
    else:
        sql_query = english_to_sql(user_input)
        ai_reply = execute_sql_query(sql_query)

    print("AI:", ai_reply)

    # Save history
    chat_history_json.append({
        "timestamp": datetime.now().isoformat(),
        "user": user_input,
        "ai": ai_reply
    })

# -----------------------------
# 8️⃣ Save JSON chat history
# -----------------------------
with open("chat_history.json", "w", encoding="utf-8") as f:
    json.dump(chat_history_json, f, indent=4, ensure_ascii=False)

conn.close()
print("✅ Chat history saved.")
