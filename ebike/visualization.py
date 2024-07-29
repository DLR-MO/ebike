# SPDX-License-Identifier: MIT
import os.path
import sqlite3

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

    for robot, robot_data in results.items():
        plt.title("Cumulative solve rates")
        plt.ylim(0, 1)
        results_df = {}
        for scenario, scenario_data in robot_data.items():
            for solver, data in scenario_data.items():
                results_df[f"{solver}_{scenario}"] = result_to_df(data[0])

        max_ik_time = max([np.max(data.ik_time) for data in results_df.values()]) * 1000
        for scenario in robot_data:
            plt.gca().set_prop_cycle(None)  # reset colors
            for solver in scenario_data:
                data = results_df[f"{solver}_{scenario}"]
                linestyle = "dashed" if scenario.endswith("seed") else "solid"
                plt.plot(
                    np.append(
                        np.sort(data.ik_time[data.reached == 1] * 1000), max_ik_time
                    ),
                    np.append(
                        np.arange(np.sum(data.reached == 1)),
                        np.sum(data.reached == 1) - 1,
                    )
                    / (len(data) - 1),
                    label=solver,
                    linestyle=linestyle,
                )
        plt.xlabel("Time (ms)")
        plt.ylabel("Fraction solved")
        plt.legend()
        plt.show()


def plot_from_db():
    if not os.path.exists("results"):
        os.mkdir("results")
    with sqlite3.connect("results.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT scenario, robot FROM experiments")
        experiment_data = cur.fetchall()
        for scenario, robot in experiment_data:
            cur.execute(
                "SELECT DISTINCT solver FROM experiments WHERE scenario = ? AND robot = ?",
                (scenario, robot),
            )
            solvers = cur.fetchall()
            plt.title(f"Cumulative solve rates, {robot} on {scenario}")
            plt.ylim(0, 1)
            for i, (solver,) in enumerate(solvers):
                cur.execute(
                    "SELECT id FROM experiments WHERE scenario = ? AND robot = ? AND solver = ?",
                    (scenario, robot, solver),
                )
                experiment_ids = cur.fetchall()
                for (experiment_id,) in experiment_ids:
                    cur.execute(
                        "SELECT reached, ik_time FROM results WHERE experiment_id = ?",
                        (experiment_id,),
                    )
                    results = cur.fetchall()
                    reached, ik_time = np.array(results).T
                    if np.sum(reached == 1) > 0:
                        plt.plot(
                            np.sort(ik_time[reached == 1] * 1000),
                            np.arange(np.sum(reached == 1)) / (len(reached) - 1),
                            label=solver,
                            linestyle="solid",
                            color=plt.cm.tab20(i),
                        )
            plt.xlabel("Time (ms)")
            plt.ylabel("Fraction solved")
            # hide duplicate legend entries
            ax = plt.gca()
            entries = set()
            for p in ax.get_lines():
                if p.get_label() in entries:
                    p.set_label("_" + p.get_label())
                entries.add(p.get_label())
            plt.legend()
            plt.savefig(f"results/{scenario}_{robot}.png", dpi=300, bbox_inches="tight")
            plt.xlim(0, 50)
            plt.savefig(
                f"results/{scenario}_{robot}_detail.png", dpi=300, bbox_inches="tight"
            )
            plt.close()
