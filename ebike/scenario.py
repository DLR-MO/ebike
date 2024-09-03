# SPDX-License-Identifier: MIT


class AbstractScenario:
    name = None
    hole_position = []
    hole_axis = []

    def get_config(self, planning_group):
        reach_config = {
            "optimization": {
                "radius": 0.2,
                "max_steps": 0,
                "step_improvement_threshold": 0.01,
                "max_threads": 1,
            },
            "ik_solver": {
                "name": "MoveItIKSolver",
                "distance_threshold": 0.0,
                "planning_group": planning_group,
                "collision_mesh_filename": self.ply_file,
                "touch_links": ["end_effector", "endo_third_link"],
                "hole_position": self.hole_position,
                "hole_axis": self.hole_axis,
            },
            "evaluator": {
                "name": "NoOpEvaluator",
            },
            "display": {
                "name": "ROSDisplay",
                "collision_mesh_filename": self.ply_file,
                "kinematic_base_frame": "base_link",
                "marker_scale": 0.05,
            },
            "target_pose_generator": {
                "name": "PointCloudTargetPoseGenerator",
                "pcd_file": self.pcd_file,
            },
            "logger": {"name": "BoostProgressConsoleLogger"},
        }
        if self.ply_file is None:
            del reach_config["ik_solver"]["collision_mesh_filename"]
            del reach_config["display"]["collision_mesh_filename"]
        return reach_config

    @property
    def ply_file(self):
        return f"package://ebike/scenarios/{self.name}.ply"

    @property
    def pcd_file(self):
        return f"package://ebike/scenarios/{self.name}.pcd"


class Table(AbstractScenario):
    name = "Table"


class SmallTable(AbstractScenario):
    name = "SmallTable"


class TableObjects(AbstractScenario):
    name = "TableObjects"


class Shelf(AbstractScenario):
    name = "Shelf"


class Barrel(AbstractScenario):
    name = "Barrel"


class Random(AbstractScenario):
    name = "Random"

    @property
    def ply_file(self):
        return None

    @property
    def pcd_file(self):
        return "package://ebike/scenarios/random_1000.pcd"


class RandomUR(AbstractScenario):
    name = "Random"

    @property
    def ply_file(self):
        return None

    @property
    def pcd_file(self):
        return "package://ebike/scenarios/random_ur.pcd"
