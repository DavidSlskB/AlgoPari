# scraping/fdj_scraper.py
from __future__ import annotations
import json
import time
from typing import List, Tuple, Dict
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from utils.team_mapper import change_team_names
from models.match import Match

# --- HTTP session with retries & headers ---
def create_requests_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1,
                    status_forcelist=(429, 500, 502, 503, 504),
                    allowed_methods=frozenset(["GET", "POST"]))
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    # User-Agent classique de navigateur pour réduire les risques de blocage
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    })
    return session

# --- Main scraper ---
def get_fdj_matches(min_odds: float, max_odds: float,
                    leagues: List[str] | None = None,
                    sleep_between_requests: float = 0.3) -> Tuple[List[Match], Dict[str,int]]:
    """
    Scrape FDJ pages declared in data/config.json.
    Returns (matches_list, counts_by_league).

    - min_odds, max_odds: filtre des cotes
    - leagues: liste optionnelle de ligues à scraper (None => toutes)
    - sleep_between_requests: délai entre requêtes pour politesse
    """
    # charger config
    cfg_path = Path("data/config.json")
    if not cfg_path.exists():
        raise FileNotFoundError("data/config.json introuvable")

    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    fdj_urls = config.get("fdj_urls", {})
    championships = config.get("championships", list(fdj_urls.keys()))

    # si on fournit une sous-liste, on filtre
    if leagues:
        championships = [c for c in championships if c in leagues]

    session = create_requests_session()
    matches_list: List[Match] = []
    seen = set()
    counts: Dict[str,int] = {c: 0 for c in championships}

    for ligue in championships:
        url = fdj_urls.get(ligue)
        if not url:
            print(f"⚠️ URL introuvable pour la ligue {ligue} dans config.json")
            continue

        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ Erreur requête FDJ {ligue}: {e}")
            continue

        soup = BeautifulSoup(resp.content, "html.parser")
        matchs_html = soup.find_all(class_="match-home")

        for match_html in matchs_html:
            try:
                raw_title_el = match_html.find("div", class_="match-home_title")
                if raw_title_el is None:
                    continue
                raw_title = raw_title_el.get_text().strip().lower()

                date_heure_el = match_html.find("p", attrs={"data": "app-offers|marketTypeOffre"})
                date_heure = date_heure_el.get_text() if date_heure_el else ""
                date = date_heure[-12:-7].strip() if len(date_heure) >= 12 else ""
                heure = date_heure[-6:-1].strip() if len(date_heure) >= 6 else ""

                odds1_el = match_html.find("span", attrs={"data": "app-market-template|outcome-1|outcomeButton_value"})
                odds2_el = match_html.find("span", attrs={"data": "app-market-template|outcome-2|outcomeButton_value"})
                if odds1_el is None and odds2_el is None:
                    continue

                # convert cotes en float si possible
                odds1 = float(odds1_el.get_text().replace(",", ".")) if odds1_el else None
                odds2 = float(odds2_el.get_text().replace(",", ".")) if odds2_el else None

                # normaliser le titre avec le mapping
                cleaned_title = change_team_names(raw_title, ligue).strip().lower()

                # test et ajout (1 ou 2)
                if odds1 is not None and min_odds <= odds1 <= max_odds:
                    team1 = cleaned_title.split("-")[0].strip()
                    key = f"{cleaned_title}|{date}|{heure}|1"
                    if key not in seen:
                        matches_list.append(Match(ligue, cleaned_title, date, heure, odds1, "1", team1))
                        seen.add(key)
                        counts[ligue] = counts.get(ligue, 0) + 1

                if odds2 is not None and min_odds <= odds2 <= max_odds:
                    # garde la seconde partie après le '-'
                    parts = cleaned_title.split("-", 1)
                    team2 = parts[1].strip() if len(parts) > 1 else ""
                    key = f"{cleaned_title}|{date}|{heure}|2"
                    if key not in seen:
                        matches_list.append(Match(ligue, cleaned_title, date, heure, odds2, "2", team2))
                        seen.add(key)
                        counts[ligue] = counts.get(ligue, 0) + 1

            except Exception as e:
                print(f"⚠️ Erreur parsing FDJ ({ligue}) : {e}")
                continue

        # pause légère pour politesse
        time.sleep(sleep_between_requests)

    return matches_list, counts
