/* savestate_test — exercises serialize/unserialize + SET_SERIALIZATION_QUIRKS. */

#include <string.h>

#include "sample_common.h"

#define STATE_SIZE 4096u

static uint8_t state[STATE_SIZE];

static void savestate_register_env(void)
{
    uint64_t quirks = 0;
    sample_environ_cb(RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS, &quirks);
}

static bool savestate_load_game(const struct retro_game_info *info)
{
    (void)info;
    memset(state, 0, sizeof(state));
    return true;
}

static void savestate_run_frame(void)
{
    state[sample_frame_count % STATE_SIZE] = (uint8_t)(sample_frame_count & 0xFFu);
}

static size_t savestate_serialize_size(void) { return STATE_SIZE; }

static bool savestate_serialize(void *data, size_t size)
{
    if (size < STATE_SIZE)
        return false;
    memcpy(data, state, STATE_SIZE);
    return true;
}

static bool savestate_unserialize(const void *data, size_t size)
{
    if (size < STATE_SIZE)
        return false;
    memcpy(state, data, STATE_SIZE);
    return true;
}

const struct sample_core_def sample_core = {
    .register_env_calls = savestate_register_env,
    .load_game          = savestate_load_game,
    .run_frame          = savestate_run_frame,
    .serialize_size     = savestate_serialize_size,
    .serialize          = savestate_serialize,
    .unserialize        = savestate_unserialize,
};
