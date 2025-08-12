from __future__ import annotations
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import unicodedata
import re

# === Normalisation des noms ===
def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")  # supprime accents
    name = re.sub(r"\s+", " ", name)  # espaces multiples → simple espace
    return name.strip().lower()

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
    print(f"🌐 Scraping FBRef : {fbref_url}")

    try:
        resp = requests.get(fbref_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Erreur FBRef ({fbref_url}) : {e}")
        return {}

    soup = BeautifulSoup(resp.content, "html.parser")
    results = {}

    rows = soup.select("table.stats_table tbody tr")
    print(f"🔍 {len(rows)} lignes trouvées dans les tables de la page")

    for row in rows:
        home_el = row.find("td", {"data-stat": "home_team"})
        away_el = row.find("td", {"data-stat": "away_team"})
        score_el = row.find("td", {"data-stat": "score"})

        if not home_el or not away_el:
            continue

        home_name = home_el.get_text(strip=True)
        away_name = away_el.get_text(strip=True)

        # Nettoyage supplémentaire
        home_name = home_name.replace("\u00a0", " ")
        away_name = away_name.replace("\u00a0", " ")

        if not score_el:
            continue

        score_txt = score_el.get_text(strip=True).replace("\u2013", "-")  # en-dash → tiret
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

        key = (normalize_name(home_name), normalize_name(away_name))
        results[key] = (score_txt, resultat)

    print(f"✅ {len(results)} matchs trouvés : {list(results.keys())}")
    return results
