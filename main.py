# main.py
from core.config import generate_configurations
from core.simulator import run_scraping_pipeline
from core.result_updater import update_pending_results
from core.stats_generator import calculate_statistics
import sys
from datetime import datetime

sys.stdout = open(f"logs/log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8")

def main():
    print("\n=== Étape 1 : Scraping FDJ ===")
    configs = generate_configurations()
    for _, _, Y, Z in configs:
        run_scraping_pipeline(Y, Z)

    print("\n=== Étape 2 : Mise à jour des résultats FBRef ===")
    update_pending_results()

    print("\n=== Étape 3 : Calcul des statistiques et génération des graphiques ===")
    calculate_statistics(initial_balance=100, stake=1)

if __name__ == "__main__":
    main()
