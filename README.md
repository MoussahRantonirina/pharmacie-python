# Gestion de Pharmacie

Application complète de gestion de stock et de ventes pour pharmacie, réalisée en Python (Tkinter, SQLite).

## 🚀 Fonctionnalités principales

- Authentification par rôle (médecin/superadmin & pharmaciens)
- Ajout, modification, vente et suivi de stock des médicaments
- Alertes automatiques sur les stocks faibles ou en rupture
- Gestion des utilisateurs pharmaciens (ajout/suppression/modification)
- Interface graphique simple et intuitive

---

## 👤 Accès SuperAdmin (Médecin)

Pour accéder à toutes les fonctionnalités :

```info
Nom d'utilisateur : medecin
Mot de passe      : medecin
```

---

## 💻 Lancer le projet

1. **Prérequis**
   - Python 3.x installé (Tkinter et SQLite inclus d’office)
2. **Installation**
   - Clonez ce repo
   - (Optionnel) Créez et activez un environnement virtuel :

     ```bash
     python -m venv venv
     source venv/bin/activate  # Linux/Mac
     venv\Scripts\activate     # Windows
     ```

   - Installez Pillow (pour la gestion des images) :

     ```bash
     pip install pillow
     ```

3. **Démarrage**
   - Dans le dossier du projet, lancez :

     ```bash
     python main.py
     ```

   - L’interface graphique s’ouvre.

---

## 🖱️ Utilisation

- **Connexion** : Saisissez vos identifiants selon votre rôle.
- **Médecin (SuperAdmin)** :
  - Gère les utilisateurs pharmaciens
  - Ajoute, modifie, vend des médicaments
  - Visualise et édite son profil
- **Pharmacien** :
  - Peut vendre des médicaments
  - Peut consulter la liste et les alertes

**Double-cliquez sur un médicament pour voir sa photo (si ajoutée).**

---

## 📁 Structure

- `main.py` : point d’entrée de l’application
- `db/` : gestion de la base SQLite et accès aux données
- `models/` : objets métier (médicament, utilisateur)
- `ui/` : composants de l’interface graphique (si présents)

---

## 🛠️ Stack technique

- Python 3.x
- Tkinter (interface graphique)
- SQLite3 (base de données locale)
- Pillow (gestion d’images - à installer)

---

## 📢 Note

- **Droits réservés** :  
  © 2025 Moussah Rantonirina. Toute reproduction ou distribution interdite sans autorisation.

---

## 🤝 Contribuer

Toute suggestion ou contribution est la bienvenue ! Ouvrez une issue ou une pull request.
