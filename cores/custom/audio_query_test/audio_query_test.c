/* audio_query_test — GET_AUDIO_VIDEO_ENABLE + SET_MINIMUM_AUDIO_LATENCY. */

#include "sample_common.h"

static int av_enable_mask;

static void audio_register_env(void)
{
    unsigned latency_ms = 64;
    sample_environ_cb(RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY, &latency_ms);
}

static void audio_run_frame(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_GET_AUDIO_VIDEO_ENABLE, &av_enable_mask);
}

const struct sample_core_def sample_core = {
    .register_env_calls = audio_register_env,
    .run_frame          = audio_run_frame,
};
