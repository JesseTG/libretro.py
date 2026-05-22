# Custom libretro cores written for libretro.py's test suite.
#
# Each entry below uses add_sample_core() from cmake/SampleCore.cmake and
# links against the ``libretro::common`` INTERFACE target provided by
# LibretroCommon.cmake, which exposes the canonical ``libretro.h`` plus
# the rest of the libretro-common header surface.

if(NOT TARGET libretro::common)
    message(FATAL_ERROR
        "cores/custom expects the libretro::common target. "
        "Did LibretroCommon.cmake run before add_subdirectory(cores/custom)?")
endif()

add_sample_core(
    NAME led_test
    CATEGORY custom
    SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/led_test/led_test.c"
    LIBS libretro::common
)
