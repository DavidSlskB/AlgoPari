# scraping/fbref_scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_fbref_result(date_str, title):
    """
    Récupère le résultat d'un match depuis FBRef.
    
    :param date_str: date du match au format "dd/mm"
    :param title: titre normalisé du match, ex: "juventus-napoli"
    :return: tuple (score_str, resultat) 
             score_str ex. "2-1", resultat = "1", "N", ou "2"
    """
    # Transformer la date en éléments pour URL FBRef
    day, month = date_str.split("/")
    year = datetime.now().year
    fbref_url = f"https://fbref.com/fr/matchs/{year}-{month}-{day}"

    try:
        response = requests.get(fbref_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur connexion FBRef pour {date_str} : {e}")
        return None, None

    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("div", class_="table_wrapper tabbed")

    for table in tables:
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            home_team = row.find("td", {"data-stat": "home_team"})
            away_team = row.find("td", {"data-stat": "away_team"})
            score_cell = row.find("td", {"data-stat": "score"})

            if home_team and away_team and score_cell:
                match_name = f"{home_team.get_text().lower()}-{away_team.get_text().lower()}"
                if match_name == title:
                    score_str = score_cell.get_text().replace("–", "-")
                    try:
                        home_goals, away_goals = map(int, score_str.split("-"))
                    except ValueError:
                        return None, None  # score non disponible

                    if home_goals > away_goals:
                        return score_str, "1"
                    elif home_goals == away_goals:
                        return score_str, "N"
                    else:
                        return score_str, "2"

    print(f"Match {title} non trouvé sur FBRef le {date_str}")
    return None, None
