from core.config import generate_configurations
from core.simulator import run_simulation

def main():
    configs = generate_configurations()
    for X, P, Y, Z in configs:
        run_simulation(X, P, Y, Z)

if __name__ == "__main__":
    main()
