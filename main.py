from scraping.fdj_scraper import get_fdj_matches

if __name__ == "__main__":
    matches = get_fdj_matches(min_odds=1.2, max_odds=1.5)
    for m in matches:
        print(m)
