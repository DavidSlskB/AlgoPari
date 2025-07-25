# AlgoPari (Version initiale)

**Simulation automatique de paris sportifs à partir de données de cotes et de résultats réels.**


## Description

Ce projet simule des paris sportifs sur les six plus grands championnats de football européens en utilisant des cotes issues du site FDJ (`parionssport.fdj.fr`) et les résultats des matchs issus de `fbref.com`.

L’objectif est de tester différentes stratégies de mise, de filtrage des cotes, et d’optimiser les gains en simulant un grand nombre de combinaisons de paramètres (mise, cagnotte initiale, bornes de cote).


## Fonctionnement global

1. **Web scraping** des cotes FDJ pour les championnats suivants :
   - Ligue 1
   - Premier League
   - La Liga
   - Serie A
   - Liga Portugal
   - Bundesliga

2. **Filtrage** des matchs selon une borne inférieure (`Y`) et supérieure (`Z`) sur les cotes.

3. **Simulation de paris** :
   - Une mise fixe `P` est placée pour chaque pari.
   - Le portefeuille de départ est `X`.
   - Le pari est placé tant que la cagnotte est suffisante.

4. **Mise à jour** des résultats après le match (minimum 3h après coup d’envoi) via scraping sur FBRef :
   - Si le pari est gagnant, le gain est `P * cote`.
   - Sinon, la mise est perdue.

5. **Enregistrement** des résultats et des statistiques :
   - Fichiers `archives.csv` pour chaque combinaison testée.
   - Statistiques globales : gain total, gain moyen par pari, gain moyen par euro misé.


## Paramètres principaux

- `X` : Montant initial de la cagnotte (ex. 10, 20, 50, 100).
- `P` : Mise par pari (ex. 1, 3, 5, 10).
- `Y` : Cote minimale (ex. 1.0, 1.2…).
- `Z` : Cote maximale (≥ Y + 0.2).

Ces 4 paramètres sont testés dans une boucle imbriquée pour explorer toutes les combinaisons possibles.


## Structure des fichiers générés

- `Results/`  
  ├── `X-P-Y-Z/` : Dossier pour chaque combinaison testée  
  ├── `perdus.txt` : Liste des stratégies ayant perdu toute leur cagnotte  
  ├── `stats1.txt` : Gains totaux par combinaison  
  ├── `stats2.txt` : Gain moyen par pari  
  ├── `stats3.txt` : Gain moyen par euro parié  
  └── `0-Perdus/` : Dossiers déplacés pour les simulations ayant échoué


## Dépendances

Le projet utilise les bibliothèques suivantes :
- `requests`
- `beautifulsoup4`
- `datetime`
- `csv`
- `os`, `shutil`, `sys`

Installation via pip :

```bash
pip install requests beautifulsoup4
```


## Licence

Projet personnel sans licence spécifique. Ne pas utiliser à des fins de jeu ou de paris réels.
