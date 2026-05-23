/* led_test — exercises RETRO_ENVIRONMENT_GET_LED_INTERFACE.
 *
 * Each frame, two LEDs are toggled in opposite phase so any LedDriver in
 * the frontend receives a steady stream of distinct state changes.
 */

#include "sample_common.h"

static struct retro_led_interface led_iface;

static bool led_load_game(const struct retro_game_info *info)
{
    (void)info;
    if (!sample_environ_cb(RETRO_ENVIRONMENT_GET_LED_INTERFACE, &led_iface))
        led_iface.set_led_state = NULL;
    return true;
}

static void led_run_frame(void)
{
    if (led_iface.set_led_state)
    {
        led_iface.set_led_state(0, (sample_frame_count & 1u) == 0u ? 1 : 0);
        led_iface.set_led_state(1, (sample_frame_count & 1u) == 1u ? 1 : 0);
    }
}

const struct sample_core_def sample_core = {
    .load_game = led_load_game,
    .run_frame = led_run_frame,
};
