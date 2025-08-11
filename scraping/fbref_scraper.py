from __future__ import annotations
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import unicodedata

# === Normalisation des noms ===
def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    return " ".join(name.lower().split())

def match_title_matches(a: str, b: str) -> bool:
    return normalize_name(a) == normalize_name(b)

# === Scraper tous les résultats d'une date ===
def get_fbref_results_for_date(date_str: str) -> dict:
    """
    Retourne un dict {(home, away): (score, resultat)}
    resultat = "1" | "2" | "X"
    """
    try:
        match_date = datetime.strptime(date_str, "%d/%m").replace(year=datetime.now().year)
    except ValueError:
        print(f"⚠️ Date invalide : {date_str}")
        return {}

    fbref_url = f"https://fbref.com/en/matches/{match_date.strftime('%Y-%m-%d')}"

    try:
        resp = requests.get(fbref_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Erreur FBRef ({fbref_url}) : {e}")
        return {}

    soup = BeautifulSoup(resp.content, "html.parser")
    results = {}

    for row in soup.select("table.stats_table tbody tr"):
        home_el = row.find("td", {"data-stat": "home_team"})
        away_el = row.find("td", {"data-stat": "away_team"})
        score_el = row.find("td", {"data-stat": "score"})

        if not home_el or not away_el:
            continue

        home_name = home_el.get_text(strip=True)
        away_name = away_el.get_text(strip=True)

        if not score_el:
            continue  # match pas encore joué

        score_txt = score_el.get_text(strip=True)
        if "-" not in score_txt:
            continue

        try:
            home_goals, away_goals = map(int, score_txt.split("-"))
        except ValueError:
            continue

        if home_goals > away_goals:
            resultat = "1"
        elif away_goals > home_goals:
            resultat = "2"
        else:
            resultat = "X"

        results[(normalize_name(home_name), normalize_name(away_name))] = (score_txt, resultat)

    return results
