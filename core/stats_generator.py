# core/stats_generator.py
from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, Tuple
import matplotlib.pyplot as plt
from core.pending_manager import load_pending_matches
from core.config import generate_configurations
from datetime import datetime

def calculate_statistics(initial_balance: float, stake: float):
    matches = load_pending_matches()
    done_matches = [m for m in matches if m["status"] == "done"]

    if not done_matches:
        print("⚠️ Aucun match terminé trouvé.")
        return

    # Tri par date/heure
    done_matches.sort(key=lambda m: (
        datetime.strptime(m["date"], "%d/%m"),
        m["heure"]
    ))

    # === Stats globales ===
    balance = initial_balance
    wins = 0
    losses = 0
    league_stats: Dict[str, Dict[str, float]] = {}

    balance_history = [initial_balance]
    match_labels = ["Initiale"]

    # === Stats par plage de cotes ===
    configs = generate_configurations()
    # dict { (Y, Z): {"matches":0, "wins":0, "losses":0, "profit":0.0} }
    odds_stats: Dict[Tuple[float, float], Dict[str, float]] = {
        (Y, Z): {"matches": 0, "wins": 0, "losses": 0, "profit": 0.0}
        for _, _, Y, Z in configs
    }

    for m in done_matches:
        cote = float(m["cote"])
        if m["resultat"] == m["choix"]:
            balance += stake * (cote - 1)
            wins += 1
            result_value = "win"
            profit_change = stake * (cote - 1)
        else:
            balance -= stake
            losses += 1
            result_value = "loss"
            profit_change = -stake

        balance_history.append(balance)
        match_labels.append(f"{m['titre']} {m['date']}")

        # Stats par ligue
        ligue = m["ligue"]
        if ligue not in league_stats:
            league_stats[ligue] = {"matches": 0, "wins": 0, "losses": 0}
        league_stats[ligue]["matches"] += 1
        league_stats[ligue][result_value + "s"] = league_stats[ligue].get(result_value + "s", 0) + 1

        # Stats par plage de cotes
        for (Y, Z) in odds_stats.keys():
            if Y <= cote <= Z:
                odds_stats[(Y, Z)]["matches"] += 1
                if result_value == "win":
                    odds_stats[(Y, Z)]["wins"] += 1
                else:
                    odds_stats[(Y, Z)]["losses"] += 1
                odds_stats[(Y, Z)]["profit"] += profit_change
                break


    total_matches = wins + losses
    win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
    roi = ((balance - initial_balance) / initial_balance * 100)

    Path("results").mkdir(exist_ok=True)

    # Rapport texte
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

        f.write("\n=== Statistiques par plage de cotes ===\n")
        for (Y, Z), stats in sorted(odds_stats.items()):
            if stats["matches"] == 0:
                continue
            wr = (stats["wins"] / stats["matches"] * 100)
            roi_range = (stats["profit"] / (stake * stats["matches"])) * 100
            f.write(f"{Y:.2f} - {Z:.2f} : {stats['wins']} victoires / {stats['matches']} matchs "
                    f"({wr:.2f}%) | ROI: {roi_range:.2f}%\n")

    print(f"✅ Rapport texte généré : {report_path}")

    # CSV résumé
    csv_path = Path("results/statistics_summary.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Clé", "Matchs", "Victoires", "Défaites", "WinRate (%)", "ROI (%)"])
        for ligue, stats in league_stats.items():
            wr = (stats["wins"] / stats["matches"] * 100) if stats["matches"] > 0 else 0
            writer.writerow(["Ligue", ligue, stats["matches"], stats["wins"], stats["losses"], f"{wr:.2f}", ""])

        for (Y, Z), stats in sorted(odds_stats.items()):
            if stats["matches"] == 0:
                continue
            wr = (stats["wins"] / stats["matches"] * 100)
            roi_range = (stats["profit"] / (stake * stats["matches"])) * 100
            writer.writerow(["Plage de cotes", f"{Y:.2f}-{Z:.2f}", stats["matches"], stats["wins"], stats["losses"], f"{wr:.2f}", f"{roi_range:.2f}"])

    print(f"✅ Résumé CSV généré : {csv_path}")

    # Graphiques
    _generate_graphics(balance, initial_balance, league_stats, odds_stats, balance_history, match_labels)

def _generate_graphics(final_balance, initial_balance, league_stats, odds_stats, balance_history=None, match_labels=None):
    Path("results/graphs").mkdir(parents=True, exist_ok=True)

    # Évolution match par match
    if balance_history and match_labels:
        plt.figure(figsize=(10,5))
        plt.plot(range(len(balance_history)), balance_history, marker="o")
        plt.xticks(range(len(balance_history)), match_labels, rotation=45, ha="right", fontsize=8)
        plt.ylabel("€")
        plt.title("Évolution de la Cagnotte Match par Match")
        plt.tight_layout()
        plt.savefig("results/graphs/balance_history.png")
        plt.close()

    # V/D par ligue
    leagues = list(league_stats.keys())
    wins = [stats["wins"] for stats in league_stats.values()]
    losses = [stats["losses"] for stats in league_stats.values()]

    if leagues:
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

    # Win rate par plage de cotes
    ranges = [f"{Y:.2f}-{Z:.2f}" for (Y,Z) in odds_stats.keys() if odds_stats[(Y,Z)]["matches"] > 0]
    win_rates = [(stats["wins"] / stats["matches"] * 100) if stats["matches"] > 0 else 0
                 for stats in odds_stats.values() if stats["matches"] > 0]

    if ranges:
        plt.figure(figsize=(10,5))
        plt.bar(ranges, win_rates, color="blue")
        plt.ylabel("WinRate (%)")
        plt.title("Taux de Victoire par plage de cotes")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("results/graphs/winrate_by_odds_range.png")
        plt.close()

    # ROI par plage de cotes
    rois = [((stats["profit"] / (stats["matches"])) / 1) * 100 / 1  # en %
            for stats in odds_stats.values() if stats["matches"] > 0]
    if ranges:
        plt.figure(figsize=(10,5))
        plt.bar(ranges, rois, color="orange")
        plt.ylabel("ROI (%)")
        plt.title("ROI par plage de cotes")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("results/graphs/roi_by_odds_range.png")
        plt.close()

    # Balance initiale/finale
    balances = [initial_balance, final_balance]
    plt.figure(figsize=(6,4))
    plt.plot(["Initiale", "Finale"], balances, marker="o")
    plt.title("Évolution globale de la Cagnotte")
    plt.ylabel("€")
    plt.savefig("results/graphs/balance_evolution.png")
    plt.close()

    print("📊 Graphiques générés dans results/graphs/")
