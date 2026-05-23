/* hw_shared_context_test — SET_HW_SHARED_CONTEXT. */

#include "sample_common.h"

static void hw_register_env(void)
{
    bool shared = true;
    sample_environ_cb(RETRO_ENVIRONMENT_SET_HW_SHARED_CONTEXT, &shared);
}

const struct sample_core_def sample_core = {
    .register_env_calls = hw_register_env,
};
