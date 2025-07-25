class Match:
    def __init__(self, ligue, titre, date, heure, un_n_deux, cote, equipe):
        self.ligue = ligue
        self.titre = titre
        self.date = date
        self.heure = heure
        self.un_n_deux = un_n_deux
        self.cote = cote
        self.equipe = equipe

    def __str__(self):
        return f"{self.ligue}, {self.titre}, {self.date} {self.heure} : {self.un_n_deux} - {self.cote} - {self.equipe}"
