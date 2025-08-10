# core/simulator.py
from __future__ import annotations
import os
import csv
import json
from datetime import datetime
from pathlib import Path

from scraping.fdj_scraper import get_fdj_matches

def _safe_dirname(X, P, Y, Z) -> str:
    # format lisible et portable pour des dossiers
    return f"{int(X)}-{int(P)}-{Y:.2f}-{Z:.2f}".replace(".", "_")

def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def _write_csv(path: Path, matches):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ligue", "titre", "date", "heure", "cote", "choix", "equipe"])
        for m in matches:
            writer.writerow([m.ligue, m.titre, m.date, m.heure, m.cote, m.choix, m.equipe])

def run_simulation(X, P, Y, Z, *, base_results_dir: str = "results",
                   overwrite: bool = True, leagues: list | None = None):
    """
    Récupère les matchs FDJ (filtrés par Y-Z) et sauvegarde les résultats:
     - CSV matches
     - metadata.json (params + counts + timestamp)

    Options:
      - overwrite: si False et le CSV existe, on saute l'écriture
      - leagues: liste optionnelle pour restreindre les ligues scrappées
    """
    print(f"\n=== Simulation X={X} P={P} Y={Y} Z={Z} ===")

    dir_name = _safe_dirname(X, P, Y, Z)
    results_path = Path(base_results_dir) / dir_name
    _ensure_dir(results_path)

    csv_path = results_path / f"matches_{dir_name}.csv"
    metadata_path = results_path / "metadata.json"

    # Récupération des matchs
    matches, counts = get_fdj_matches(min_odds=Y, max_odds=Z, leagues=leagues)

    if not matches:
        print("Aucun match trouvé pour cette configuration.")
        # on écrit malgré tout un metadata minimal
        metadata = {
            "X": X, "P": P, "Y": Y, "Z": Z,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "matches_found": 0,
            "counts": counts
        }
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return

    # si existant et overwrite False => skip
    if csv_path.exists() and not overwrite:
        print(f"Le fichier {csv_path} existe déjà et overwrite=False -> skip")
    else:
        _write_csv(csv_path, matches)
        print(f"✅ {len(matches)} matchs enregistrés dans {csv_path}")

    # write metadata
    metadata = {
        "X": X, "P": P, "Y": Y, "Z": Z,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "matches_found": len(matches),
        "counts": counts
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"ℹ️ Metadata enregistré dans {metadata_path}")

    # résumé console par ligue
    print("→ Résumé par ligue :")
    for ligue, cnt in counts.items():
        print(f"   - {ligue}: {cnt} matchs")
