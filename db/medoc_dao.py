from db.db_manager import get_connection
from models.medicament import Medicament

def ajouter_medicament(nom, stock, prix, seuil_alerte=10, image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO medicaments (nom, stock, prix, seuil_alerte, image_path) VALUES (?, ?, ?, ?, ?)",
        (nom, stock, prix, seuil_alerte, image_path)
    )
    conn.commit()
    conn.close()

def lister_medicaments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicaments")
    rows = cursor.fetchall()
    conn.close()
    return [Medicament(*row) for row in rows]

def vendre_medicament(medicament_id, quantite, date_vente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM medicaments WHERE id = ?", (medicament_id,))
    stock = cursor.fetchone()[0]
    if stock < quantite:
        conn.close()
        return False
    cursor.execute(
        "UPDATE medicaments SET stock = stock - ? WHERE id = ?",
        (quantite, medicament_id)
    )
    cursor.execute(
        "INSERT INTO ventes (medicament_id, quantite, date_vente) VALUES (?, ?, ?)",
        (medicament_id, quantite, date_vente)
    )
    conn.commit()
    conn.close()
    return True

def get_alertes_stock():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicaments WHERE stock <= seuil_alerte")
    rows = cursor.fetchall()
    conn.close()
    return [Medicament(*row) for row in rows]

def modifier_medicament(med_id, nouveau_nom, nouveau_stock, nouveau_prix, nouveau_seuil, image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    if image_path is not None:
        cursor.execute(
            "UPDATE medicaments SET nom=?, stock=?, prix=?, seuil_alerte=?, image_path=? WHERE id=?",
            (nouveau_nom, nouveau_stock, nouveau_prix, nouveau_seuil, image_path, med_id)
        )
    else:
        cursor.execute(
            "UPDATE medicaments SET nom=?, stock=?, prix=?, seuil_alerte=? WHERE id=?",
            (nouveau_nom, nouveau_stock, nouveau_prix, nouveau_seuil, med_id)
        )
    conn.commit()
    conn.close()