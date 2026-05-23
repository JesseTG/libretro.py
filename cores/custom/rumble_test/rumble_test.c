/* rumble_test — exercises RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE. */

#include "sample_common.h"

static struct retro_rumble_interface rumble;

static bool rumble_load_game(const struct retro_game_info *info)
{
    (void)info;
    if (!sample_environ_cb(RETRO_ENVIRONMENT_GET_RUMBLE_INTERFACE, &rumble))
        rumble.set_rumble_state = NULL;
    return true;
}

static void rumble_run_frame(void)
{
    if (!rumble.set_rumble_state)
        return;

    const uint16_t strong = (sample_frame_count & 1u) ? 0xFFFFu : 0u;
    const uint16_t weak   = (sample_frame_count & 1u) ? 0u      : 0x8000u;
    rumble.set_rumble_state(0, RETRO_RUMBLE_STRONG, strong);
    rumble.set_rumble_state(0, RETRO_RUMBLE_WEAK,   weak);
}

const struct sample_core_def sample_core = {
    .load_game = rumble_load_game,
    .run_frame = rumble_run_frame,
};
