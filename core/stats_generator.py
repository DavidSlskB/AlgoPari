# core/stats_generator.py
from __future__ import annotations
import csv
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt
from core.pending_manager import load_pending_matches

def calculate_statistics(initial_balance: float, stake: float):
    matches = load_pending_matches()
    done_matches = [m for m in matches if m["status"] == "done"]

    if not done_matches:
        print("⚠️ Aucun match terminé trouvé.")
        return

    # Tri des matchs par date puis heure
    done_matches.sort(key=lambda m: (
        datetime.strptime(m["date"], "%d/%m"),
        m["heure"]
    ))

    balance = initial_balance
    wins = 0
    losses = 0
    league_stats: Dict[str, Dict[str, float]] = {}

    balance_history = [initial_balance]
    match_labels = ["Initiale"]

    for m in done_matches:
        cote = float(m["cote"])
        if m["resultat"] == m["choix"]:
            balance += stake * (cote - 1)
            wins += 1
            result_value = "win"
        else:
            balance -= stake
            losses += 1
            result_value = "loss"

        balance_history.append(balance)
        match_labels.append(f"{m['titre']} {m['date']}")

        ligue = m["ligue"]
        if ligue not in league_stats:
            league_stats[ligue] = {"matches": 0, "wins": 0, "losses": 0}
        league_stats[ligue]["matches"] += 1
        league_stats[ligue][result_value + "s"] = league_stats[ligue].get(result_value + "s", 0) + 1

    total_matches = wins + losses
    win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
    roi = ((balance - initial_balance) / initial_balance * 100)

    # Rapport texte
    Path("results").mkdir(exist_ok=True)
    report_path = Path("results/statistics_report.txt")
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"=== Statistiques Globales ===\n")
        f.write(f"Cagnotte initiale : {initial_balance:.2f}€\n")
        f.write(f"Cagnotte finale   : {balance:.2f}€\n")
        f.write(f"Bénéfice net      : {balance - initial_balance:.2f}€\n")
        f.write(f"ROI               : {roi:.2f}%\n")
        f.write(f"Matchs joués      : {total_matches}\n")
        f.write(f"Victoires         : {wins} ({win_rate:.2f}%)\n")
        f.write(f"Défaites          : {losses}\n\n")

        f.write(f"=== Statistiques par Ligue ===\n")
        for ligue, stats in league_stats.items():
            wr = (stats["wins"] / stats["matches"] * 100) if stats["matches"] > 0 else 0
            f.write(f"{ligue}: {stats['wins']} victoires / {stats['matches']} matchs ({wr:.2f}%)\n")

    print(f"✅ Rapport texte généré : {report_path}")

    # CSV résumé
    csv_path = Path("results/statistics_summary.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Ligue", "Matchs", "Victoires", "Défaites", "WinRate (%)"])
        for ligue, stats in league_stats.items():
            wr = (stats["wins"] / stats["matches"] * 100) if stats["matches"] > 0 else 0
            writer.writerow([ligue, stats["matches"], stats["wins"], stats["losses"], f"{wr:.2f}"])

    print(f"✅ Résumé CSV généré : {csv_path}")

    # Graphiques
    _generate_graphics(balance, initial_balance, league_stats, balance_history, match_labels)

def _generate_graphics(final_balance, initial_balance, league_stats, balance_history=None, match_labels=None):
    Path("results/graphs").mkdir(parents=True, exist_ok=True)

    # Graphique 1 : évolution match par match
    if balance_history and match_labels:
        plt.figure(figsize=(10,5))
        plt.plot(range(len(balance_history)), balance_history, marker="o")
        plt.xticks(range(len(balance_history)), match_labels, rotation=45, ha="right", fontsize=8)
        plt.ylabel("€")
        plt.title("Évolution de la Cagnotte Match par Match")
        plt.tight_layout()
        plt.savefig("results/graphs/balance_history.png")
        plt.close()

    # Graphique 2 : Répartition victoires/défaites par ligue
    leagues = list(league_stats.keys())
    wins = [stats["wins"] for stats in league_stats.values()]
    losses = [stats["losses"] for stats in league_stats.values()]

    plt.figure(figsize=(8,5))
    bar_width = 0.35
    x = range(len(leagues))
    plt.bar(x, wins, width=bar_width, label="Victoires", color="green")
    plt.bar([i + bar_width for i in x], losses, width=bar_width, label="Défaites", color="red")
    plt.xticks([i + bar_width/2 for i in x], leagues, rotation=45)
    plt.ylabel("Nombre de matchs")
    plt.title("Victoires/Défaites par Ligue")
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/graphs/wins_losses_by_league.png")
    plt.close()

    # Graphique 3 : Win rate par ligue
    win_rates = [(stats["wins"] / stats["matches"] * 100) if stats["matches"] > 0 else 0 for stats in league_stats.values()]
    plt.figure(figsize=(8,5))
    plt.bar(leagues, win_rates, color="blue")
    plt.ylabel("WinRate (%)")
    plt.title("Taux de Victoire par Ligue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("results/graphs/winrate_by_league.png")
    plt.close()

    # Graphique 4 : balance initiale/finale
    balances = [initial_balance, final_balance]
    plt.figure(figsize=(6,4))
    plt.plot(["Initiale", "Finale"], balances, marker="o")
    plt.title("Évolution globale de la Cagnotte")
    plt.ylabel("€")
    plt.savefig("results/graphs/balance_evolution.png")
    plt.close()

    print("📊 Graphiques générés dans results/graphs/")