def generate_configurations():
    # Cagnotte initiale
    X_values = [100]

    # Mise par pari (montant fixe ici, mais on pourrait tester % de bankroll)
    P_values = [1]

    # Cote min à tester (1.15 pour éviter les cotes ultra-basses)
    Y_values = [round(x, 2) for x in [1.15, 1.20, 1.25, 1.30, 1.35, 1.40]]

    # Cote max à tester (jusqu'à 1.80 pour rester sur favoris solides)
    Z_values = [round(x, 2) for x in [1.35, 1.40, 1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.75, 1.80]]

    configs = []

    for X in X_values:
        for P in P_values:
            for Y in Y_values:
                for Z in Z_values:
                    # On garde seulement si Z est au moins +0.2 par rapport à Y
                    if Z >= Y + 0.20:
                        configs.append((X, P, Y, Z))
    
    return configs
