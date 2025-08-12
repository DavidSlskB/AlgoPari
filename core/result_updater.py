from __future__ import annotations
from datetime import datetime
from collections import defaultdict
from core.pending_manager import load_pending_matches, update_match_result
from scraping.fbref_scraper import get_fbref_results_for_date, normalize_name

def update_pending_results():
    today = datetime.now().date()
    matches = load_pending_matches()
    pending = [m for m in matches if m["status"] == "pending"]

    if not pending:
        print("✅ Aucun match en attente.")
        return

    # Grouper par date pour limiter les requêtes
    matches_by_date = defaultdict(list)
    for m in pending:
        try:
            match_dt = datetime.strptime(m["date"], "%d/%m").replace(year=today.year).date()
        except ValueError:
            continue
        if match_dt <= today:
            matches_by_date[m["date"]].append(m)

    updated_count = 0

    for date_str, matches_list in matches_by_date.items():
        print(f"\n📅 Traitement des matchs du {date_str}...")
        results_dict = get_fbref_results_for_date(date_str)

        for m in matches_list:
            if "-" not in m["titre"]:
                continue
            home_team, away_team = m["titre"].split("-", 1)

            key = (normalize_name(home_team), normalize_name(away_team))
            print(f"🔑 Recherche clé : {key} parmi {list(results_dict.keys())}")
            if key in results_dict:
                score, resultat = results_dict[key]
                update_match_result(m["titre"], m["date"], m["heure"], m["choix"], score, resultat)
                updated_count += 1
                print(f"✅ {m['titre']} {m['date']} → {score} ({resultat})")
            else:
                print(f"❌ Résultat non trouvé pour {m['titre']} {m['date']}")

    print(f"\nMises à jour terminées : {updated_count} matchs complétés.")
