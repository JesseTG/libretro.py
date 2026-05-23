/* input_query_test — GET_INPUT_BITMASKS, GET_INPUT_MAX_USERS,
 * GET_INPUT_DEVICE_CAPABILITIES, SET_CONTROLLER_INFO.
 */

#include "sample_common.h"

static bool input_bitmasks_supported;
static unsigned input_max_users;
static uint64_t input_caps;

static const struct retro_controller_description controllers_port_0[] = {
    { "RetroPad", RETRO_DEVICE_JOYPAD },
};

static const struct retro_controller_info controller_info[] = {
    { controllers_port_0, 1 },
    { NULL, 0 },
};

static void input_register_env(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_SET_CONTROLLER_INFO, (void *)controller_info);
}

static void input_run_frame(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_GET_INPUT_BITMASKS,           &input_bitmasks_supported);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_INPUT_MAX_USERS,          &input_max_users);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_INPUT_DEVICE_CAPABILITIES, &input_caps);
}

const struct sample_core_def sample_core = {
    .register_env_calls = input_register_env,
    .run_frame          = input_run_frame,
};
