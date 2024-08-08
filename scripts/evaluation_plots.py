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
        solver_labels = []
        with open(config_file, "r") as f:
            robot = f.readline().strip()
            solvers = f.readline().strip().split(",")
            line = f.readline().strip()
            if line.startswith("labels:"):
                solver_labels = line[len("labels:") :].split(",")
            else:
                plots.append(line.split(","))
            for line in f.readlines():
                plots.append(line.strip().split(","))
        for i, scenarios in enumerate(plots):
            generate_plot(
                solvers,
                solver_labels,
                scenarios,
                robot,
                os.path.join(RESULTS_DIR, folder, "plot_" + str(i)),
            )
            generate_table(
                solvers,
                solver_labels,
                scenarios,
                robot,
                os.path.join(RESULTS_DIR, folder, "table_" + str(i)),
            )
