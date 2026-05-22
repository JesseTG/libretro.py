/* led_test — minimal libretro core that exercises RETRO_ENVIRONMENT_GET_LED_INTERFACE.
 *
 * Each frame, two LEDs are toggled in opposite phase so any LedDriver in the
 * frontend receives a steady stream of distinct state changes. The core
 * otherwise renders a black framebuffer and produces no audio.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "libretro.h"

#define FB_WIDTH  256u
#define FB_HEIGHT 224u

static retro_environment_t environ_cb;
static retro_video_refresh_t video_cb;
static retro_audio_sample_t audio_cb;
static retro_audio_sample_batch_t audio_batch_cb;
static retro_input_poll_t input_poll_cb;
static retro_input_state_t input_state_cb;

static struct retro_led_interface led_iface;
static unsigned frame_count = 0;
static uint16_t framebuffer[FB_WIDTH * FB_HEIGHT];

RETRO_API void retro_init(void) { frame_count = 0; }
RETRO_API void retro_deinit(void) {}

RETRO_API unsigned retro_api_version(void) { return RETRO_API_VERSION; }

RETRO_API void retro_get_system_info(struct retro_system_info *info)
{
    memset(info, 0, sizeof(*info));
    info->library_name = "led_test";
    info->library_version = "0.1";
    info->valid_extensions = "";
    info->need_fullpath = false;
    info->block_extract = false;
}

RETRO_API void retro_get_system_av_info(struct retro_system_av_info *info)
{
    memset(info, 0, sizeof(*info));
    info->geometry.base_width = FB_WIDTH;
    info->geometry.base_height = FB_HEIGHT;
    info->geometry.max_width = FB_WIDTH;
    info->geometry.max_height = FB_HEIGHT;
    info->geometry.aspect_ratio = 0.0f;
    info->timing.fps = 60.0;
    info->timing.sample_rate = 30000.0;
}

RETRO_API void retro_set_environment(retro_environment_t cb)
{
    environ_cb = cb;
    bool no_game = true;
    cb(RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME, &no_game);
    enum retro_pixel_format fmt = RETRO_PIXEL_FORMAT_RGB565;
    cb(RETRO_ENVIRONMENT_SET_PIXEL_FORMAT, &fmt);
}

RETRO_API void retro_set_video_refresh(retro_video_refresh_t cb) { video_cb = cb; }
RETRO_API void retro_set_audio_sample(retro_audio_sample_t cb) { audio_cb = cb; }
RETRO_API void retro_set_audio_sample_batch(retro_audio_sample_batch_t cb) { audio_batch_cb = cb; }
RETRO_API void retro_set_input_poll(retro_input_poll_t cb) { input_poll_cb = cb; }
RETRO_API void retro_set_input_state(retro_input_state_t cb) { input_state_cb = cb; }

RETRO_API void retro_set_controller_port_device(unsigned port, unsigned device)
{
    (void)port;
    (void)device;
}

RETRO_API void retro_reset(void) { frame_count = 0; }

RETRO_API bool retro_load_game(const struct retro_game_info *info)
{
    (void)info;
    memset(&led_iface, 0, sizeof(led_iface));
    if (!environ_cb || !environ_cb(RETRO_ENVIRONMENT_GET_LED_INTERFACE, &led_iface))
        led_iface.set_led_state = NULL;
    return true;
}

RETRO_API bool retro_load_game_special(unsigned type, const struct retro_game_info *info, size_t num)
{
    (void)type;
    (void)info;
    (void)num;
    return false;
}

RETRO_API void retro_unload_game(void) {}

RETRO_API unsigned retro_get_region(void) { return RETRO_REGION_NTSC; }

RETRO_API void *retro_get_memory_data(unsigned id)
{
    (void)id;
    return NULL;
}

RETRO_API size_t retro_get_memory_size(unsigned id)
{
    (void)id;
    return 0;
}

RETRO_API void retro_run(void)
{
    if (led_iface.set_led_state)
    {
        led_iface.set_led_state(0, (frame_count & 1u) == 0u ? 1 : 0);
        led_iface.set_led_state(1, (frame_count & 1u) == 1u ? 1 : 0);
    }

    if (input_poll_cb)
        input_poll_cb();

    memset(framebuffer, 0, sizeof(framebuffer));
    if (video_cb)
        video_cb(framebuffer, FB_WIDTH, FB_HEIGHT, FB_WIDTH * sizeof(uint16_t));

    frame_count++;
}

RETRO_API size_t retro_serialize_size(void) { return 0; }

RETRO_API bool retro_serialize(void *data, size_t size)
{
    (void)data;
    (void)size;
    return false;
}

RETRO_API bool retro_unserialize(const void *data, size_t size)
{
    (void)data;
    (void)size;
    return false;
}

RETRO_API void retro_cheat_reset(void) {}

RETRO_API void retro_cheat_set(unsigned index, bool enabled, const char *code)
{
    (void)index;
    (void)enabled;
    (void)code;
}
