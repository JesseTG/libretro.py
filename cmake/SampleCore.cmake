# add_sample_core(
#     NAME <name>
#     SOURCES <src1> [<src2> ...]
#     [CATEGORY <subdir>]
#     [INCLUDES <dir1> [<dir2> ...]]
#     [LIBS <lib1> [<lib2> ...]]
#     [COMPILE_OPTIONS <opt1> [<opt2> ...]]
#     [COMPILE_DEFINITIONS <def1> [<def2> ...]]
# )
#
# Declare a libretro core as a MODULE library. The output filename is
# `<name>_libretro.<so|dll|dylib>` (matching the libretro frontend naming
# convention) and the binary is installed into
# `libretro/samples/<category>/<name>_libretro.<ext>` inside the wheel.
#
# CATEGORY defaults to "custom". Cores must not link against the Python
# runtime: libretro cores are plain shared libraries that the frontend
# loads via dlopen / LoadLibrary.

function(add_sample_core)
    set(_opts "")
    set(_singles NAME CATEGORY)
    set(_multis SOURCES INCLUDES LIBS COMPILE_OPTIONS COMPILE_DEFINITIONS)
    cmake_parse_arguments(SC "${_opts}" "${_singles}" "${_multis}" ${ARGN})

    if(NOT SC_NAME)
        message(FATAL_ERROR "add_sample_core: NAME is required")
    endif()
    if(NOT SC_SOURCES)
        message(FATAL_ERROR "add_sample_core: SOURCES is required")
    endif()
    if(NOT SC_CATEGORY)
        set(SC_CATEGORY "custom")
    endif()

    add_library(${SC_NAME} MODULE ${SC_SOURCES})

    if(SC_INCLUDES)
        target_include_directories(${SC_NAME} PRIVATE ${SC_INCLUDES})
    endif()
    if(SC_COMPILE_DEFINITIONS)
        target_compile_definitions(${SC_NAME} PRIVATE ${SC_COMPILE_DEFINITIONS})
    endif()
    if(SC_COMPILE_OPTIONS)
        target_compile_options(${SC_NAME} PRIVATE ${SC_COMPILE_OPTIONS})
    endif()
    if(SC_LIBS)
        target_link_libraries(${SC_NAME} PRIVATE ${SC_LIBS})
    endif()

    # Frontend naming convention: <name>_libretro.<ext>, no "lib" prefix.
    set_target_properties(${SC_NAME} PROPERTIES
        PREFIX ""
        OUTPUT_NAME "${SC_NAME}_libretro"
    )

    if(APPLE)
        # MODULE libraries default to ".so" on macOS,
        # but frontends (and libretro.samples._loader) expect ".dylib"
        set_target_properties(${SC_NAME} PROPERTIES SUFFIX ".dylib")
    endif()

    if(WIN32)
        # libretro.h declares the public entry points with __declspec(dllexport),
        # so explicit per-symbol exports already cover the API. Setting this
        # additionally ensures any RETRO_API-marked symbol is exported even when
        # the macro is misconfigured in a vendored libretro.h copy.
        set_target_properties(${SC_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

        if (MINGW)
            # Link the static library statically so that the sample core
            # isn't sensitive to the location and version of the runtime stdlib
            target_link_options(${SC_NAME} PRIVATE -static-libgcc -static-libstdc++ -static)
        endif()
    endif()

    install(TARGETS ${SC_NAME}
        LIBRARY DESTINATION "libretro/samples/${SC_CATEGORY}"
        RUNTIME DESTINATION "libretro/samples/${SC_CATEGORY}"
    )
endfunction()
