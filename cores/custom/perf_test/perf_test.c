/* perf_test — exercises GET_PERF_INTERFACE + SET_PERFORMANCE_LEVEL. */

#include "sample_common.h"

static struct retro_perf_callback perf;
static struct retro_perf_counter frame_counter = { .ident = "frame_loop" };

static void perf_register_env(void)
{
    unsigned level = 5;
    sample_environ_cb(RETRO_ENVIRONMENT_SET_PERFORMANCE_LEVEL, &level);
}

static bool perf_load_game(const struct retro_game_info *info)
{
    (void)info;
    if (!sample_environ_cb(RETRO_ENVIRONMENT_GET_PERF_INTERFACE, &perf))
        perf.perf_register = NULL;
    if (perf.perf_register)
        perf.perf_register(&frame_counter);
    return true;
}

static void perf_run_frame(void)
{
    if (perf.perf_start)
        perf.perf_start(&frame_counter);
    if (perf.perf_stop)
        perf.perf_stop(&frame_counter);
}

const struct sample_core_def sample_core = {
    .register_env_calls = perf_register_env,
    .load_game          = perf_load_game,
    .run_frame          = perf_run_frame,
};
