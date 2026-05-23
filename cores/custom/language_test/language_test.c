/* language_test — GET_LANGUAGE + re-asserts GET_USERNAME. */

#include "sample_common.h"

static unsigned language;
static const char *username;

static void language_run_frame(void)
{
    sample_environ_cb(RETRO_ENVIRONMENT_GET_LANGUAGE, &language);
    sample_environ_cb(RETRO_ENVIRONMENT_GET_USERNAME, &username);
}

const struct sample_core_def sample_core = {
    .run_frame = language_run_frame,
};
