cmake_minimum_required(VERSION 3.21)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

include(UseCython)

cython_transpile("${CMAKE_CURRENT_SOURCE_DIR}/src/creedsolo/creedsolo.pyx"
                 LANGUAGE C OUTPUT_VARIABLE creedsolo_c)

python_add_library(creedsolo MODULE "${creedsolo_c}" WITH_SOABI)

install(TARGETS creedsolo DESTINATION .)
