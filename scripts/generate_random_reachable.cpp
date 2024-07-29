#include <moveit/robot_state/robot_state.h>
#include <moveit/robot_model_loader/robot_model_loader.h>
#include <ament_index_cpp/get_package_share_directory.hpp>


std::string get_xacro(const std::string &xacro_file) {
  std::string xacro_command = "xacro " + xacro_file;
  std::string xacro_output;
  FILE *stream = popen(xacro_command.c_str(), "r");
  if (stream) {
    const int max_buffer = 256;
    char buffer[max_buffer];
    while (!feof(stream)) {
      if (fgets(buffer, max_buffer, stream) != nullptr) {
        xacro_output.append(buffer);
      }
    }
    pclose(stream);
  }
  return xacro_output;
}


int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("generate_random_reachable");
    std::string urdf_file = ament_index_cpp::get_package_share_directory("elise_description") + "/urdf/robot.urdf.xacro";
    std::string urdf = get_xacro(urdf_file);
    std::string srdf_file = ament_index_cpp::get_package_share_directory("elise_moveit_config") + "/config/robot.srdf";
    std::string srdf = get_xacro(srdf_file);
    rdf_loader::RDFLoader loader(urdf, srdf);
    auto model = std::make_shared<moveit::core::RobotModel>(loader.getURDF(), loader.getSRDF());
    moveit::core::RobotState rs(model);
    const int num_samples = 1000;
    std::array<Eigen::Isometry3d, num_samples> samples;
    for (auto &pose : samples) {
        rs.setToRandomPositions();
        rs.updateLinkTransforms();
        pose = rs.getGlobalLinkTransform("end_effector");
    }
    // write to PCD
    std::ostream &output = std::cout;
    output << "VERSION 0.7\n"
           << "FIELDS x y z normal_x normal_y normal_z curvature\n"
           << "SIZE 4 4 4 4 4 4 4\n"
           << "TYPE F F F F F F F\n"
           << "COUNT 1 1 1 1 1 1 1\n"
           << "WIDTH " << num_samples << "\n"
           << "HEIGHT 1\n"
           << "VIEWPOINT 0 0 0 1 0 0 0\n"
           << "POINTS " << num_samples << "\n"
           << "DATA ascii\n";
    for (const auto &pose : samples) {
        // position
        output << pose.translation().x() << " "
               << pose.translation().y() << " "
               << pose.translation().z() << " ";
        // normal
        Eigen::Vector3d normal = pose.rotation() * Eigen::Vector3d::UnitZ();
        output << normal.x() << " "
               << normal.y() << " "
               << normal.z() << " "
               // curvature
               << "0\n";
    }
}
