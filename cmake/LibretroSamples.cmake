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

# Upstream "tests/test" — the canonical reference core. Single C file plus
# a vendored libretro.h in the same directory.
add_sample_core(
    NAME test
    CATEGORY tests
    SOURCES "${_lrs_src}/tests/test/libretro-test.c"
    INCLUDES "${_lrs_src}/tests/test"
    COMPILE_DEFINITIONS ${_lrs_common_defs}
)

# Additional upstream cores (audio, input, midi, video, more tests) will
# be added here as the test suite grows. Each call mirrors the layout
# above: SOURCES point into the fetched tree, INCLUDES carries the path
# to the vendored libretro.h.
