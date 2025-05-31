# Gestion de Pharmacie

Application de gestion de stock et ventes pour une pharmacie (Python, Tkinter, SQLite).

note SuperAdmin Access :

   ```username : medecin
      password : medecin
   ```

## Lancer le projet

1. Activez l'environnement virtuel
2. Lancez :

   ```bash
   python main.py
   ```

3. L'interface s'ouvre. Vous pouvez :
   - Ajouter un médicament
   - Vendre un médicament
   - Afficher les alertes de stock faible

## Structure

- `main.py` : point d'entrée
- `db/` : gestion base de données
- `models/` : classes métier (ex : médicament)
- `ui/` : interface graphique

## Stack

- Python 3.x
- Tkinter (inclus)
- SQLite3 (inclus)
