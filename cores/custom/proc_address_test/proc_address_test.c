/* proc_address_test — exercises SET_PROC_ADDRESS_CALLBACK. */

#include <string.h>

#include "sample_common.h"

static unsigned my_callable_count;

RETRO_API void my_callable(void)
{
    my_callable_count++;
}

static retro_proc_address_t pat_get_proc_address(const char *sym)
{
    if (sym && strcmp(sym, "my_callable") == 0)
        return (retro_proc_address_t)my_callable;
    return NULL;
}

static void proc_register_env(void)
{
    struct retro_get_proc_address_interface iface = {
        .get_proc_address = pat_get_proc_address,
    };
    sample_environ_cb(RETRO_ENVIRONMENT_SET_PROC_ADDRESS_CALLBACK, &iface);
}

const struct sample_core_def sample_core = {
    .register_env_calls = proc_register_env,
};
