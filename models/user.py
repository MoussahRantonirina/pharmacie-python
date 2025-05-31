class User:
    def __init__(self, id, username, password_hash, role="pharmacien", adresse="", tel=""):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.adresse = adresse
        self.tel = tel