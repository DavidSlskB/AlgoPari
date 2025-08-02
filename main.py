from core.config import generate_configurations
from core.simulator import run_simulation


def main():
    configs = generate_configurations()

    for config in configs[:3]:  # pour tester uniquement 3 combinaisons
        X, P, Y, Z = config
        run_simulation(X, P, Y, Z)

if __name__ == "__main__":
    main()
