# Fetch the libretro-samples repository at a pinned commit and expose its
# sample cores via add_sample_core(...) targets. Upstream only ships
# per-core hand-written Makefiles, so each sample is registered here as a
# fresh CMake target rather than reusing any upstream build glue.

include(FetchContent)

set(LIBRETRO_SAMPLES_GIT_REPOSITORY "https://github.com/libretro/libretro-samples.git"
    CACHE STRING "URL of the libretro-samples repository to fetch")
set(LIBRETRO_SAMPLES_GIT_TAG "bce193bc1b8c9a3da43b2ead0158a69e28b37ed8"
    CACHE STRING "Commit/tag of libretro-samples to fetch")

FetchContent_Declare(libretro_samples
    GIT_REPOSITORY "${LIBRETRO_SAMPLES_GIT_REPOSITORY}"
    GIT_TAG        "${LIBRETRO_SAMPLES_GIT_TAG}"
    GIT_SHALLOW    FALSE  # Required when GIT_TAG is a raw commit SHA.
)

FetchContent_MakeAvailable(libretro_samples)

set(_lrs_src "${libretro_samples_SOURCE_DIR}")

# Compile definitions that several upstream cores rely on but don't set themselves:
#   _USE_MATH_DEFINES — makes M_PI etc. visible from <math.h> on MSVC.
set(_lrs_common_defs _USE_MATH_DEFINES)

# --- audio/ ---------------------------------------------------------------

foreach(_audio_core IN ITEMS audio_callback audio_no_callback audio_playback_wav)
    add_sample_core(
        NAME ${_audio_core}
        CATEGORY audio
        SOURCES "${_lrs_src}/audio/${_audio_core}/libretro-test.c"
        INCLUDES "${_lrs_src}/audio/${_audio_core}"
        COMPILE_DEFINITIONS ${_lrs_common_defs}
    )
endforeach()

# --- input/button_test ----------------------------------------------------

