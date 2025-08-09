# core/simulator.py

import os
import csv
from scraping.fdj_scraper import get_fdj_matches

def run_simulation(X, P, Y, Z):
    print(f"\n=== Simulation X={X} P={P} Y={Y} Z={Z} ===")

    matches = get_fdj_matches(min_odds=Y, max_odds=Z)

    if not matches:
        print("Aucun match trouvé pour cette configuration.")
        return

    # Créer le dossier results/<config>/
    dir_name = f"results/{X}-{P}-{Y}-{Z}"
    os.makedirs(dir_name, exist_ok=True)

    # Chemin du fichier CSV
    csv_path = os.path.join(dir_name, f"matches_{X}-{P}-{Y}-{Z}.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ligue", "titre", "date", "heure", "cote", "choix", "equipe"])
        for m in matches:
            writer.writerow([m.ligue, m.titre, m.date, m.heure, m.cote, m.choix, m.equipe])

    print(f"✅ {len(matches)} matchs enregistrés dans {csv_path}")
