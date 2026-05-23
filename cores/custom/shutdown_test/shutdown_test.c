/* shutdown_test — calls RETRO_ENVIRONMENT_SHUTDOWN after a few frames. */

#include "sample_common.h"

#define SHUTDOWN_AT_FRAME 5u

static void shutdown_run_frame(void)
{
    if (sample_frame_count == SHUTDOWN_AT_FRAME)
        sample_environ_cb(RETRO_ENVIRONMENT_SHUTDOWN, NULL);
}

const struct sample_core_def sample_core = {
    .run_frame = shutdown_run_frame,
};
