# SPDX-License-Identifier: MIT

class AbstractScenario:
    name = None

    def get_config(self, planning_group):
        ply_file = f'package://ebike/scenarios/{self.name}.ply'
        pcd_file = f'package://ebike/scenarios/{self.name}.pcd'
        reach_config = {
            'optimization': {
                'radius': 0.2,
                'max_steps': 0,
                'step_improvement_threshold': 0.01,
                'max_threads': 1
            },
            'ik_solver': {
                'name': 'MoveItIKSolver',
                'distance_threshold': 0.0,
                'planning_group': planning_group,
                'collision_mesh_filename': ply_file,
                'touch_links': ['end_effector']
            },
            'evaluator': {
                'name': 'NoOpEvaluator',
            },
            'display': {
                'name': 'ROSDisplay',
                'collision_mesh_filename': ply_file,
                'kinematic_base_frame': 'base_link',
                'marker_scale': 0.05,
            },
            'target_pose_generator': {
                'name': 'PointCloudTargetPoseGenerator',
                'pcd_file': pcd_file
            },
            'logger': {
                'name': 'BoostProgressConsoleLogger'
            }
        }
        return reach_config


class Table(AbstractScenario):
    name = 'table'


class SmallTable(AbstractScenario):
    name = 'small_table'


class Kallax(AbstractScenario):
    name = 'kallax'

class Barrel(AbstractScenario):
    name = 'barrel'
