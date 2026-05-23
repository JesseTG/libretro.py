/* power_test — exercises RETRO_ENVIRONMENT_GET_DEVICE_POWER. */

#include "sample_common.h"

static struct retro_device_power last_power;

static void power_run_frame(void)
{
    last_power.state          = RETRO_POWERSTATE_UNKNOWN;
    last_power.seconds        = RETRO_POWERSTATE_NO_ESTIMATE;
    last_power.percent        = RETRO_POWERSTATE_NO_ESTIMATE;
    sample_environ_cb(RETRO_ENVIRONMENT_GET_DEVICE_POWER, &last_power);
}

const struct sample_core_def sample_core = {
    .run_frame = power_run_frame,
};
