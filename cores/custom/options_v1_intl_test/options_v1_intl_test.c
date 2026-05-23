/* options_v1_intl_test — SET_CORE_OPTIONS (v1) + _INTL + _DISPLAY. */

#include "sample_common.h"

static struct retro_core_option_definition options_v1[] = {
    {
        "v1_choice",
        "V1 Choice",
        "Pick one.",
        {
            { "a", "A" },
            { "b", "B" },
            { NULL, NULL },
        },
        "a",
    },
    { NULL, NULL, NULL, { { NULL, NULL } }, NULL },
};

static struct retro_core_options_intl options_intl = {
    .us    = options_v1,
    .local = NULL,
};

static void options_v1_register_env(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_SET_CORE_OPTIONS, options_v1);
    sample_environ_cb(RETRO_ENVIRONMENT_SET_CORE_OPTIONS_INTL, &options_intl);

    struct retro_core_option_display display = {
        .key     = "v1_choice",
        .visible = true,
    };
    sample_environ_cb(RETRO_ENVIRONMENT_SET_CORE_OPTIONS_DISPLAY, &display);
}

const struct sample_core_def sample_core = {
    .register_env_calls = options_v1_register_env,
};
