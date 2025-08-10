# core/pending_manager.py
from __future__ import annotations
import csv
from pathlib import Path
from typing import List
from models.match import Match

PENDING_FILE = Path("data/pending_matches.csv")

def load_pending_matches() -> List[dict]:
    """Charge tous les matchs existants dans pending_matches.csv"""
    if not PENDING_FILE.exists():
        return []
    with PENDING_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_pending_matches(matches: List[dict]):
    """Écrit la liste complète des matchs dans pending_matches.csv"""
    with PENDING_FILE.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["ligue", "titre", "date", "heure", "cote", "choix", "equipe", "resultat", "score", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matches)

def add_new_pending_matches(new_matches: List[Match]) -> int:
    """
    Ajoute les nouveaux matchs FDJ qui ne sont pas déjà dans pending_matches.csv.
    Retourne le nombre de matchs ajoutés.
    """
    existing = load_pending_matches()
    existing_keys = { (m["titre"], m["date"], m["heure"], m["choix"]) for m in existing }

    added = 0
    for m in new_matches:
        key = (m.titre, m.date, m.heure, m.choix)
        if key not in existing_keys:
            existing.append({
                "ligue": m.ligue,
                "titre": m.titre,
                "date": m.date,
                "heure": m.heure,
                "cote": str(m.cote),
                "choix": m.choix,
                "equipe": m.equipe,
                "resultat": "",
                "score": "",
                "status": "pending"
            })
            existing_keys.add(key)
            added += 1

    save_pending_matches(existing)
    return added

def update_match_result(titre: str, date: str, heure: str, choix: str, score: str, resultat: str):
    """
    Met à jour le résultat d'un match dans pending_matches.csv
    """
    matches = load_pending_matches()
    for m in matches:
        if m["titre"] == titre and m["date"] == date and m["heure"] == heure and m["choix"] == choix:
            m["score"] = score or ""
            m["resultat"] = resultat or ""
            if score and resultat:
                m["status"] = "done"
            break
    save_pending_matches(matches)
