class Wallet:
    def __init__(self, somme_initiale):
        self.cagnotte = somme_initiale
        self.historique = []
    
    def __str__(self):
        return f"started with {self.historique[0]}, nom get {self.cagnotte}"
    
    def get_cagnotte(self):
        return self.cagnotte
    
    def get_historique(self):
        return self.historique
