# core/result_updater.py
from __future__ import annotations
from datetime import datetime
from core.pending_manager import load_pending_matches, update_match_result
from scraping.fbref_scraper import get_fbref_result

def update_pending_results():
    today = datetime.now().date()
    matches = load_pending_matches()
    pending = [m for m in matches if m["status"] == "pending"]

    if not pending:
        print("✅ Aucun match en attente.")
        return

    updated_count = 0
    for m in pending:
        # Vérifier si le match est passé
        try:
            match_dt = datetime.strptime(m["date"], "%d/%m").replace(year=today.year).date()
        except ValueError:
            continue

        if match_dt > today:
            continue  # match futur → on saute

        # Déterminer home/away depuis le titre
        if "-" in m["titre"]:
            home_team, away_team = m["titre"].split("-", 1)
        else:
            continue

        score, resultat = get_fbref_result(m["ligue"], m["date"], home_team, away_team)
        if score:
            update_match_result(m["titre"], m["date"], m["heure"], m["choix"], score, resultat)
            updated_count += 1
            print(f"✅ {m['titre']} {m['date']} → {score} ({resultat})")
        else:
            print(f"❌ Résultat non trouvé pour {m['titre']} {m['date']}")

    print(f"\nMises à jour terminées : {updated_count} matchs complétés.")
