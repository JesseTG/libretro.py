/* video_query_test — GET_OVERSCAN, GET_CAN_DUPE, GET_PREFERRED_HW_RENDER. */

#include "sample_common.h"

static bool overscan_visible;
static bool can_dupe;
static unsigned preferred_hw;

static void video_query_run_frame(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_GET_OVERSCAN,            &overscan_visible);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_CAN_DUPE,            &can_dupe);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_PREFERRED_HW_RENDER, &preferred_hw);
}

const struct sample_core_def sample_core = {
    .run_frame = video_query_run_frame,
};
