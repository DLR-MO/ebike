# SPDX-License-Identifier: MIT

import matplotlib.pyplot as plt
import numpy as np

from ebike.utils import result_to_df


def print_results(results):
    for robot, robot_data in results.items():
        for scenario, scenario_data in robot_data.items():
            results_df = {}
            for solver, data in scenario_data.items():
                results_df[solver] = result_to_df(data[0])

            print(f"Success rates ({robot} on {scenario}):")
            for solver, data in results_df.items():
                success_rate = np.sum(data.reached == 1) / len(data)
                print(f"{solver}: {success_rate}")

            print(f"Solve times (ms) ({robot} on {scenario}):")
            for solver, data in results_df.items():
                solve_times = data.ik_time[data.reached == 1] * 1000
                print(
                    f"{solver}: {solve_times.mean():.2f} ms ± {solve_times.std():.2f} ms"
                )


def plot_results(results):
    for robot, robot_data in results.items():
        for scenario, scenario_data in robot_data.items():
            results_df = {}
            for solver, data in scenario_data.items():
                results_df[solver] = result_to_df(data[0])

            plt.title(f"Success rates ({robot} on {scenario})")
            plt.bar(
                results_df.keys(),
                [np.sum(data.reached == 1) / len(data) for data in results_df.values()],
            )
            plt.show()
            plt.title(f"Solve times (ms) ({robot} on {scenario})")
            plt.boxplot(
                [
                    data.ik_time[data.reached == 1] * 1000
                    for data in results_df.values()
                ],
                labels=results_df.keys(),
            )
            plt.show()
