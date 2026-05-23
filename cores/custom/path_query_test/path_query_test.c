/* path_query_test — GET_LIBRETRO_PATH, GET_CORE_ASSETS_DIRECTORY, GET_PLAYLIST_DIRECTORY. */

#include "sample_common.h"

static const char *libretro_path;
static const char *core_assets_dir;
static const char *playlist_dir;

static void path_query_run_frame(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_GET_LIBRETRO_PATH,         &libretro_path);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_CORE_ASSETS_DIRECTORY, &core_assets_dir);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_PLAYLIST_DIRECTORY,    &playlist_dir);
}

const struct sample_core_def sample_core = {
    .run_frame = path_query_run_frame,
};
