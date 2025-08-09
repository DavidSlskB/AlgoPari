# scraping/fdj_scraper.py

import json
import requests
from bs4 import BeautifulSoup
from utils.team_mapper import change_team_names
from models.match import Match

def get_fdj_matches(min_odds, max_odds):
    """
    Récupère les matchs disponibles sur FDJ pour toutes les ligues
    et retourne une liste d'objets Match filtrés par cote.
    """
    # Charger config.json
    with open("data/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    fdj_urls = config["fdj_urls"]
    championships = config["championships"]

    matches_list = []

    for ligue in championships:
        url = fdj_urls[ligue]
        print(f"Scraping {ligue}...")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération de {ligue}: {e}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        matchs_html = soup.find_all(class_="match-home")

        for match_html in matchs_html:
            try:
                raw_title = match_html.find(
                    "div", class_="match-home_title"
                ).get_text().strip().lower()

                date_heure = match_html.find(
                    "p", attrs={"data": "app-offers|marketTypeOffre"}
                ).get_text()

                date = date_heure[-12:-7]  # extraction "jj/mm"
                heure = date_heure[-6:-1]  # extraction "HH:MM"

                odds1 = match_html.find(
                    "span",
                    attrs={"data": "app-market-template|outcome-1|outcomeButton_value"},
                ).get_text().replace(",", ".")
                odds2 = match_html.find(
                    "span",
                    attrs={"data": "app-market-template|outcome-2|outcomeButton_value"},
                ).get_text().replace(",", ".")

                odds1 = float(odds1)
                odds2 = float(odds2)

                cleaned_title = change_team_names(raw_title, ligue)

                # Pari sur équipe 1 si la cote est dans la plage
                if min_odds <= odds1 <= max_odds:
                    team1 = cleaned_title.split("-")[0]
                    matches_list.append(
                        Match(ligue, cleaned_title, date, heure, odds1, "1", team1)
                    )

                # Pari sur équipe 2 si la cote est dans la plage
                if min_odds <= odds2 <= max_odds:
                    team2 = cleaned_title.split("-")[1]
                    matches_list.append(
                        Match(ligue, cleaned_title, date, heure, odds2, "2", team2)
                    )

            except Exception as e:
                print(f"Erreur parsing match : {e}")

    return matches_list
