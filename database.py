import sqlite3

DB_PATH = 'egebot.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS progress
                 (user_id INTEGER, topic TEXT, passed INTEGER,
                 UNIQUE(user_id, topic))''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def update_progress(user_id: int, topic: str, passed: int = 1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO progress (user_id, topic, passed)
                 VALUES (?, ?, ?)
                 ON CONFLICT(user_id, topic) DO UPDATE SET passed=excluded.passed''',
              (user_id, topic, passed))
    conn.commit()
    conn.close()

def check_progress(user_id: int, topic: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT passed FROM progress WHERE user_id=? AND topic=?', (user_id, topic))
    res = c.fetchone()
    conn.close()
    return res[0] if res else 0

def set_setting(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO settings (key, value)
                 VALUES (?, ?)
                 ON CONFLICT(key) DO UPDATE SET value=excluded.value''',
              (key, value))
    conn.commit()
    conn.close()

def get_setting(key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key=?', (key,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None
