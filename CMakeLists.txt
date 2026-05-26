cmake_minimum_required(VERSION 3.20)

message(STATUS "Using CMake ${CMAKE_VERSION} from ${CMAKE_COMMAND}")
project(libretro_py_cores
    LANGUAGES C CXX
    DESCRIPTION "Sample libretro cores for the libretro.py test suite"
)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_C_VISIBILITY_PRESET hidden)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

option(LIBRETRO_PY_BUILD_CORES "Build sample libretro cores" ON)

include(SampleCore)

if(LIBRETRO_PY_BUILD_CORES)
    include(LibretroCommon)
    include(LibretroSamples)
    add_subdirectory(cores/custom)
endif()
