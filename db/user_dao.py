import sqlite3
import hashlib
from models.user import User

DB_NAME = "pharmacie.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_user_table():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT CHECK(role in ('medecin','pharmacien')) NOT NULL DEFAULT 'pharmacien',
            adresse TEXT DEFAULT '',
            tel TEXT DEFAULT ''
        )
    """)
    conn.commit()
    # Création du compte medecin si aucun utilisateur
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        add_user("medecin", "medecin", "medecin", "Adresse du cabinet", "0000000000")
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, role="pharmacien", adresse="", tel=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password_hash, role, adresse, tel) VALUES (?, ?, ?, ?, ?)",
        (username, hash_password(password), role, adresse, tel)
    )
    conn.commit()
    conn.close()

def delete_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=? AND role='pharmacien'", (username,))
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, role, adresse, tel FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and hash_password(password) == row[2]:
        return User(*row)
    return None

def list_pharmaciens():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash, role, adresse, tel FROM users WHERE role='pharmacien'")
    rows = c.fetchall()
    conn.close()
    return [User(*row) for row in rows]

def update_user_infos(user_id, new_password=None, adresse=None, tel=None, username=None):
    conn = get_conn()
    c = conn.cursor()
    if username:
        c.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))
    if new_password:
        c.execute(
            "UPDATE users SET password_hash=?, adresse=?, tel=? WHERE id=?",
            (hash_password(new_password), adresse, tel, user_id)
        )
    else:
        c.execute(
            "UPDATE users SET adresse=?, tel=? WHERE id=?",
            (adresse, tel, user_id)
        )
    conn.commit()
    conn.close()

def username_exists(new_username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE username=?", (new_username,))
    exists = c.fetchone()[0] > 0
    conn.close()
    return exists