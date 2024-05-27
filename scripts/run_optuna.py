#!/usr/bin/env python3
import numpy as np
import optuna
import reach_ros

from ebike.benchmark import Benchmark
from ebike.ik import AbstractIK
from ebike.robot import UR10
from ebike.scenario import SmallTable
from ebike.utils import result_to_df


class PickIKOptuna(AbstractIK):
    name = "pick_ik_optuna"
    population_size = None
    elite_size = None
    wipeout_fitness_tol = None
    max_generations = None
    gd_max_iters = None
    gd_max_time = None
    gd_step_size = None

    def set_config(self, planning_group):
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver",
            "pick_ik/PickIkPlugin",
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_timeout",
            1.0,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.mode", "global"
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.stop_optimization_on_valid_solution",
            True,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_num_threads", 1
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_stop_on_first_solution",
            True,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_population_size",
            self.population_size,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_elite_size",
            self.elite_size,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_wipeout_fitness_tol",
            self.wipeout_fitness_tol,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_max_generations",
            self.max_generations,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_gd_max_iters",
            self.gd_max_iters,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.memetic_gd_max_time",
            self.gd_max_time,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.gd_step_size",
            self.gd_step_size,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.gd_min_cost_delta", 1.0e-12
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.cost_threshold", 10000.0
        )

    def update_parameters(self, trial):
        self.population_size = trial.suggest_int("memetic_population_size", 1, 100)
        self.elite_size = trial.suggest_int(
            "memetic_elite_size", 1, self.population_size
        )
        self.wipeout_fitness_tol = trial.suggest_float(
            "memetic_wipeout_fitness_tol", 0.000001, 0.1, log=True
        )
        self.max_generations = trial.suggest_int("memetic_max_generations", 1, 100)
        self.gd_max_iters = trial.suggest_int("gd_max_iters", 1, 100)
        self.gd_max_time = trial.suggest_float("gd_max_time", 0.00001, 0.1, log=True)
        self.gd_step_size = trial.suggest_float("gd_step_size", 0.000001, 0.1, log=True)


class BenchmarkOptimization:
    def __init__(self):
        self.benchmark = Benchmark()
        self.robot = UR10()
        self.benchmark.add_robot(self.robot)
        self.scenario = SmallTable()
        self.benchmark.add_scenario(self.scenario)
        self.pick_ik = PickIKOptuna()
        self.benchmark.add_ik(self.pick_ik)

        sampler = optuna.samplers.TPESampler()
        storage = "sqlite:///optuna.db"

        study_name = "pick_ik_optuna"
        if study_name in optuna.get_all_study_names(storage):
            self.study = optuna.load_study(study_name=study_name, storage=storage)
        else:
            self.study = optuna.create_study(
                study_name=study_name,
                sampler=sampler,
                storage=storage,
                direction="maximize",
            )
            self.study.enqueue_trial(
                {
                    "memetic_num_threads": 1,
                    "memetic_population_size": 16,
                    "memetic_elite_size": 4,
                    "memetic_wipeout_fitness_tol": 0.00001,
                    "memetic_max_generations": 100,
                    "memetic_gd_max_iters": 25,
                    "memetic_gd_max_time": 0.005,
                    "gd_step_size": 0.0001,
                }
            )

    def optimize(self):
        self.study.optimize(self.objective, n_trials=30)

    def objective(self, trial):
        self.pick_ik.update_parameters(trial)
        result = self.benchmark.run()
        result = result_to_df(
            result[self.robot.name][self.scenario.name][self.pick_ik.name][0]
        )
        num_reached = np.sum(result.reached == 1)
        avg_ik_time = np.mean(result.ik_time[result.reached == 1])
        trial.set_user_attr("avg_ik_time", avg_ik_time)
        return num_reached / len(result)


if __name__ == "__main__":
    bo = BenchmarkOptimization()
    bo.optimize()
    print(bo.study.best_params)
    print(bo.study.best_value)
    print(bo.study.best_trial.user_attrs)
    print(optuna.importance.get_param_importances(bo.study))
