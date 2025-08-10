# scraping/fbref_scraper.py
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import unicodedata

# === Outils pour normaliser les noms d'équipes ===
def normalize_name(name: str) -> str:
    """
    Supprime accents, passe en minuscule, enlève espaces multiples.
    """
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    return " ".join(name.lower().split())

def match_title_matches(a: str, b: str) -> bool:
    """
    Vérifie si deux noms d'équipes normalisés correspondent
    """
    return normalize_name(a) == normalize_name(b)

# === Scraper FBRef ===
def get_fbref_result(ligue: str, date_str: str, home_team: str, away_team: str):
    """
    Retourne (score, resultat) pour un match FBRef donné par ligue, date et équipes.
    resultat = "1" | "2" | "X"
    """
    # Charger config ligues FBRef
    cfg_path = Path("data/config.json")
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    fbref_urls = config.get("fbref_urls", {})
    url = fbref_urls.get(ligue)
    if not url:
        print(f"⚠️ Pas d'URL FBRef pour {ligue}")
        return None, None

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Erreur FBRef {ligue}: {e}")
        return None, None

    soup = BeautifulSoup(resp.content, "html.parser")
    rows = soup.select("table.stats_table tbody tr")

    for row in rows:
        date_el = row.find("td", {"data-stat": "date"})
        if not date_el:
            continue
        match_date = date_el.get_text(strip=True)
        # FBRef format "2024-08-15" → on le compare à date_str
        try:
            match_dt = datetime.strptime(match_date, "%Y-%m-%d").date()
        except ValueError:
            continue

        try:
            target_dt = datetime.strptime(date_str, "%d/%m").replace(year=match_dt.year).date()
        except ValueError:
            continue

        if match_dt != target_dt:
            continue

        # Récup équipes
        home_el = row.find("td", {"data-stat": "home_team"})
        away_el = row.find("td", {"data-stat": "away_team"})
        if not home_el or not away_el:
            continue

        home_name = home_el.get_text(strip=True)
        away_name = away_el.get_text(strip=True)

        if match_title_matches(home_team, home_name) and match_title_matches(away_team, away_name):
            # Récup score
            score_el = row.find("td", {"data-stat": "score"})
            if not score_el:
                return None, None
            score_txt = score_el.get_text(strip=True)
            if "-" not in score_txt:
                return None, None

            try:
                home_goals, away_goals = map(int, score_txt.split("-"))
            except ValueError:
                return None, None

            if home_goals > away_goals:
                return score_txt, "1"
            elif away_goals > home_goals:
                return score_txt, "2"
            else:
                return score_txt, "X"

    return None, None
