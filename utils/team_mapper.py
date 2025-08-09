# utils/team_mapper.py

import json

with open("data/team_mapping.json", "r", encoding="utf-8") as f:
    TEAM_MAPPING = json.load(f)

def change_team_names(raw_title: str, ligue: str) -> str:
    """
    Transforme un titre 'juventus turin-naples' en 'juventus-napoli' selon le mapping.
    """
    raw_title = raw_title.lower()
    if "-" not in raw_title:
        return raw_title  # sécurité

    team1, team2 = [t.strip() for t in raw_title.split("-")]

    mapping = TEAM_MAPPING.get(ligue, {})
    team1_clean = mapping.get(team1, team1)
    team2_clean = mapping.get(team2, team2)

    return f"{team1_clean}-{team2_clean}"
