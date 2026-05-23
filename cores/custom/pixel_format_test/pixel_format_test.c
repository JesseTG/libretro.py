/* pixel_format_test — cycles SET_PIXEL_FORMAT, SET_ROTATION, SET_SYSTEM_AV_INFO. */

#include "sample_common.h"

static const enum retro_pixel_format pixel_formats[] = {
    RETRO_PIXEL_FORMAT_XRGB8888,
    RETRO_PIXEL_FORMAT_RGB565,
    RETRO_PIXEL_FORMAT_0RGB1555,
};

static void pixfmt_run_frame(void)
{
    if (sample_frame_count % 30u != 0u)
        return;

    const unsigned step = (unsigned)(sample_frame_count / 30u) % 3u;

    enum retro_pixel_format fmt = pixel_formats[step];
    sample_environ_cb(RETRO_ENVIRONMENT_SET_PIXEL_FORMAT, &fmt);

    unsigned rotation = step;
    sample_environ_cb(RETRO_ENVIRONMENT_SET_ROTATION, &rotation);

    if (step == 2u)
    {
        struct retro_system_av_info info;
        retro_get_system_av_info(&info);
        sample_environ_cb(RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO, &info);
    }
}

const struct sample_core_def sample_core = {
    .run_frame = pixfmt_run_frame,
};
