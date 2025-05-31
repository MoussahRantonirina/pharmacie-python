import sqlite3

DB_NAME = "pharmacie.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            stock INTEGER NOT NULL,
            prix REAL NOT NULL,
            seuil_alerte INTEGER DEFAULT 10,
            image_path TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicament_id INTEGER,
            quantite INTEGER,
            date_vente TEXT,
            FOREIGN KEY(medicament_id) REFERENCES medicaments(id)
        )
    """)
    conn.commit()
    conn.close()