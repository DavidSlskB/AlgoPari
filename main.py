from scraping.fbref_scraper import get_fbref_result

date = "01/08"
title = "schalke 04-Herta BSC"

score, result = get_fbref_result(date, title)
print(f"Score : {score}, Résultat : {result}")
