cmake_minimum_required(VERSION 3.7)

# Extract package name and version from package.xml
find_package(ros_industrial_cmake_boilerplate REQUIRED)
extract_package_metadata(pkg)
project(${pkg_extracted_name} VERSION ${pkg_extracted_version} LANGUAGES CXX)

find_package(ament_cmake REQUIRED)
find_package(moveit_core REQUIRED)
find_package(moveit_ros_planning REQUIRED)
find_package(ament_index_cpp REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(DIRECTORY scripts USE_SOURCE_PERMISSIONS DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
install(DIRECTORY scenarios DESTINATION share/${PROJECT_NAME})

add_executable(generate_random_reachable
  scripts/generate_random_reachable.cpp
)
ament_target_dependencies(generate_random_reachable
  moveit_core
  moveit_ros_planning
  ament_index_cpp
)
install(
  TARGETS generate_random_reachable
  DESTINATION lib/${PROJECT_NAME}/scripts
)

ament_package()
