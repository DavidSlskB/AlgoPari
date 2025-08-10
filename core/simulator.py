# core/simulator.py
from __future__ import annotations
from datetime import datetime

from scraping.fdj_scraper import get_fdj_matches
from core.pending_manager import add_new_pending_matches

def run_scraping_pipeline(Y, Z, leagues=None):
    """
    Scrape FDJ avec plage de cotes [Y, Z], ajoute les nouveaux matchs
    dans pending_matches.csv.
    """
    print(f"\n=== Scraping FDJ pour Y={Y}, Z={Z} ===")
    matches, counts = get_fdj_matches(min_odds=Y, max_odds=Z, leagues=leagues)

    if not matches:
        print("Aucun match trouvé.")
        return

    added_count = add_new_pending_matches(matches)
    print(f"✅ {added_count} nouveaux matchs ajoutés à pending_matches.csv")
    print("→ Résumé par ligue :")
    for ligue, cnt in counts.items():
        print(f"   - {ligue}: {cnt} matchs trouvés")
