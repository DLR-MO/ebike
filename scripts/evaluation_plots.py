#!/usr/bin/python3
import os

from ebike.visualization import generate_plot, generate_table

RESULTS_DIR = "results"

if __name__ == "__main__":
    for folder in os.listdir(RESULTS_DIR):
        if not os.path.isdir(os.path.join(RESULTS_DIR, folder)):
            continue
        config_file = os.path.join(RESULTS_DIR, folder, "config.txt")
        plots = []
        with open(config_file, "r") as f:
            robot = f.readline().strip()
            solvers = f.readline().strip().split(",")
            for line in f.readlines():
                plots.append(line.strip().split(","))
        for i, scenarios in enumerate(plots):
            generate_plot(
                solvers,
                scenarios,
                robot,
                os.path.join(RESULTS_DIR, folder, "plot_" + str(i)),
            )
            generate_table(
                solvers,
                scenarios,
                robot,
                os.path.join(RESULTS_DIR, folder, "table_" + str(i)),
            )
