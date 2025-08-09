class Match:
    def __init__(self, ligue, titre, date, heure, cote, choix, equipe):
        self.ligue = ligue      # Ligue 1
        self.titre = titre      # Lille-Paris
        self.date = date        # dd/mm
        self.heure = heure      # HH:MM
        self.cote = float(cote) # 1.22
        self.choix = choix      # 1 ou 2
        self.equipe = equipe    # Lille

    def __str__(self):
        return f"Match - {self.ligue}, {self.titre}, {self.date} {self.heure} : {self.choix} - {self.cote} - {self.equipe}"
