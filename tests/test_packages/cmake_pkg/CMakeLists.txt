project(cmake_pkg VERSION 3.2.0)

# Using C++17
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

#
# Dependencies
#

# Usual dependencies
find_package(mpi_cmake_modules REQUIRED)
find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Boost REQUIRED COMPONENTS filesystem)


add_library(${PROJECT_NAME} SHARED
  src/foo.cpp
)
target_include_directories(
  ${PROJECT_NAME} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
                         $<INSTALL_INTERFACE:include>)
target_link_libraries(${PROJECT_NAME}
    Boost::boost
    Boost::filesystem
)


# install the include directory
install(DIRECTORY include/ DESTINATION include)

# command to install the library and binaries
install(TARGETS ${PROJECT_NAME})

# Export this package as a cmake package.
generate_cmake_package()
