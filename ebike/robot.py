# SPDX-License-Identifier: MIT

import reach_ros
from ament_index_python.packages import get_package_share_directory

from ebike.utils import get_xacro


class AbstractRobot:
    name = None

    def set_config(self):
        raise NotImplementedError

    def get_planning_group(self):
        raise NotImplementedError


class UR10(AbstractRobot):
    name = "ur10"

    def set_config(self):
        xacro_file = (
            get_package_share_directory("ur_description") + "/urdf/ur.urdf.xacro"
        )
        robot_description = get_xacro(xacro_file, {"name": "ur", "ur_type": "ur10"})
        semantic_file = (
            get_package_share_directory("ur_moveit_config") + "/srdf/ur.srdf.xacro"
        )
        robot_description_semantic = get_xacro(
            semantic_file, {"name": "ur", "ur_type": "ur10"}
        )
        reach_ros.set_parameter("robot_description", robot_description)
        reach_ros.set_parameter(
            "robot_description_semantic", robot_description_semantic
        )

    def get_planning_group(self):
        return "ur_manipulator"
