/* jit_capable_test — GET_JIT_CAPABLE + SET_SUPPORT_ACHIEVEMENTS. */

#include "sample_common.h"

static bool jit_capable;

static void jit_register_env(void)
{
    bool achievements = true;
    sample_environ_cb(RETRO_ENVIRONMENT_SET_SUPPORT_ACHIEVEMENTS, &achievements);
}

static void jit_run_frame(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_GET_JIT_CAPABLE, &jit_capable);
}

const struct sample_core_def sample_core = {
    .register_env_calls = jit_register_env,
    .run_frame          = jit_run_frame,
};
