/* options_v2_test — SET_CORE_OPTIONS_V2 + _V2_INTL + display-update callback. */

#include "sample_common.h"

static struct retro_core_option_v2_category categories[] = {
    { "general", "General", "General options" },
    { NULL, NULL, NULL },
};

static struct retro_core_option_v2_definition definitions[] = {
    {
        "test_choice",
        "Choice",
        NULL,
        "Pick one of three.",
        NULL,
        "general",
        {
            { "a", "A" },
            { "b", "B" },
            { "c", "C" },
            { NULL, NULL },
        },
        "a",
    },
    {
        "test_bool",
        "Boolean",
        NULL,
        "Toggle.",
        NULL,
        "general",
        {
            { "true",  "Yes" },
            { "false", "No"  },
            { NULL, NULL },
        },
        "true",
    },
    { NULL, NULL, NULL, NULL, NULL, NULL, { { NULL, NULL } }, NULL },
};

static struct retro_core_options_v2 options = {
    categories,
    definitions,
};

static struct retro_core_options_v2_intl options_intl = {
    .us    = &options,
    .local = NULL,
};

static bool options_update_display(void)
{
    return true;
}

static struct retro_core_options_update_display_callback options_display_cb = {
    .callback = options_update_display,
};

static void options_v2_register_env(void)
{
    unsigned version = 0;
    sample_environ_cb(RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION, &version);

    if (version >= 2)
    {
        sample_environ_cb(RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2, &options);
        sample_environ_cb(RETRO_ENVIRONMENT_SET_CORE_OPTIONS_V2_INTL, &options_intl);
        sample_environ_cb(
            RETRO_ENVIRONMENT_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK,
            &options_display_cb);
    }
}

const struct sample_core_def sample_core = {
    .register_env_calls = options_v2_register_env,
};
