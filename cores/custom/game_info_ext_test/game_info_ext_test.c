/* game_info_ext_test — GET_GAME_INFO_EXT + SET_CONTENT_INFO_OVERRIDE. */

#include "sample_common.h"

static const struct retro_game_info_ext *game_info_ext;

static const struct retro_system_content_info_override overrides[] = {
    {
        .extensions       = "bin",
        .need_fullpath    = false,
        .persistent_data  = true,
    },
    { NULL, false, false },
};

static void content_register_env(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE, (void *)overrides);
}

static bool content_load_game(const struct retro_game_info *info)
{
    (void)info;
    sample_environ_cb(RETRO_ENVIRONMENT_GET_GAME_INFO_EXT, &game_info_ext);
    return true;
}

const struct sample_core_def sample_core = {
    .register_env_calls = content_register_env,
    .load_game          = content_load_game,
};
