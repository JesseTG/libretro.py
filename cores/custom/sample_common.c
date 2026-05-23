/* sample_common.c — shared libretro entry points for cores/custom/*. */

#include <string.h>

#include "sample_common.h"

retro_environment_t       sample_environ_cb;
retro_video_refresh_t     sample_video_cb;
retro_audio_sample_t      sample_audio_cb;
retro_audio_sample_batch_t sample_audio_batch_cb;
retro_input_poll_t        sample_input_poll_cb;
retro_input_state_t       sample_input_state_cb;

unsigned sample_frame_count;

typedef uint16_t sample_pixel_t;
static sample_pixel_t sample_framebuffer[SAMPLE_CORE_WIDTH * SAMPLE_CORE_HEIGHT];

RETRO_API void retro_init(void)
{
    sample_frame_count = 0;
    if (sample_core.init)
        sample_core.init();
}

RETRO_API void retro_deinit(void)
{
    if (sample_core.deinit)
        sample_core.deinit();
}

RETRO_API unsigned retro_api_version(void)
{
    return RETRO_API_VERSION;
}

RETRO_API void retro_get_system_info(struct retro_system_info *info)
{
    memset(info, 0, sizeof(*info));
    info->library_name     = SAMPLE_CORE_NAME;
    info->library_version  = SAMPLE_CORE_VERSION;
    info->valid_extensions = SAMPLE_CORE_VALID_EXTENSIONS;
    info->need_fullpath    = false;
    info->block_extract    = false;
}

RETRO_API void retro_get_system_av_info(struct retro_system_av_info *info)
{
    memset(info, 0, sizeof(*info));
    info->geometry.base_width   = SAMPLE_CORE_WIDTH;
    info->geometry.base_height  = SAMPLE_CORE_HEIGHT;
    info->geometry.max_width    = SAMPLE_CORE_WIDTH;
    info->geometry.max_height   = SAMPLE_CORE_HEIGHT;
    info->geometry.aspect_ratio = 0.0f;
    info->timing.fps            = SAMPLE_CORE_FPS;
    info->timing.sample_rate    = SAMPLE_CORE_SAMPLE_RATE;
}

RETRO_API void retro_set_environment(retro_environment_t cb)
{
    sample_environ_cb = cb;

    bool no_game = true;
    cb(RETRO_ENVIRONMENT_SET_SUPPORT_NO_GAME, &no_game);

    enum retro_pixel_format fmt = SAMPLE_CORE_PIXEL_FORMAT;
    cb(RETRO_ENVIRONMENT_SET_PIXEL_FORMAT, &fmt);

    if (sample_core.register_env_calls)
        sample_core.register_env_calls();
}

RETRO_API void retro_set_video_refresh(retro_video_refresh_t cb)           { sample_video_cb = cb; }
RETRO_API void retro_set_audio_sample(retro_audio_sample_t cb)              { sample_audio_cb = cb; }
RETRO_API void retro_set_audio_sample_batch(retro_audio_sample_batch_t cb)  { sample_audio_batch_cb = cb; }
RETRO_API void retro_set_input_poll(retro_input_poll_t cb)                  { sample_input_poll_cb = cb; }
RETRO_API void retro_set_input_state(retro_input_state_t cb)                { sample_input_state_cb = cb; }

RETRO_API void retro_set_controller_port_device(unsigned port, unsigned device)
{
    (void)port;
    (void)device;
}

RETRO_API void retro_reset(void)
{
    sample_frame_count = 0;
    if (sample_core.reset)
        sample_core.reset();
}

RETRO_API bool retro_load_game(const struct retro_game_info *info)
{
    if (sample_core.load_game)
        return sample_core.load_game(info);
    return true;
}

RETRO_API bool retro_load_game_special(unsigned type, const struct retro_game_info *info, size_t num)
{
    (void)type;
    (void)info;
    (void)num;
    return false;
}

RETRO_API void retro_unload_game(void)
{
    if (sample_core.unload_game)
        sample_core.unload_game();
}

RETRO_API unsigned retro_get_region(void)
{
    return RETRO_REGION_NTSC;
}

RETRO_API void *retro_get_memory_data(unsigned id)
{
    if (sample_core.get_memory_data)
        return sample_core.get_memory_data(id);
    return NULL;
}

RETRO_API size_t retro_get_memory_size(unsigned id)
{
    if (sample_core.get_memory_size)
        return sample_core.get_memory_size(id);
    return 0;
}

RETRO_API void retro_run(void)
{
    if (sample_core.run_frame)
        sample_core.run_frame();

    if (sample_input_poll_cb)
        sample_input_poll_cb();

    memset(sample_framebuffer, 0, sizeof(sample_framebuffer));
    if (sample_video_cb)
        sample_video_cb(sample_framebuffer,
                        SAMPLE_CORE_WIDTH,
                        SAMPLE_CORE_HEIGHT,
                        SAMPLE_CORE_WIDTH * sizeof(sample_pixel_t));

    sample_frame_count++;
}

RETRO_API size_t retro_serialize_size(void)
{
    if (sample_core.serialize_size)
        return sample_core.serialize_size();
    return 0;
}

RETRO_API bool retro_serialize(void *data, size_t size)
{
    if (sample_core.serialize)
        return sample_core.serialize(data, size);
    return false;
}

RETRO_API bool retro_unserialize(const void *data, size_t size)
{
    if (sample_core.unserialize)
        return sample_core.unserialize(data, size);
    return false;
}

RETRO_API void retro_cheat_reset(void) {}

RETRO_API void retro_cheat_set(unsigned index, bool enabled, const char *code)
{
    (void)index;
    (void)enabled;
    (void)code;
}
