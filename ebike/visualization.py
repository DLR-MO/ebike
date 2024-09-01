# SPDX-License-Identifier: MIT
import os.path
import sqlite3
from itertools import zip_longest

import matplotlib.pyplot as plt
import numpy as np

from ebike.utils import result_to_df


def get(li, i, default):
    try:
        return li[i]
    except IndexError:
        return default


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

            print(f"Solution callback count ({robot} on {scenario}):")
            for solver, data in results_df.items():
                counts = data.solution_callback_count[data.reached == 1]
                print(f"{solver}: {counts.mean():.2f} ± {counts.std():.2f}")


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


def generate_plot(
    solvers,
    solver_labels,
    solver_colors,
    solver_styles,
    scenarios,
    robot,
    output_prefix,
):
    with sqlite3.connect("results.db") as conn:
        cur = conn.cursor()
        time_plot = plt.figure()
        time_ax = time_plot.subplots()
        if len(scenarios) == 1:
            title_suffix = f", {robot} on {scenarios[0]}"
        elif len(solvers) == 1:
            title_suffix = f", {robot} using {solvers[0]}"
        else:
            title_suffix = f" on {robot}"
        time_ax.set_title("Cumulative solve rates" + title_suffix)
        time_ax.set_ylim(0, 1)
        it_plot = plt.figure()
        it_ax = it_plot.subplots()
        it_ax.set_title("Solver iterations" + title_suffix)
        it_ax.set_ylim(0, 1)
        total_count_max = 0
        for scenario in scenarios:
            for i, (solver, solver_label, solver_color) in enumerate(
                zip_longest(solvers, solver_labels, solver_colors)
            ):
                n_avg = 3
                cur.execute(
                    "SELECT id FROM experiments WHERE scenario = ? AND robot = ? AND solver = ? ORDER BY id DESC LIMIT ?",
                    (scenario, robot, solver, n_avg),
                )
                fetch_result = cur.fetchall()
                use_avg = True
                if len(fetch_result) == 0:
                    print(f"Skipping {solver} on {scenario} because it does not exist")
                    continue
                elif len(fetch_result) < 3:
                    print(
                        f"Warning: {solver} on {scenario} only has {len(fetch_result)} runs!"
                    )
                    use_avg = False

                experiment_ids = [r[0] for r in fetch_result]
                cur.execute(
                    "SELECT MAX(ik_time), MAX(solution_callback_count) FROM results WHERE experiment_id IN ({})".format(
                        ",".join("?" * len(experiment_ids))
                    ),
                    experiment_ids,
                )
                max_time, max_count = cur.fetchone()

                cdfs = []
                count_cdfs = []
                xs = np.arange(0, int(max_time * 100000)) / 100
                for experiment_id in experiment_ids:
                    cur.execute(
                        "SELECT reached, ik_time, solution_callback_count FROM results WHERE experiment_id = ?",
                        (experiment_id,),
                    )
                    results = cur.fetchall()
                    reached, ik_time, count = np.array(results).T
                    times = np.sort(ik_time[reached == 1] * 1000)
                    times = (
                        np.histogram(
                            times, bins=np.arange(0, int(max_time * 100000) + 1) / 100
                        )[0].cumsum()
                        / 1000
                    )
                    if len(times) == 0:
                        times = np.zeros_like(xs)
                    else:
                        times = np.pad(
                            times, (0, int(max_time * 100000) - len(times)), "edge"
                        )
                    cdfs.append(times)

                    iterations = np.sort(count[reached == 1])
                    if len(iterations) == 0:
                        counts = np.zeros(max_count)
                    else:
                        counts, _ = np.histogram(
                            count[reached == 1],
                            bins=np.arange(iterations.min(), iterations.max() + 2),
                        )
                        counts = np.pad(counts, (0, max_count - len(counts)), "edge")
                    count_cdfs.append(np.concatenate([[0], np.cumsum(counts) / 1000]))

                if len(scenarios) > 1 and len(solvers) > 1:
                    label = f"{solver_label or solver} on {scenario}"
                elif len(scenarios) > 1:
                    label = scenario
                else:
                    label = solver_label or solver

                color = (
                    plt.cm.tab20(solver_color)
                    if solver_color is not None
                    else plt.cm.tab10(i)
                )
                cdfs = np.vstack(cdfs)
                mean_cdf = np.mean(cdfs, axis=0)
                min_cdf = np.min(cdfs, axis=0)
                max_cdf = np.max(cdfs, axis=0)
                if get(solver_styles, i, "solid") == "solid" and scenario.endswith(
                    "seed"
                ):
                    style = "dotted"
                else:
                    style = get(solver_styles, i, "solid")
                time_ax.plot(xs, mean_cdf, label=label, color=color, linestyle=style)
                if use_avg:
                    time_ax.fill_between(
                        xs,
                        min_cdf,
                        max_cdf,
                        alpha=0.2,
                        color=color,
                    )

                count_cdfs = np.vstack(count_cdfs)
                count_mean = np.mean(count_cdfs, axis=0)
                count_min = np.min(count_cdfs, axis=0)
                count_max = np.max(count_cdfs, axis=0)
                it_ax.plot(
                    np.arange(0, max_count + 1),
                    count_mean,
                    label=label,
                    color=color,
                    linestyle=style,
                )
                if use_avg:
                    it_ax.fill_between(
                        np.arange(0, max_count + 1),
                        count_min,
                        count_max,
                        alpha=0.2,
                        color=color,
                    )

                total_count_max = max(total_count_max, max_count)
        time_ax.set_xlabel("Duration (ms)")
        time_ax.set_ylabel("Fraction solved")
        time_ax.legend()
        time_ax.set_xlim(0, 1000)
        time_plot.savefig(f"{output_prefix}.png", dpi=300, bbox_inches="tight")
        time_ax.set_xlim(0, 50)
        time_plot.savefig(f"{output_prefix}_detail.png", dpi=300, bbox_inches="tight")
        time_ax.set_xlim(0, 5)
        time_plot.savefig(f"{output_prefix}_detail2.png", dpi=300, bbox_inches="tight")
        plt.close(time_plot)

        it_ax.set_xlabel("Iterations")
        it_ax.set_ylabel("Fraction solved")
        it_ax.legend()
        it_ax.set_xlim(0, total_count_max)
        it_plot.savefig(
            f"{output_prefix}_iterations.png",
            dpi=300,
            bbox_inches="tight",
        )
        it_ax.set_xlim(0, 100)
        it_plot.savefig(
            f"{output_prefix}_iterations_detail.png",
            dpi=300,
            bbox_inches="tight",
        )
        it_ax.set_xlim(0, 10)
        it_plot.savefig(
            f"{output_prefix}_iterations_detail2.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close(it_plot)


def generate_table(solvers, solver_labels, scenarios, robot, output_prefix):
    with sqlite3.connect("results.db") as conn:
        cur = conn.cursor()
        time_table = ""
        count_table = ""
        durations = {0.005: [], 0.01: [], 0.1: [], 1: []}
        iterations = {1: [], 2: [], 3: [], 5: [], 10: [], 100: []}
        time_table += (
            'table.header("Duration", '
            + ", ".join([f'"{int(x*1000)}ms"' for x in durations])
            + ', "Mean"),\n'
        )
        count_table += (
            'table.header("Iterations", '
            + ", ".join([f'"{x}"' for x in iterations])
            + ', "Mean"),\n'
        )
        for scenario in scenarios:
            for solver, solver_label in zip_longest(solvers, solver_labels):
                n_avg = 3
                cur.execute(
                    "SELECT id FROM experiments WHERE scenario = ? AND robot = ? AND solver = ? ORDER BY id DESC LIMIT ?",
                    (scenario, robot, solver, n_avg),
                )
                fetch_result = cur.fetchall()
                if len(fetch_result) == 0:
                    print(f"Skipping {solver} on {scenario} because it does not exist")
                    continue
                elif len(fetch_result) < 3:
                    print(
                        f"Warning: {solver} on {scenario} only has {len(fetch_result)} runs!"
                    )

                experiment_ids = [r[0] for r in fetch_result]

                for arr in durations.values():
                    arr.clear()
                for arr in iterations.values():
                    arr.clear()
                dur_means = []
                it_means = []

                for experiment_id in experiment_ids:
                    cur.execute(
                        "SELECT reached, ik_time, solution_callback_count FROM results WHERE experiment_id = ?",
                        (experiment_id,),
                    )
                    results = cur.fetchall()
                    reached, ik_time, count = np.array(results).T

                    for dur, arr in durations.items():
                        arr.append(np.sum(ik_time[reached == 1] <= dur) / len(reached))
                    if np.sum([reached == 1]) > 0:
                        dur_means.append(np.mean(ik_time[reached == 1]))
                        it_means.append(np.mean(count[reached == 1]))
                    else:
                        dur_means.append(0)
                        it_means.append(0)
                    for nit, arr in iterations.items():
                        arr.append(np.sum(count[reached == 1] <= nit) / len(reached))

                if len(scenarios) > 1 and len(solvers) > 1:
                    label = f"{solver_label or solver} on {scenario}"
                elif len(scenarios) > 1:
                    label = scenario
                else:
                    label = solver_label or solver

                time_table += f'"{label}", '
                for arr in durations.values():
                    time_table += f'"{np.mean(arr)*100:.1f}%", '
                time_table += f'"{np.mean(dur_means)*1000:.3f}ms",\n'
                count_table += f'"{label}", '
                for arr in iterations.values():
                    count_table += f'"{np.mean(arr)*100:.1f}%", '
                count_table += f'"{np.mean(it_means):.3f} its",\n'
        with open(output_prefix + ".txt", "w") as text_file:
            text_file.write(
                '#figure(\nplacement: auto,\ncaption: "",\ngrid(inset: 5pt,\n'
            )
            text_file.write(
                "table(columns: (auto," + " 1fr," * (len(durations) + 1) + "),\n"
            )
            text_file.write(time_table)
            text_file.write("),\n")
            text_file.write(
                "table(columns: (auto," + " 1fr," * (len(iterations) + 1) + "),\n"
            )
            text_file.write(count_table)
            text_file.write(")))")


def plot_from_db(solvers_=[]):
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

            # filter bio ik
            def is_bio_ik(s):
                if not s.startswith("BioIK") and not s.startswith("Bio_ik"):
                    return False
                if s.startswith("BioIK "):
                    return False
                return True

            # solvers = [s for s in solvers if is_bio_ik(s[0])]
            if solvers_:
                solvers = [s for s in solvers if s[0] in solvers_]

            print(scenario)
            print('table.header("Duration", "5ms", "10ms", "100ms", "1000ms", "Mean"),')
            plt.title(f"Cumulative solve rates, {robot} on {scenario}")
            plt.ylim(0, 1)
            for i, (solver,) in enumerate(solvers):
                cur.execute(
                    "SELECT id FROM experiments WHERE scenario = ? AND robot = ? AND solver = ?",
                    (scenario, robot, solver),
                )
                experiment_ids = cur.fetchall()
                solve_rates_5ms = []
                solve_rates_10ms = []
                solve_rates_100ms = []
                solve_rates_1000ms = []
                time_means = []
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
                            label=solver.split()[0],
                            linestyle="solid",
                            color=plt.cm.tab10(i),
                        )
                    solve_rates_5ms.append(
                        np.sum(ik_time[reached == 1] <= 0.005) / len(ik_time)
                    )
                    solve_rates_10ms.append(
                        np.sum(ik_time[reached == 1] <= 0.01) / len(ik_time)
                    )
                    solve_rates_100ms.append(
                        np.sum(ik_time[reached == 1] <= 0.1) / len(ik_time)
                    )
                    solve_rates_1000ms.append(
                        np.sum(ik_time[reached == 1] <= 1.0) / len(ik_time)
                    )
                    time_means.append(np.mean(ik_time))
                print(f'"{solver} ({len(experiment_ids)})", ', end="")
                print(
                    f'"{np.mean(solve_rates_5ms):.3f}", "{np.mean(solve_rates_10ms):.3f}", "{np.mean(solve_rates_100ms):.3f}", "{np.mean(solve_rates_1000ms):.3f}", "{np.mean(time_means) * 1000:.3f} ms",'
                )
            plt.xlabel("Duration (ms)")
            plt.ylabel("Fraction solved")
            # hide duplicate legend entries
            ax = plt.gca()
            entries = set()
            for p in ax.get_lines():
                if p.get_label() in entries:
                    p.set_label("_" + p.get_label())
                entries.add(p.get_label())
            plt.legend()
            plt.xlim(0, 1000)
            plt.savefig(f"results/{scenario}_{robot}.png", dpi=300, bbox_inches="tight")
            plt.xlim(0, 50)
            plt.savefig(
                f"results/{scenario}_{robot}_detail.png", dpi=300, bbox_inches="tight"
            )
            plt.xlim(0, 5)
            plt.savefig(
                f"results/{scenario}_{robot}_detail2.png", dpi=300, bbox_inches="tight"
            )
            plt.close()

            # solution callback count
            plt.title(f"Solver iterations, {robot} on {scenario}")
            plt.ylim(0, 1)
            print('table.header("Solver", "1", "2", "3", "5", "10", "100", "Mean"),')
            count_max = 0
            for i, (solver,) in enumerate(solvers):
                cur.execute(
                    "SELECT id FROM experiments WHERE scenario = ? AND robot = ? AND solver = ?",
                    (scenario, robot, solver),
                )
                experiment_ids = cur.fetchall()
                iterations = {1: [], 2: [], 3: [], 5: [], 10: [], 100: []}
                count_means = []
                for (experiment_id,) in experiment_ids:
                    cur.execute(
                        "SELECT reached, solution_callback_count FROM results WHERE experiment_id = ?",
                        (experiment_id,),
                    )
                    results = cur.fetchall()
                    reached, count = np.array(results).T
                    if np.sum(reached == 1) > 0:
                        plt.plot(
                            np.sort(count[reached == 1]),
                            np.arange(np.sum(reached == 1)) / (len(reached) - 1),
                            label=solver,
                            linestyle="solid",
                            color=plt.cm.tab10(i),
                        )
                    if np.sum(count[reached == 1]) > 0:
                        count_max = max(count_max, np.max(count[reached == 1]))
                    for nit, arr in iterations.items():
                        arr.append(np.sum(count[reached == 1] <= nit) / len(count))
                    count_means.append(np.mean(count[reached == 1]))
                print(f'"{solver} ({len(experiment_ids)})", ', end="")
                for nit, arr in iterations.items():
                    print(f'"{np.mean(arr):.3f}", ', end="")
                print(f'"{np.mean(count_means):.3f} its",')
            plt.xlabel("Iterations")
            plt.ylabel("Fraction solved")
            # hide duplicate legend entries
            ax = plt.gca()
            entries = set()
            for p in ax.get_lines():
                if p.get_label() in entries:
                    p.set_label("_" + p.get_label())
                entries.add(p.get_label())
            plt.legend()
            plt.xlim(0, count_max)
            plt.savefig(
                f"results/{scenario}_{robot}_iterations.png",
                dpi=300,
                bbox_inches="tight",
            )
            plt.xlim(0, 10)
            plt.savefig(
                f"results/{scenario}_{robot}_iterations_detail.png",
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()
