# SPDX-License-Identifier: MIT

import matplotlib.pyplot as plt
import numpy as np
from ebike.utils import result_to_df


def plot_results(results):
    # Transform to pandas dataframes
    for robot, robot_data in results.items():
        for scenario, scenario_data in robot_data.items():
            results_df = {}
            for solver, data in scenario_data.items():
                results_df[solver] = result_to_df(data[0])

            plt.title(f"Success rates ({robot} on {scenario})")
            plt.bar(results_df.keys(), [np.sum(data.reached == True) / len(data) for data in results_df.values()])
            plt.show()
            plt.title(f"Solve times (ms) ({robot} on {scenario})")
            plt.boxplot([data.ik_time[data.reached == True] * 1000 for data in results_df.values()],
                        labels=results_df.keys())
            plt.show()