# button_test vendors a tiny libretro-common subset alongside its sources,
# but ``retro_timers.h`` from that subset pulls in ``compat/msvc.h`` on
# Windows which only exists in the full libretro-common tree. Put both on
# the include path so the MSVC path resolves.
add_sample_core(
    NAME button_test
    CATEGORY input
    SOURCES "${_lrs_src}/input/button_test/libretro.c"
    INCLUDES
        "${_lrs_src}/input/button_test"
        "${_lrs_src}/input/button_test/libretro-common/include"
        "${libretro_common_SOURCE_DIR}/include"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

# --- midi/midi_test -------------------------------------------------------

add_sample_core(
    NAME midi_test
    CATEGORY midi
    SOURCES "${_lrs_src}/midi/midi_test/libretro.c"
    INCLUDES "${_lrs_src}/midi/midi_test"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

# --- tests/ ---------------------------------------------------------------

# tests/test — the canonical reference core.
add_sample_core(
    NAME test
    CATEGORY tests
    SOURCES "${_lrs_src}/tests/test/libretro-test.c"
    INCLUDES "${_lrs_src}/tests/test"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

# tests/test_advanced — adds subsystem and content-override coverage.
add_sample_core(
    NAME test_advanced
    CATEGORY tests
    SOURCES "${_lrs_src}/tests/test_advanced/libretro-test.c"
    INCLUDES "${_lrs_src}/tests/test_advanced"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

# tests/cruzes — TTF text-rendering demo. Ships a vendored stb_truetype.h,
# three bitmap-font headers, and a small ttf2c helper (the latter provides
# the rasteriser cruzes.c calls into).
add_sample_core(
    NAME cruzes
    CATEGORY tests
    SOURCES
        "${_lrs_src}/tests/cruzes/cruzes.c"
        "${_lrs_src}/tests/cruzes/ttf2c.c"
    INCLUDES "${_lrs_src}/tests/cruzes"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

# --- video/software/ ------------------------------------------------------

add_sample_core(
    NAME software_rendering
    CATEGORY video
    SOURCES "${_lrs_src}/video/software/rendering/libretro-test.c"
    INCLUDES "${_lrs_src}/video/software/rendering"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

add_sample_core(
    NAME software_direct_to_vram
    CATEGORY video
    SOURCES "${_lrs_src}/video/software/rendering_direct_to_vram/libretro-test.c"
    INCLUDES "${_lrs_src}/video/software/rendering_direct_to_vram"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

# --- video/opengl/ --------------------------------------------------------
#
# The OpenGL cores need a system GL header set and the upstream ``glsym/``
# loader for cross-platform extension resolution. The Windows SDK ships
# ``GL/gl.h`` but not ``GL/glext.h``; rather than depend on GLEW or vendor
# Khronos headers, we skip the GL cores when the extension header is
# missing. ``find_package`` is allowed to fail on platforms where GL
# development headers aren't installed at all.
find_package(OpenGL COMPONENTS OpenGL)

include(CheckIncludeFile)
set(CMAKE_REQUIRED_QUIET TRUE)
check_include_file("GL/glext.h" LIBRETRO_PY_HAVE_GL_GLEXT_H)

if(OpenGL_FOUND)
    set(_gl_root "${_lrs_src}/video/opengl")

    # Each fixed-function / shader sample has its own ``glsym/`` directory
    # with the GL loader sources it wants.
    add_sample_core(
        NAME gl_fixedfunction
        CATEGORY video
        SOURCES
            "${_gl_root}/libretro_test_gl_fixedfunction/libretro_gl_ff_test.c"
            "${_gl_root}/libretro_test_gl_fixedfunction/glsym/glsym_gl.c"
            "${_gl_root}/libretro_test_gl_fixedfunction/glsym/rglgen.c"
        INCLUDES
            "${_gl_root}/libretro_test_gl_fixedfunction"
            "${_gl_root}/libretro_test_gl_fixedfunction/glsym"
        COMPILE_DEFINITIONS ${_lrs_common_defs} HAVE_OPENGL
        LIBS OpenGL::GL
    )

    add_sample_core(
        NAME gl_shaders
        CATEGORY video
        SOURCES
            "${_gl_root}/libretro_test_gl_shaders/libretro_gl_test.c"
            "${_gl_root}/libretro_test_gl_shaders/glsym/glsym_gl.c"
            "${_gl_root}/libretro_test_gl_shaders/glsym/rglgen.c"
        INCLUDES
            "${_gl_root}/libretro_test_gl_shaders"
            "${_gl_root}/libretro_test_gl_shaders/glsym"
        COMPILE_DEFINITIONS ${_lrs_common_defs} HAVE_OPENGL CORE
        LIBS OpenGL::GL
    )

    # Need ZLIB for the PNG library that this sample uses
    find_package(ZLIB)
    # The compute-shaders sample is C++ and vendors its own ``glm/``,
    # ``gl/``, ``rpng/`` and ``app/`` helper layers. Every ``.cpp`` under
    # ``libretro/``, ``app/``, ``gl/`` and ``rpng/`` participates.
    set(_gl_cs "${_gl_root}/libretro_test_gl_compute_shaders")
    file(GLOB _gl_cs_sources
        CONFIGURE_DEPENDS
        "${_gl_cs}/libretro/*.cpp"
        "${_gl_cs}/app/*.cpp"
        "${_gl_cs}/gl/*.cpp"
        "${_gl_cs}/rpng/*.c"
        "${_gl_cs}/glsym/glsym_gl.c"
        "${_gl_cs}/glsym/rglgen.c"
    )
    add_sample_core(
        NAME gl_compute_shaders
        CATEGORY video
        SOURCES ${_gl_cs_sources}
        INCLUDES
            "${_gl_cs}"
            "${_gl_cs}/libretro"
            "${_gl_cs}/app"
            "${_gl_cs}/gl"
            "${_gl_cs}/rpng"
            "${_gl_cs}/glsym"
            "${_gl_cs}/glm"
        COMPILE_DEFINITIONS ${_lrs_common_defs} HAVE_OPENGL CORE GL_GLEXT_PROTOTYPES
        LIBS OpenGL::GL ZLIB::ZLIB
    )
else()
    if(NOT OpenGL_FOUND)
        message(STATUS "libretro.py: OpenGL not found; skipping GL sample cores.")
    elseif(NOT LIBRETRO_PY_HAVE_GL_GLEXT_H)
        message(STATUS
            "libretro.py: GL/glext.h not available on this toolchain; "
            "skipping GL sample cores.")
    endif()
endif()
