# Custom libretro cores written for libretro.py's test suite.
#
# Each core lives in cores/custom/<name>/<name>.c and pairs with the
# shared sample_common.c boilerplate. add_custom_core() wraps the
# add_sample_core() helper from cmake/SampleCore.cmake; new cores get
# added by inserting one line.

if(NOT TARGET libretro::common)
    message(FATAL_ERROR
        "cores/custom expects the libretro::common target. "
        "Did LibretroCommon.cmake run before add_subdirectory(cores/custom)?")
endif()

function(add_custom_core)
    set(_singles NAME)
    set(_multis SOURCES INCLUDES LIBS COMPILE_OPTIONS COMPILE_DEFINITIONS)
    cmake_parse_arguments(CC "" "${_singles}" "${_multis}" ${ARGN})

    if(NOT CC_NAME)
        message(FATAL_ERROR "add_custom_core: NAME is required")
    endif()

    add_sample_core(
        NAME ${CC_NAME}
        CATEGORY custom
        SOURCES
            "${CMAKE_CURRENT_SOURCE_DIR}/${CC_NAME}/${CC_NAME}.c"
            "${CMAKE_CURRENT_SOURCE_DIR}/sample_common.c"
            ${CC_SOURCES}
        INCLUDES
            "${CMAKE_CURRENT_SOURCE_DIR}/include"
            ${CC_INCLUDES}
        LIBS libretro::common ${CC_LIBS}
        COMPILE_OPTIONS ${CC_COMPILE_OPTIONS}
        COMPILE_DEFINITIONS
            "SAMPLE_CORE_NAME=\"${CC_NAME}\""
            ${CC_COMPILE_DEFINITIONS}
    )
endfunction()

# --- Driver-specific cores (14) -----------------------------------------

add_custom_core(NAME led_test)
add_custom_core(NAME rumble_test)
add_custom_core(NAME sensor_test)
add_custom_core(NAME microphone_test)
add_custom_core(NAME power_test)
add_custom_core(NAME perf_test)
add_custom_core(NAME vfs_test)
add_custom_core(NAME memory_map_test)
add_custom_core(NAME savestate_test)
add_custom_core(NAME keyboard_test)
add_custom_core(NAME proc_address_test)
add_custom_core(NAME shutdown_test)
add_custom_core(NAME options_v2_test)
add_custom_core(NAME options_v1_intl_test)

# --- Env-query cores (10) -----------------------------------------------

add_custom_core(NAME path_query_test)
add_custom_core(NAME video_query_test)
add_custom_core(NAME pixel_format_test)
add_custom_core(NAME input_query_test)
add_custom_core(NAME timing_query_test)
add_custom_core(NAME audio_query_test)
add_custom_core(NAME language_test)
add_custom_core(NAME game_info_ext_test)
add_custom_core(NAME jit_capable_test)
add_custom_core(NAME hw_shared_context_test)
