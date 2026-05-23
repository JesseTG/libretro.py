/* microphone_test — exercises RETRO_ENVIRONMENT_GET_MICROPHONE_INTERFACE. */

#include "sample_common.h"

static struct retro_microphone_interface mic_iface;
static retro_microphone_t *mic;
static int16_t mic_buffer[1024];

static bool mic_load_game(const struct retro_game_info *info)
{
    (void)info;
    struct retro_microphone_interface req = {
        .interface_version = RETRO_MICROPHONE_INTERFACE_VERSION,
    };
    if (sample_environ_cb(RETRO_ENVIRONMENT_GET_MICROPHONE_INTERFACE, &req))
        mic_iface = req;

    if (mic_iface.open_mic)
    {
        struct retro_microphone_params params = { .rate = 44100 };
        mic = mic_iface.open_mic(&params);
        if (mic && mic_iface.set_mic_state)
            mic_iface.set_mic_state(mic, true);
    }
    return true;
}

static void mic_run_frame(void)
{
    if (mic && mic_iface.read_mic)
        (void)mic_iface.read_mic(mic, mic_buffer, sizeof(mic_buffer) / sizeof(mic_buffer[0]));
}

static void mic_unload_game(void)
{
    if (mic && mic_iface.close_mic)
        mic_iface.close_mic(mic);
    mic = NULL;
}

const struct sample_core_def sample_core = {
    .load_game   = mic_load_game,
    .unload_game = mic_unload_game,
    .run_frame   = mic_run_frame,
};
