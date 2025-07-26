def generate_configurations():
    # Cagnotte initiale
    X_values = [100]

    # Mise par pari
    P_values = [1]

    # Cote min
    Y_values = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

    # Cote max
    Z_values = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]

    configs = []

    for X in X_values:
        for P in P_values:
            for Y in Y_values:
                for Z in Z_values:
                    if Z >= Y + 0.2:
                        configs.append((X, P, Y, Z))
    
    return configs