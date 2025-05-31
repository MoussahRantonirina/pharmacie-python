import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from db.db_manager import init_db
from db.medoc_dao import ajouter_medicament, lister_medicaments, vendre_medicament, modifier_medicament
from db.user_dao import add_user, delete_user, list_pharmaciens, update_user_infos, username_exists
from models.medicament import Medicament
from models.user import User
from datetime import datetime
import os

class PharmacieApp:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title(f"Gestion de Pharmacie - Connecté : {user.username} ({user.role})")
        self.root.state('zoomed')
        self.root.configure(bg="#f0f4f8")
        self.images_cache = {}

        # Menu
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        user_menu = tk.Menu(menu, tearoff=0)
        user_menu.add_command(label="Mon profil", command=self.modifier_profil)
        if user.role == "medecin":
            user_menu.add_separator()
            user_menu.add_command(label="Gérer les pharmaciens", command=self.gerer_pharmaciens)
        user_menu.add_separator()
        user_menu.add_command(label="Déconnexion", command=self.logout)
        menu.add_cascade(label=f"{user.username} ({user.role})", menu=user_menu)


        tk.Label(
            root, text="Gestion de Pharmacie", font=("Arial", 20, "bold"), bg="#f0f4f8", fg="#1976D2"
        ).pack(pady=(15, 8))

        frame_list = tk.LabelFrame(root, text="Médicaments", font=("Arial", 12, "bold"),
                                  padx=8, pady=8, bg="#f8fafc", fg="#1976D2")
        frame_list.pack(pady=(5, 10), padx=10, fill="both", expand=True)

        columns = ("Nom", "Stock", "Prix", "Seuil")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings")
        self.tree["displaycolumns"] = columns
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Prix", text="Prix (Ar)")
        self.tree.heading("Seuil", text="Seuil alerte (boîtes)")
        self.tree.column("Nom", width=210)
        self.tree.column("Stock", width=70)
        self.tree.column("Prix", width=110)
        self.tree.column("Seuil", width=140)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscroll=scrollbar.set)

        frame_btn = tk.Frame(root, bg="#f0f4f8")
        frame_btn.pack(pady=(10, 12))

        style_btn = {"font": ("Arial", 12), "bg": "#1976D2", "fg": "white", "activebackground": "#1565C0", "width": 18, "relief": "raised"}

        # Boutons selon le rôle
        self.btn_ajouter = tk.Button(frame_btn, text="Ajouter un médicament", command=self.ajouter, **style_btn)
        self.btn_ajouter.grid(row=0, column=0, padx=6, pady=4)
        self.btn_vendre = tk.Button(frame_btn, text="Vendre médicament", command=self.vendre, **style_btn)
        self.btn_vendre.grid(row=0, column=1, padx=6, pady=4)
        self.btn_editer = tk.Button(frame_btn, text="Réapprov./Éditer", command=self.editer_medicament, **style_btn)
        self.btn_editer.grid(row=0, column=2, padx=6, pady=4)
        self.btn_alertes = tk.Button(frame_btn, text="Alertes stock", command=self.alertes, **style_btn)
        self.btn_alertes.grid(row=0, column=3, padx=6, pady=4)
        self.btn_refresh = tk.Button(frame_btn, text="Rafraîchir", command=self.update_liste, **style_btn)
        self.btn_refresh.grid(row=0, column=4, padx=6, pady=4)

        legend = tk.Label(
            root, text="Légende :  Rouge = rupture | Orange = stock faible | Double-cliquez un médicament pour voir la photo",
            font=("Arial", 10), bg="#f0f4f8", fg="#666"
        )
        legend.pack(pady=(4, 0))
        tk.Label(root, text="© 2025 Moussah Rantonirina. Tous droits réservés.", font=("Arial", 9), bg="#f0f4f8", fg="#999").pack(pady=(4, 0))

        # Gestion droits
        self.apply_role_rights()

        self.update_liste()

    def apply_role_rights(self):
        if self.user.role == "pharmacien":
            self.btn_ajouter.config(state="disabled")
            self.btn_editer.config(state="disabled")
        else:
            self.btn_ajouter.config(state="normal")
            self.btn_editer.config(state="normal")

    def logout(self):
        self.root.destroy()
        import main
        main.run_app()

    def modifier_profil(self):
        ProfilDialog(self.root, self.user)

    def gerer_pharmaciens(self):
        GererPharmaciensDialog(self.root)

    def get_photo(self, path, size=(32, 32)):
        if not path or not os.path.exists(path):
            return None
        key = (path, size)
        if key not in self.images_cache:
            try:
                img = Image.open(path).resize(size)
                self.images_cache[key] = ImageTk.PhotoImage(img)
            except Exception:
                self.images_cache[key] = None
        return self.images_cache[key]

    def update_liste(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        meds = lister_medicaments()
        for med in meds:
            if med.stock < 5:
                tag = "red"
            elif 5 <= med.stock <= med.seuil_alerte:
                tag = "orange"
            else:
                tag = "black"
            photo = self.get_photo(med.image_path)
            self.tree.insert(
                "", "end", iid=med.id,
                values=(med.nom, med.stock, med.prix, med.seuil_alerte),
                tags=(tag,),
                image=photo
            )
            if not hasattr(self, 'tree_img_refs'):
                self.tree_img_refs = {}
            self.tree_img_refs[med.id] = photo
        self.tree.tag_configure("red", foreground="red")
        self.tree.tag_configure("orange", foreground="orange")
        self.tree.tag_configure("black", foreground="black")

    def ajouter(self):
        if self.user.role != "medecin":
            messagebox.showwarning("Droits insuffisants", "Seul le medecin peut ajouter un médicament.", parent=self.root)
            return
        dialog = AjoutMedicamentDialog(self.root)
        self.root.wait_window(dialog.top)
        if dialog.result:
            nom, stock, prix, seuil, img_path = dialog.result
            ajouter_medicament(nom, stock, prix, seuil, img_path)
            self.update_liste()
            messagebox.showinfo("Succès", "Médicament ajouté.", parent=self.root)

    def vendre(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un médicament.", parent=self.root)
            return
        med = [m for m in lister_medicaments() if str(m.id) == selected][0]
        dialog = VenteMedicamentDialog(self.root, med)
        self.root.wait_window(dialog.top)
        if dialog.result:
            quantite = dialog.result
            ok = vendre_medicament(med.id, quantite, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if ok:
                self.update_liste()
                messagebox.showinfo("Succès", "Vente enregistrée.", parent=self.root)
            else:
                messagebox.showerror("Erreur", "Stock insuffisant.", parent=self.root)

    def alertes(self):
        meds = lister_medicaments()
        ruptures = [m for m in meds if m.stock == 0]
        tres_faibles = [m for m in meds if 0 < m.stock <= 2]
        faibles = [m for m in meds if 3 <= m.stock <= m.seuil_alerte]
        sections = []
        if ruptures:
            lignes = [f"  - {m.nom}" for m in ruptures]
            sections.append("🔴 Rupture totale :\n" + "\n".join(lignes))
        if tres_faibles:
            lignes = [f"  - {m.nom} ({m.stock} boîte{'s' if m.stock > 1 else ''})" for m in tres_faibles]
            sections.append("🟠 Stock critique (1 ou 2 boîtes) :\n" + "\n".join(lignes))
        if faibles:
            lignes = [f"  - {m.nom} ({m.stock} boîtes)" for m in faibles]
            sections.append("🟡 Stock faible :\n" + "\n".join(lignes))
        if sections:
            msg = "\n\n".join(sections)
            if ruptures or tres_faibles:
                messagebox.showwarning("Alerte Stock", msg, parent=self.root)
            else:
                messagebox.showinfo("Alerte Stock", msg, parent=self.root)
        else:
            messagebox.showinfo("Stock OK", "Aucune alerte de stock.", parent=self.root)
        
    def editer_medicament(self):
        if self.user.role != "medecin":
            messagebox.showwarning("Droits insuffisants", "Seul le medecin peut modifier un médicament.", parent=self.root)
            return
        SelectionEditDialog(self.root, self)

    def on_tree_double_click(self, event):
        item = self.tree.focus()
        if not item:
            return
        med = [m for m in lister_medicaments() if str(m.id) == item][0]
        if med.image_path and os.path.exists(med.image_path):
            img = Image.open(med.image_path).resize((200, 200))
            img_tk = ImageTk.PhotoImage(img)
            top = tk.Toplevel(self.root)
            top.title(f"Image de {med.nom}")
            top.geometry("220x240")
            tk.Label(top, text=med.nom, font=("Arial", 14, "bold")).pack(pady=5)
            lbl = tk.Label(top, image=img_tk)
            lbl.image = img_tk
            lbl.pack(pady=10)
            tk.Button(top, text="Fermer", command=top.destroy).pack(pady=8)
        else:
            messagebox.showinfo("Info", "Aucune image associée.", parent=self.root)

class GererPharmaciensDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Gestion des pharmaciens")
        self.top.geometry("400x430")
        self.top.config(bg="#f8fafc")
        self.top.grab_set()

        tk.Label(self.top, text="Ajouter un pharmacien", font=("Arial", 14, "bold"), bg="#f8fafc", fg="#1976D2").pack(pady=6)
        frame_aj = tk.Frame(self.top, bg="#f8fafc")
        frame_aj.pack(pady=2)

        for i, (label, attr) in enumerate([
            ("Nom utilisateur:", "entry_nom"),
            ("Mot de passe:", "entry_pwd"),
            ("Adresse:", "entry_adresse"),
            ("Téléphone:", "entry_tel"),
        ]):
            tk.Label(frame_aj, text=label, font=("Arial", 11), bg="#f8fafc").grid(row=i, column=0, padx=2, sticky="w")
            entry = tk.Entry(frame_aj, font=("Arial", 11), bd=2, relief="groove", show="*" if "pwd" in attr else "")
            entry.grid(row=i, column=1, padx=2, pady=2)
            setattr(self, attr, entry)

        tk.Button(self.top, text="Ajouter", command=self.ajouter, font=("Arial", 11, "bold"), bg="#1976D2",
                  fg="white", width=13, relief="groove", activebackground="#1565C0").pack(pady=8)

        tk.Label(self.top, text="Liste des pharmaciens :", font=("Arial", 11), bg="#f8fafc").pack(pady=4)
        self.lb = tk.Listbox(self.top, font=("Arial", 11), height=8, bd=2, relief="groove", highlightcolor="#1976D2")
        self.lb.pack(pady=2, fill="both", expand=True, padx=8)
        tk.Button(self.top, text="Supprimer sélectionné", command=self.supprimer, font=("Arial", 11, "bold"),
                  bg="#d32f2f", fg="white", width=18, relief="groove", activebackground="#b71c1c").pack(pady=8)

        self.update_liste()
    # ... (reste inchangé)

    def update_liste(self):
        self.lb.delete(0, tk.END)
        pharmaciens = list_pharmaciens()
        for u in pharmaciens:
            self.lb.insert(tk.END, f"{u.username} | {u.adresse} | {u.tel}")

    def ajouter(self):
        nom = self.entry_nom.get().strip()
        pwd = self.entry_pwd.get().strip()
        adresse = self.entry_adresse.get().strip()
        tel = self.entry_tel.get().strip()
        if not nom or not pwd or not adresse or not tel:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires.", parent=self.top)
            return
        try:
            add_user(nom, pwd, "pharmacien", adresse, tel)
            messagebox.showinfo("Succès", f"Pharmacien '{nom}' ajouté.", parent=self.top)
            self.entry_nom.delete(0, tk.END)
            self.entry_pwd.delete(0, tk.END)
            self.entry_adresse.delete(0, tk.END)
            self.entry_tel.delete(0, tk.END)
            self.update_liste()
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}", parent=self.top)

    def supprimer(self):
        selection = self.lb.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionner un pharmacien à supprimer.", parent=self.top)
            return
        info = self.lb.get(selection[0])
        nom = info.split(" | ")[0]
        if messagebox.askyesno("Confirmer", f"Supprimer le pharmacien '{nom}' ?", parent=self.top):
            delete_user(nom)
            self.update_liste()


class ProfilDialog:
    def __init__(self, parent, user):
        self.user = user
        self.top = tk.Toplevel(parent)
        self.top.title("Mon profil")
        self.top.geometry("400x250")
        self.top.config(bg="#f0f4f8")
        self.top.grab_set()

        row = 0
        frame = tk.Frame(self.top, bg="#f0f4f8")
        frame.pack(expand=True, fill="both", padx=24, pady=14)

        # Si medecin, champ modifiable pour username
        if user.role == "medecin":
            tk.Label(frame, text="Nom d'utilisateur :", font=("Arial", 11, "bold"), bg="#f0f4f8").grid(row=row, column=0, sticky="w")
            self.entry_username = tk.Entry(frame, font=("Arial", 11), bd=2, relief="groove")
            self.entry_username.insert(0, user.username)
            self.entry_username.grid(row=row, column=1, pady=2, sticky="ew")
            row += 1
        else:
            tk.Label(frame, text=f"Nom d'utilisateur : {user.username}", font=("Arial", 12, "bold"), bg="#f0f4f8", fg="#1976D2").grid(row=row, column=0, columnspan=2, pady=8)
            row += 1

        tk.Label(frame, text="Adresse :", font=("Arial", 11), bg="#f0f4f8").grid(row=row, column=0, sticky="w")
        self.entry_adresse = tk.Entry(frame, font=("Arial", 11), bd=2, relief="groove")
        self.entry_adresse.insert(0, user.adresse)
        self.entry_adresse.grid(row=row, column=1, pady=2, sticky="ew")
        row += 1

        tk.Label(frame, text="Téléphone :", font=("Arial", 11), bg="#f0f4f8").grid(row=row, column=0, sticky="w")
        self.entry_tel = tk.Entry(frame, font=("Arial", 11), bd=2, relief="groove")
        self.entry_tel.insert(0, user.tel)
        self.entry_tel.grid(row=row, column=1, pady=2, sticky="ew")
        row += 1

        tk.Label(frame, text="Nouveau mot de passe (laisser vide pour ne pas changer) :", font=("Arial", 10), bg="#f0f4f8").grid(row=row, column=0, columnspan=2, pady=(8,2), sticky="w")
        row += 1
        self.entry_pwd = tk.Entry(frame, show="*", font=("Arial", 11), bd=2, relief="groove")
        self.entry_pwd.grid(row=row, column=0, columnspan=2, pady=2, sticky="ew")
        row += 1

        tk.Button(frame, text="Enregistrer", command=self.enregistrer, font=("Arial", 11, "bold"),
                  bg="#1976D2", fg="white", width=15, relief="groove", activebackground="#1565C0").grid(row=row, column=0, columnspan=2, pady=14)

        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)

    def enregistrer(self):
        adresse = self.entry_adresse.get().strip()
        tel = self.entry_tel.get().strip()
        pwd = self.entry_pwd.get().strip()
        # Gestion de la modification du nom d'utilisateur pour le médecin
        if self.user.role == "medecin":
            new_username = self.entry_username.get().strip()
            if not new_username:
                messagebox.showerror("Erreur", "Le nom d'utilisateur est obligatoire.", parent=self.top)
                return
            if new_username != self.user.username and username_exists(new_username):
                messagebox.showerror("Erreur", "Nom d'utilisateur déjà utilisé.", parent=self.top)
                return
        else:
            new_username = None
        if not adresse or not tel:
            messagebox.showerror("Erreur", "Adresse et téléphone obligatoires.", parent=self.top)
            return
        update_user_infos(self.user.id, new_password=pwd if pwd else None, adresse=adresse, tel=tel, username=new_username)
        if new_username:
            self.user.username = new_username
        self.user.adresse = adresse
        self.user.tel = tel
        if pwd:
            self.user.password_hash = pwd  # Pour mémoire, mais pas utilisé directement
        messagebox.showinfo("Succès", "Profil mis à jour.", parent=self.top)
        self.top.destroy()

class AjoutMedicamentDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Ajouter un médicament")
        self.top.geometry("400x370")
        self.top.grab_set()
        self.result = None
        self.img_path = None

        tk.Label(self.top, text="Nom :", font=("Arial", 12)).pack(pady=4)
        self.entry_nom = tk.Entry(self.top, font=("Arial", 12))
        self.entry_nom.pack(pady=4)
        self.entry_nom.focus_set()

        tk.Label(self.top, text="Stock initial :", font=("Arial", 12)).pack(pady=4)
        self.entry_stock = tk.Entry(self.top, font=("Arial", 12))
        self.entry_stock.pack(pady=4)

        tk.Label(self.top, text="Prix unitaire (Ariary) :", font=("Arial", 12)).pack(pady=4)
        self.entry_prix = tk.Entry(self.top, font=("Arial", 12))
        self.entry_prix.pack(pady=4)

        # Label seuil d'alerte
        tk.Label(self.top, text="Seuil d'alerte (en boîtes, min 5, max 10) :", font=("Arial", 12)).pack(pady=4)
        self.entry_seuil = tk.Entry(self.top, font=("Arial", 12))
        self.entry_seuil.insert(0, "5")
        self.entry_seuil.pack(pady=4)

        self.img_label = tk.Label(self.top, text="Aucune image sélectionnée.", font=("Arial", 10), fg="#444")
        self.img_label.pack(pady=2)
        tk.Button(self.top, text="Choisir une image", command=self.choose_image).pack(pady=4)

        tk.Button(self.top, text="Valider", command=self.validate, font=("Arial", 12), bg="#1976D2", fg="white", width=12).pack(pady=10)

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        if path:
            self.img_path = path
            self.img_label.config(text=os.path.basename(path))

    def validate(self):
        nom = self.entry_nom.get()
        try:
            stock = int(self.entry_stock.get())
            prix = float(self.entry_prix.get())
            seuil = int(self.entry_seuil.get())
        except (TypeError, ValueError):
            messagebox.showerror("Erreur", "Entrée invalide.", parent=self.top)
            return
        if not nom:
            messagebox.showerror("Erreur", "Le nom est obligatoire.", parent=self.top)
            return
        if not (5 <= seuil <= 10):
            messagebox.showerror("Erreur", "Le seuil d'alerte doit être entre 5 et 10 boîtes.", parent=self.top)
            return
        self.result = (nom, stock, prix, seuil, self.img_path)
        self.top.destroy()

class VenteMedicamentDialog:
    def __init__(self, parent, med: Medicament):
        self.top = tk.Toplevel(parent)
        self.top.title("Vendre médicament")
        self.top.geometry("320x180")
        self.top.grab_set()
        self.result = None

        tk.Label(self.top, text=f"{med.nom}\nStock actuel : {med.stock}", font=("Arial", 12)).pack(pady=8)
        tk.Label(self.top, text="Quantité à vendre :", font=("Arial", 12)).pack(pady=4)
        self.entry_qte = tk.Entry(self.top, font=("Arial", 12))
        self.entry_qte.pack(pady=4)
        self.entry_qte.focus_set()

        tk.Button(self.top, text="Valider", command=self.validate, font=("Arial", 12), bg="#1976D2", fg="white", width=12).pack(pady=10)

    def validate(self):
        try:
            qte = int(self.entry_qte.get())
        except (ValueError, TypeError):
            messagebox.showerror("Erreur", "Entrée invalide.", parent=self.top)
            return
        self.result = qte
        self.top.destroy()

class SelectionEditDialog:
    def __init__(self, parent, app: PharmacieApp):
        self.app = app
        self.parent = parent
        self.meds = lister_medicaments()
        if not self.meds:
            messagebox.showinfo("Info", "Aucun médicament dans la base.", parent=parent)
            return

        self.top = tk.Toplevel(parent)
        self.top.title("Choisir un médicament à éditer")
        self.top.geometry("380x140")
        self.top.grab_set()

        tk.Label(self.top, text="Choisir le médicament :", font=("Arial", 12)).pack(pady=8)
        self.combo = ttk.Combobox(self.top, values=[m.nom for m in self.meds], state="readonly", font=("Arial", 12))
        self.combo.pack(pady=6)
        self.combo.current(0)
        tk.Button(self.top, text="Éditer", command=self.on_edit, font=("Arial", 12), bg="#1976D2", fg="white", width=12).pack(pady=10)

    def on_edit(self):
        i = self.combo.current()
        med = self.meds[i]
        self.top.destroy()
        EditMedicamentFormDialog(self.parent, self.app, med)

class EditMedicamentFormDialog:
    def __init__(self, parent, app: PharmacieApp, med: Medicament):
        self.app = app
        self.parent = parent
        self.med = med
        self.top = tk.Toplevel(parent)
        self.top.title("Éditer / Réapprovisionner")
        self.top.geometry("400x420")
        self.top.grab_set()
        self.img_path = med.image_path

        if med.image_path and os.path.exists(med.image_path):
            pil_img = Image.open(med.image_path).resize((64, 64))
            self.img_tk = ImageTk.PhotoImage(pil_img)
            self.img_label = tk.Label(self.top, image=self.img_tk)
            self.img_label.pack(pady=4)
        else:
            self.img_label = tk.Label(self.top, text="Pas d'image", font=("Arial", 10), fg="#444")
            self.img_label.pack(pady=4)
        tk.Button(self.top, text="Changer l'image", command=self.choose_image).pack(pady=4)

        tk.Label(self.top, text="Nom :", font=("Arial", 12)).pack(pady=2)
        self.entry_nom = tk.Entry(self.top, font=("Arial", 12))
        self.entry_nom.insert(0, med.nom)
        self.entry_nom.pack(pady=2)

        tk.Label(self.top, text=f"Stock actuel : {med.stock}", font=("Arial", 12)).pack(pady=2)
        self.stock_actuel = med.stock

        tk.Label(self.top, text="Quantité à ajouter :", font=("Arial", 12)).pack(pady=2)
        self.entry_rappr = tk.Entry(self.top, font=("Arial", 12))
        self.entry_rappr.insert(0, "0")
        self.entry_rappr.pack(pady=2)

        tk.Label(self.top, text="Prix unitaire (Ar) :", font=("Arial", 12)).pack(pady=2)
        self.entry_prix = tk.Entry(self.top, font=("Arial", 12))
        self.entry_prix.insert(0, str(med.prix))
        self.entry_prix.pack(pady=2)

        tk.Label(self.top, text="Seuil d'alerte (en boîtes, min 5, max 10) :", font=("Arial", 12)).pack(pady=2)
        self.entry_seuil = tk.Entry(self.top, font=("Arial", 12))
        self.entry_seuil.insert(0, str(med.seuil_alerte))
        self.entry_seuil.pack(pady=2)

        tk.Button(self.top, text="Valider", command=self.validate, font=("Arial", 12), bg="#1976D2", fg="white", width=12).pack(pady=12)

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        if path:
            self.img_path = path
            pil_img = Image.open(path).resize((64, 64))
            self.img_tk = ImageTk.PhotoImage(pil_img)
            self.img_label.configure(image=self.img_tk)
            self.img_label.image = self.img_tk

    def validate(self):
        nom = self.entry_nom.get()
        try:
            rapp = int(self.entry_rappr.get())
            prix = float(self.entry_prix.get())
            seuil = int(self.entry_seuil.get())
        except (TypeError, ValueError):
            messagebox.showerror("Erreur", "Entrée invalide.", parent=self.top)
            return
        if not nom:
            messagebox.showerror("Erreur", "Le nom est obligatoire.", parent=self.top)
            return
        if not (5 <= seuil <= 10):
            messagebox.showerror("Erreur", "Le seuil d'alerte doit être entre 5 et 10 boîtes.", parent=self.top)
            return
        total_stock = self.stock_actuel + rapp
        modifier_medicament(self.med.id, nom, total_stock, prix, seuil, self.img_path)
        self.app.update_liste()
        messagebox.showinfo("Succès", "Médicament modifié / réapprovisionné.", parent=self.top)
        self.top.destroy()

def run_app():
    init_db()
    root = tk.Tk()
    app = PharmacieApp(root)
    root.mainloop()