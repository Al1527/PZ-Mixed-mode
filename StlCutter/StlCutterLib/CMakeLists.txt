cmake_minimum_required(VERSION 3.15)

project(StlCutter LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(BUILD_SHARED_LIBS ON)

# ============================
#  Znajdź VTK
# ============================
find_package(VTK REQUIRED COMPONENTS
    CommonCore
    CommonDataModel
    IOGeometry
    FiltersCore
    FiltersGeneral
)

message(STATUS "VTK found: ${VTK_VERSION}")
message(STATUS "VTK libs: ${VTK_LIBRARIES}")

# ============================
#  Biblioteka DLL
# ============================
add_library(StlCutterLib SHARED
    StlCutter.cpp
    StlCutter.h
)

target_link_libraries(StlCutter PRIVATE ${VTK_LIBRARIES})
target_include_directories(StlCutter PRIVATE ${VTK_INCLUDE_DIRS})

vtk_module_autoinit(
    TARGETS StlCutter
    MODULES ${VTK_LIBRARIES}
)

# ============================
#  Folder deploy/
# ============================
set(DEPLOY_DIR "${CMAKE_BINARY_DIR}/deploy")

# Pobierz folder z DLL‑kami VTK
get_target_property(VTK_DLL_PATH VTK::CommonCore IMPORTED_LOCATION_RELEASE)
get_filename_component(VTK_BIN_DIR "${VTK_DLL_PATH}" DIRECTORY)

add_custom_command(TARGET StlCutter POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E echo "Tworzę folder deploy..."
    COMMAND ${CMAKE_COMMAND} -E make_directory "${DEPLOY_DIR}"

    COMMAND ${CMAKE_COMMAND} -E echo "Kopiuję StlCutter.dll..."
    COMMAND ${CMAKE_COMMAND} -E copy "$<TARGET_FILE:StlCutter>" "${DEPLOY_DIR}"

    COMMAND ${CMAKE_COMMAND} -E echo "Kopiuję DLL-e VTK..."
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${VTK_BIN_DIR}" "${DEPLOY_DIR}"
)
