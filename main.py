from core.config import generate_configurations
from core.simulator import run_simulation

def main():
    for X, P, Y, Z in generate_configurations():
        # pour dev, limite aux 2 premières ligues :
        run_simulation(X, P, Y, Z, overwrite=True, leagues=None)

if __name__ == "__main__":
    main()
