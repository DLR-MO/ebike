# SPDX-License-Identifier: MIT

import os
import sys
import tempfile
from collections import defaultdict
from datetime import datetime

import reach
import reach_ros

from ebike.utils import save_result
from ebike.visualization import plot_results, print_results


class Benchmark:
    def __init__(self, interactive=False):
        reach_ros.init_ros(sys.argv)
        self.iks = []
        self.robots = []
        self.scenarios = []
        self.results = defaultdict(lambda: defaultdict(dict))
        self.interactive = interactive
        self.start_time = datetime.now()

    def add_ik(self, ik):
        self.iks.append(ik)

    def add_scenario(self, scenario):
        self.scenarios.append(scenario)

    def add_robot(self, robot):
        self.robots.append(robot)

    def run(self):
        results_dir = tempfile.mkdtemp()
        os.environ["REACH_PLUGINS"] = "reach_ros_plugins"
        for robot in self.robots:
            robot.set_config()
            for scenario in self.scenarios:
                config = scenario.get_config(robot.get_planning_group())
                for ik in self.iks:
                    print(
                        f"Running benchmark for {ik.name} on robot {robot.name}, scenario {scenario.name}"
                    )
                    ik.set_config(robot.get_planning_group())
                    config_name = f"{robot.name} {scenario.name} {ik.name}"
                    reach.runReachStudy(
                        config, config_name, results_dir, self.interactive
                    )
                    db = reach.load(f"{results_dir}/{config_name}/reach.db.xml")
                    self.results[robot.name][scenario.name][ik.name] = db.results
                    save_result(
                        robot.name, scenario.name, ik.name, self.start_time, db.results
                    )
        print(f"Results saved in {results_dir}")
        return self.results

    def plot(self):
        plot_results(self.results)

    def print(self):
        print_results(self.results)
