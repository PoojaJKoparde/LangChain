import sqlite3

# Connect (creates file if it doesn't exist)
conn = sqlite3.connect("test_db.sqlite")
cursor = conn.cursor()

# Create a simple table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    city TEXT
)
""")

# Insert sample data
cursor.execute("INSERT INTO users (name, age, city) VALUES ('Alice', 25, 'New York')")
cursor.execute("INSERT INTO users (name, age, city) VALUES ('Bob', 30, 'Los Angeles')")
cursor.execute("INSERT INTO users (name, age, city) VALUES ('Charlie', 22, 'Chicago')")

conn.commit()
conn.close()

print("✅ test_db.sqlite created with sample data!")
