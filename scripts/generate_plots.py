#!/usr/bin/env python3
import argparse
from ebike.visualization import plot_from_db

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--solvers', nargs='*', help="Names of solvers to generate plots of")
    args = parser.parse_args()
    plot_from_db(args.solvers)
