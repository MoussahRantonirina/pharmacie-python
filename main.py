import tkinter as tk
from db.db_manager import init_db
from db.user_dao import init_user_table
from ui.login_dialog import LoginDialog
from ui.main_window import PharmacieApp

def run_app():
    init_db()
    init_user_table()
    root = tk.Tk()
    root.withdraw()  
    
    login = LoginDialog(root)
    root.wait_window(login.top)
    if login.user:
        root.deiconify()
        app = PharmacieApp(root, user=login.user)
        root.mainloop()
    else:
        root.destroy()

if __name__ == '__main__':
    run_app()