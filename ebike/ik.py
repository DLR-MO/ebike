# SPDX-License-Identifier: MIT

import reach_ros


class AbstractIK:
    name = None

    def set_config(self, planning_group):
        raise NotImplementedError


class KDL(AbstractIK):
    name = 'KDL'

    def set_config(self, planning_group):
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver',
                                'kdl_kinematics_plugin/KDLKinematicsPlugin')
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution', 0.001)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_timeout', 1.0)


class TracIK(AbstractIK):
    name = 'TracIK'

    def set_config(self, planning_group):
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver',
                                'trac_ik_kinematics_plugin/TRAC_IKKinematicsPlugin')
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution', 0.001)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_timeout', 1.0)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.solve_type', 'Speed')


class TracIKDistance(AbstractIK):
    name = 'TracIKDistance'

    def set_config(self, planning_group):
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver',
                                'trac_ik_kinematics_plugin/TRAC_IKKinematicsPlugin')
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution', 0.001)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_timeout', 1.0)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.solve_type', 'Distance')


class PickIK(AbstractIK):
    name = 'PickIK'

    def set_config(self, planning_group):
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver',
                                'pick_ik/PickIkPlugin')
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution', 0.001)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_timeout', 1.0)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.mode', 'global')
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.memetic_gd_max_iters', 5)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.memetic_population_size', 40)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.stop_optimization_on_valid_solution', True)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.cost_threshold', 10000.0)


class BioIK(AbstractIK):
    name = 'BioIK'

    def set_config(self, planning_group):
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver',
                                'bio_ik/BioIKKinematicsPlugin')
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_search_resolution', 0.001)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_timeout', 1.0)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.kinematics_solver_attempts', 1)
        reach_ros.set_parameter(f'robot_description_kinematics.{planning_group}.mode', 'bio2_memetic')
