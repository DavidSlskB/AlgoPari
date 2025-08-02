from models.wallet import Wallet
from models.match import Match

def run_simulation(X, P, Y, Z):
    print(f"Lancement de la simulation avec X={X}, P={P}, Y={Y}, Z={Z}")
    wallet = Wallet(X)

    # Simule quelques matchs fictifs (à remplacer plus tard par du scraping)
    matchs = [
        Match("Serie A", "juventus-napoli", "01/08", "18:00", 1.35, "1", "juventus"),
        Match("Premier League", "chelsea-arsenal", "01/08", "20:00", 1.45, "2", "arsenal"),
    ]

    for match in matchs:
        if Y <= match.cote <= Z and wallet.can_bet(P):
            wallet.bet(P)
            # Résultat fictif : tous les paris sont gagnants ici
            gain = P * match.cote
            wallet.win(gain)
    
    print(f"Solde final : {wallet.get_balance()}€")