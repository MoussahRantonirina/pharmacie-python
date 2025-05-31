import tkinter as tk
from tkinter import messagebox
from db.user_dao import verify_user

class LoginDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Pharmacie - Connexion")
        self.top.geometry("450x280")
        self.top.resizable(False, False)
        self.top.config(bg="#e3f2fd")
        self.top.grab_set()
        self.user = None

        frame = tk.Frame(self.top, bg="#e3f2fd")
        frame.pack(expand=True, fill="both", padx=24, pady=18)

        tk.Label(frame, text="Connexion", font=("Arial", 16, "bold"), bg="#e3f2fd", fg="#1976D2").pack(pady=(0, 18))
        tk.Label(frame, text="Nom d'utilisateur :", font=("Arial", 12), bg="#e3f2fd").pack(anchor="w")
        self.entry_username = tk.Entry(frame, font=("Arial", 12), bd=2, relief="groove")
        self.entry_username.pack(pady=4, fill="x")
        self.entry_username.focus_set()

        tk.Label(frame, text="Mot de passe :", font=("Arial", 12), bg="#e3f2fd").pack(anchor="w", pady=(8,0))
        self.entry_password = tk.Entry(frame, font=("Arial", 12), show="*", bd=2, relief="groove")
        self.entry_password.pack(pady=4, fill="x")

        tk.Button(frame, text="Se connecter", width=16, bg="#1976D2", fg="white", font=("Arial", 12, "bold"),
                  relief="groove", activebackground="#1565C0", command=self.login).pack(pady=18)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = verify_user(username, password)
        if user:
            self.user = user
            self.top.destroy()
        else:
            messagebox.showerror("Erreur", "Identifiants invalides.", parent=self.top)