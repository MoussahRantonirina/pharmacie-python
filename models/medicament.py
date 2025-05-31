class Medicament:
    def __init__(self, id, nom, stock, prix, seuil_alerte=10, image_path=None):
        self.id = id
        self.nom = nom
        self.stock = stock
        self.prix = prix
        self.seuil_alerte = seuil_alerte
        self.image_path = image_path

    def __str__(self):
        return f"{self.nom} (Stock: {self.stock}, Prix: {self.prix} Ar)"