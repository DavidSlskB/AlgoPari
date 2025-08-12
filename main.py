# main.py
import os
import sys
from datetime import datetime
from pathlib import Path

from core.config import generate_configurations
from core.simulator import run_scraping_pipeline
from core.result_updater import update_pending_results
from core.stats_generator import calculate_statistics

def main():
    # Racine du projet (utile sur GitHub Actions)
    project_root = Path(__file__).resolve().parent
    results_dir = project_root / "results"
    logs_dir = project_root / "logs"

    # Création des dossiers si inexistants
    results_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    # Nom du log
    log_filename = logs_dir / f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    # Redirection des sorties vers le fichier log
    sys.stdout = open(log_filename, "w", encoding="utf-8")

    # Détection GitHub Actions
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("🚀 Exécution via GitHub Actions")
    else:
        print("💻 Exécution locale")

    print("\n=== Étape 1 : Scraping FDJ ===")
    # configs = generate_configurations()
    # for _, _, Y, Z in configs:
    #     run_scraping_pipeline(Y, Z)

    print("\n=== Étape 2 : Mise à jour des résultats FBRef ===")
    update_pending_results()

    print("\n=== Étape 3 : Calcul des statistiques et génération des graphiques ===")
    calculate_statistics(initial_balance=100, stake=1)

if __name__ == "__main__":
    main()
