#!/usr/bin/python3
import os

from ebike.visualization import generate_plot, generate_table

RESULTS_DIR = "results"

if __name__ == "__main__":
    for folder in os.listdir(RESULTS_DIR):
        if not os.path.isdir(os.path.join(RESULTS_DIR, folder)):
            continue
        if folder.startswith("_"):
            continue
        config_file = os.path.join(RESULTS_DIR, folder, "config.txt")
        plots = []
        solver_labels = []
        solver_colors = []
        solver_styles = []
        with open(config_file, "r") as f:
            robot = f.readline().strip()
            solvers = f.readline().strip().split(",")
            for line in f.readlines():
                line = line.strip()
                if line.startswith("labels:"):
                    solver_labels = line[len("labels:") :].split(",")
                elif line.startswith("colors:"):
                    solver_colors = [int(c) for c in line[len("colors:") :].split(",")]
                elif line.startswith("styles:"):
                    solver_styles = line[len("styles:") :].split(",")
                else:
                    plots.append(line.split(","))
        for i, scenarios in enumerate(plots):
            generate_plot(
                solvers,
                solver_labels,
                solver_colors,
                solver_styles,
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
