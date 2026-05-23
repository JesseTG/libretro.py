/* timing_query_test — GET_FASTFORWARDING, GET_TARGET_REFRESH_RATE,
 * GET_THROTTLE_STATE, SET_FASTFORWARDING_OVERRIDE.
 */

#include "sample_common.h"

static bool fastforwarding;
static float target_refresh_rate;
static struct retro_throttle_state throttle;

static void timing_run_frame(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_GET_FASTFORWARDING,     &fastforwarding);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_TARGET_REFRESH_RATE, &target_refresh_rate);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_THROTTLE_STATE,      &throttle);

    if (sample_frame_count == 10u)
    {
        struct retro_fastforwarding_override ff = {
            .ratio                       = 2.0f,
            .fastforward                 = true,
            .notification                = false,
            .inhibit_toggle              = false,
        };
        sample_environ_cb(RETRO_ENVIRONMENT_SET_FASTFORWARDING_OVERRIDE, &ff);
    }
}

const struct sample_core_def sample_core = {
    .run_frame = timing_run_frame,
};
