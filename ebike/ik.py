# SPDX-License-Identifier: MIT

import reach_ros


class AbstractIK:
    name = None

    def set_config(self, planning_group):
        raise NotImplementedError


class KDL(AbstractIK):
    name = "KDL"

    def set_config(self, planning_group):
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver",
            "kdl_kinematics_plugin/KDLKinematicsPlugin",
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution",
            0.001,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_timeout",
            1.0,
        )


class RelaxedIK(AbstractIK):
    name = "RelaxedIK"

    def set_config(self, planning_group):
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver",
            "relaxed_ik/RelaxedIkPlugin",
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution",
            0.001,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_timeout",
            1.0,
        )


class TracIK(AbstractIK):
    name = "TracIK"

    def set_config(self, planning_group):
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver",
            "trac_ik_kinematics_plugin/TRAC_IKKinematicsPlugin",
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution",
            0.001,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_timeout",
            1.0,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.solve_type", "Speed"
        )


class TracIKDistance(AbstractIK):
    name = "TracIKDistance"

    def set_config(self, planning_group):
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver",
            "trac_ik_kinematics_plugin/TRAC_IKKinematicsPlugin",
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution",
            0.001,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_timeout",
            1.0,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.solve_type", "Distance"
        )


class PickIK(AbstractIK):
    name = "PickIK"

    def set_config(self, planning_group):
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver",
            "pick_ik/PickIkPlugin",
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution",
            0.001,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_timeout",
            0.5,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.mode", "global"
        )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.memetic_population_size", 93
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.memetic_elite_size", 65
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.memetic_wipeout_fitness_tol", 0.02856
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.memetic_max_generations", 56
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.memetic_gd_max_iters", 66
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.memetic_gd_max_time", 0.004159
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.gd_step_size", 2.3659e-6
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.gd_min_cost_delta", 1.0e-12
        # )
        # reach_ros.set_parameter(
        #    f"robot_description_kinematics.{planning_group}.cost_threshold", 10000.0
        # )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.stop_optimization_on_first_solution",
            True,
        )


class BioIK(AbstractIK):
    name = "BioIK"

    def set_config(self, planning_group):
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver",
            "bio_ik/BioIKKinematicsPlugin",
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution",
            0.001,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_timeout",
            1.0,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.kinematics_solver_attempts",
            1,
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.mode", "bio2_memetic"
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.population_size", 4
        )
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.child_count", 100
        )


class BioIK2MemeticL(BioIK):
    name = "BioIK2Memetic_l"

    def set_config(self, planning_group):
        super().set_config(planning_group)
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.mode", "bio2_memetic_l"
        )


class BioIK2(BioIK):
    name = "BioIK2"

    def set_config(self, planning_group):
        super().set_config(planning_group)
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.mode", "bio2"
        )


class BioIK2MemeticLBFGS(BioIK):
    name = "BioIK2MemeticLBFGS"

    def set_config(self, planning_group):
        super().set_config(planning_group)
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.mode", "bio2_memetic_lbfgs"
        )


class BioIK1(BioIK):
    name = "BioIK1"

    def set_config(self, planning_group):
        super().set_config(planning_group)
        reach_ros.set_parameter(
            f"robot_description_kinematics.{planning_group}.mode", "bio1"
        )
