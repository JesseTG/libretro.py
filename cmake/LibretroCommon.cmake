# Fetch the libretro-common repository at a pinned commit and expose it as
# an INTERFACE target ``libretro::common`` that custom cores can link against
# to pick up the canonical ``libretro.h`` and supporting headers.
#
# Upstream cores from libretro-samples still rely on the libretro.h they ship
# alongside their sources; only the custom cores in ``cores/custom/`` use
# libretro-common.

include(FetchContent)

set(LIBRETRO_COMMON_GIT_REPOSITORY "https://github.com/libretro/libretro-common.git"
    CACHE STRING "URL of the libretro-common repository to fetch")
set(LIBRETRO_COMMON_GIT_TAG "50eb3179ada37d22455fdf8d730e4c16b81e446f"
    CACHE STRING "Commit/tag of libretro-common to fetch")

FetchContent_Declare(libretro_common
    GIT_REPOSITORY "${LIBRETRO_COMMON_GIT_REPOSITORY}"
    GIT_TAG        "${LIBRETRO_COMMON_GIT_TAG}"
    GIT_SHALLOW    FALSE  # Required when GIT_TAG is a raw commit SHA.
)

FetchContent_MakeAvailable(libretro_common)

# libretro-common is mostly a header-only utility library for cores; its
# upstream Makefile builds individual ``.c`` files into a static archive,
# but for our test cores the public headers (``libretro.h`` and friends)
# under ``include/`` are all we need by default. Cores that pull in a
# specific compat helper can add the matching ``.c`` source to their own
# SOURCES list.
add_library(libretro_common INTERFACE)
target_include_directories(libretro_common INTERFACE
    "${libretro_common_SOURCE_DIR}/include")
add_library(libretro::common ALIAS libretro_common)
