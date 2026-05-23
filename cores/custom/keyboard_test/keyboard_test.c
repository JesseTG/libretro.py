/* keyboard_test — exercises RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK. */

#include "sample_common.h"

static unsigned key_event_count;
static unsigned last_keycode;

static void on_keyboard_event(bool down, unsigned keycode,
                              uint32_t character, uint16_t key_modifiers)
{
    (void)down;
    (void)character;
    (void)key_modifiers;
    key_event_count++;
    last_keycode = keycode;
}

static void kb_register_env(void)
{
    struct retro_keyboard_callback kb = { .callback = on_keyboard_event };
    sample_environ_cb(RETRO_ENVIRONMENT_SET_KEYBOARD_CALLBACK, &kb);
}

const struct sample_core_def sample_core = {
    .register_env_calls = kb_register_env,
};
