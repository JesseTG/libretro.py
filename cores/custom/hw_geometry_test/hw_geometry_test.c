/* hw_geometry_test — hardware rendering whose frame is far smaller than the
 * framebuffer the frontend allocates for it, and whose size changes as it runs.
 *
 * Two things a frontend's OpenGL video driver has to get right, and which a
 * fixed-resolution core can't expose:
 *
 *   1. The frontend sizes its render texture from ``max_width``/``max_height``,
 *      but the core only ever draws into the ``base_width``/``base_height``
 *      corner of it. A driver that reads back the whole texture shrinks the
 *      frame by ``base / max``. This core declares a maximum 8x its base size
 *      on both axes, so that mistake is impossible to miss.
 *
 *   2. A core may resize its output with SET_GEOMETRY between frames. A driver
 *      that keeps drawing through the viewport it started with leaves the
 *      excess undrawn. This core cycles through four frame sizes, one per
 *      ``retro_run``.
 *
 * Each frame is painted as four quadrants of flat, distinct colour, and every
 * texel outside the frame is painted with a fifth colour the frontend must
 * never show. A correct frontend therefore presents four equal quadrants and
 * none of the sentinel; either mistake above disturbs both properties.
 *
 * OpenGL entry points are resolved through the frontend's ``get_proc_address``
 * rather than linked, so this core needs no GL headers and builds anywhere the
 * other custom cores do.
 */

#include <string.h>

#include "sample_common.h"

/* --- Just enough OpenGL ---------------------------------------------------
 *
 * Declared here rather than pulled from <GL/gl.h>, which isn't available on
 * every toolchain that builds these cores (and which would drag in GL/glext.h
 * for the framebuffer entry points).
 */

#if defined(_WIN32)
#define GLAPIENTRY __stdcall
#else
#define GLAPIENTRY
#endif

typedef unsigned int GLenum;
typedef unsigned int GLbitfield;
typedef unsigned int GLuint;
typedef int          GLint;
typedef int          GLsizei;
typedef float        GLclampf;

#define GL_COLOR_BUFFER_BIT 0x00004000u
#define GL_DEPTH_BUFFER_BIT 0x00000100u
#define GL_SCISSOR_TEST     0x0C11u
#define GL_FRAMEBUFFER      0x8D40u

typedef void(GLAPIENTRY *gl_bind_framebuffer_t)(GLenum target, GLuint framebuffer);
typedef void(GLAPIENTRY *gl_clear_color_t)(GLclampf r, GLclampf g, GLclampf b, GLclampf a);
typedef void(GLAPIENTRY *gl_clear_t)(GLbitfield mask);
typedef void(GLAPIENTRY *gl_toggle_t)(GLenum cap);
typedef void(GLAPIENTRY *gl_rect_t)(GLint x, GLint y, GLsizei width, GLsizei height);

static struct
{
    gl_bind_framebuffer_t BindFramebuffer;
    gl_clear_color_t      ClearColor;
    gl_clear_t            Clear;
    gl_toggle_t           Enable;
    gl_toggle_t           Disable;
    gl_rect_t             Scissor;
    gl_rect_t             Viewport;
} gl;

/* --- Frame schedule and palette ------------------------------------------- */

struct hw_geometry_size
{
    unsigned width;
    unsigned height;
};

/* Every size is even, so the four quadrants divide exactly,
 * and every size fits within SAMPLE_CORE_MAX_WIDTH x SAMPLE_CORE_MAX_HEIGHT. */
static const struct hw_geometry_size hw_geometry_sizes[] = {
    { SAMPLE_CORE_WIDTH, SAMPLE_CORE_HEIGHT }, /*  64 x  48, the declared base */
    { 128u, 96u },
    { 96u, 72u },
    { 256u, 192u },
};

#define HW_GEOMETRY_SIZE_COUNT (sizeof(hw_geometry_sizes) / sizeof(hw_geometry_sizes[0]))

struct hw_geometry_rgb
{
    GLclampf r;
    GLclampf g;
    GLclampf b;
};

/* Whole components only, so each maps to an exact 8-bit value
 * and the frontend's output can be compared without a tolerance. */
static const struct hw_geometry_rgb HW_GEOMETRY_QUADRANTS[4] = {
    { 1.0f, 0.0f, 0.0f }, /* south-west, in OpenGL's bottom-left origin */
    { 0.0f, 1.0f, 0.0f }, /* south-east */
    { 0.0f, 0.0f, 1.0f }, /* north-west */
    { 1.0f, 1.0f, 1.0f }, /* north-east */
};

/* Painted over every texel the frame doesn't cover. Seeing this in a
 * presented frame means the frontend read past what the core rendered. */
static const struct hw_geometry_rgb HW_GEOMETRY_SENTINEL = { 1.0f, 0.0f, 1.0f };

/* --- State ---------------------------------------------------------------- */

static struct retro_hw_render_callback hw_render;
static bool     gl_ready;
static unsigned frame_width  = SAMPLE_CORE_WIDTH;
static unsigned frame_height = SAMPLE_CORE_HEIGHT;

/* Large enough for the biggest frame this core will ever present. */
static uint32_t software_frame[SAMPLE_CORE_MAX_WIDTH * SAMPLE_CORE_MAX_HEIGHT];

static bool hw_geometry_load_gl(void)
{
    if (!hw_render.get_proc_address)
        return false;

#define LOAD_GL(field, type, symbol)                                             \
    do                                                                           \
    {                                                                            \
        gl.field = (type)hw_render.get_proc_address(symbol);                     \
        if (!gl.field)                                                           \
            return false;                                                        \
    } while (0)

    LOAD_GL(BindFramebuffer, gl_bind_framebuffer_t, "glBindFramebuffer");
    LOAD_GL(ClearColor, gl_clear_color_t, "glClearColor");
    LOAD_GL(Clear, gl_clear_t, "glClear");
    LOAD_GL(Enable, gl_toggle_t, "glEnable");
    LOAD_GL(Disable, gl_toggle_t, "glDisable");
    LOAD_GL(Scissor, gl_rect_t, "glScissor");
    LOAD_GL(Viewport, gl_rect_t, "glViewport");

#undef LOAD_GL

    return true;
}

static void hw_geometry_context_reset(void)
{
    gl_ready = hw_geometry_load_gl();
}

static void hw_geometry_context_destroy(void)
{
    gl_ready = false;
    memset(&gl, 0, sizeof(gl));
}

static bool hw_geometry_load_game(const struct retro_game_info *info)
{
    (void)info;

    memset(&hw_render, 0, sizeof(hw_render));
    hw_render.context_type       = RETRO_HW_CONTEXT_OPENGL_CORE;
    hw_render.version_major      = 3;
    hw_render.version_minor      = 3;
    hw_render.context_reset      = hw_geometry_context_reset;
    hw_render.context_destroy    = hw_geometry_context_destroy;
    hw_render.depth              = true;
    hw_render.bottom_left_origin = true;

    return sample_environ_cb(RETRO_ENVIRONMENT_SET_HW_RENDER, &hw_render);
}

static void hw_geometry_reset(void)
{
    frame_width  = SAMPLE_CORE_WIDTH;
    frame_height = SAMPLE_CORE_HEIGHT;
}

/* Ask the frontend to resize the presented frame, staying within the maximum
 * geometry declared up front (which SET_GEOMETRY is not allowed to exceed). */
static void hw_geometry_resize(unsigned width, unsigned height)
{
    if (width == frame_width && height == frame_height)
        return;

    frame_width  = width;
    frame_height = height;

    struct retro_game_geometry geometry;
    memset(&geometry, 0, sizeof(geometry));
    geometry.base_width   = frame_width;
    geometry.base_height  = frame_height;
    geometry.max_width    = SAMPLE_CORE_MAX_WIDTH;
    geometry.max_height   = SAMPLE_CORE_MAX_HEIGHT;
    geometry.aspect_ratio = (float)frame_width / (float)frame_height;

    sample_environ_cb(RETRO_ENVIRONMENT_SET_GEOMETRY, &geometry);
}

static void hw_geometry_fill(GLint x, GLint y, GLsizei width, GLsizei height,
                             const struct hw_geometry_rgb *colour)
{
    gl.Scissor(x, y, width, height);
    gl.ClearColor(colour->r, colour->g, colour->b, 1.0f);
    gl.Clear(GL_COLOR_BUFFER_BIT);
}

/* XRGB8888: one 0x00RRGGBB word per pixel, in native byte order. */
static uint32_t hw_geometry_pack(const struct hw_geometry_rgb *colour)
{
    const uint32_t r = (uint32_t)(colour->r * 255.0f);
    const uint32_t g = (uint32_t)(colour->g * 255.0f);
    const uint32_t b = (uint32_t)(colour->b * 255.0f);
    return (r << 16) | (g << 8) | b;
}

/* The same four quadrants, drawn on the CPU and handed over as an ordinary
 * software frame. A core is free to mix the two kinds of frame -- a software
 * menu over a hardware-rendered game does exactly this -- and the frontend
 * has to sample each correctly, because the textures behind them are sized
 * differently: the hardware one covers the maximum geometry, the software one
 * covers only this frame. */
static void hw_geometry_present_software(void)
{
    const unsigned left = frame_width / 2u;
    const unsigned half = frame_height / 2u;

    for (unsigned y = 0; y < frame_height; y++)
    {
        uint32_t *row = &software_frame[(size_t)y * frame_width];

        /* Software frames run top-down, so the first rows are the ones
         * OpenGL's bottom-left origin would call "north". */
        const unsigned band = (y < half) ? 2u : 0u;

        for (unsigned x = 0; x < frame_width; x++)
            row[x] = hw_geometry_pack(&HW_GEOMETRY_QUADRANTS[band + (x < left ? 0u : 1u)]);
    }

    if (sample_video_cb)
        sample_video_cb(software_frame, frame_width, frame_height,
                        (size_t)frame_width * sizeof(uint32_t));
}

static bool hw_geometry_present_video(void)
{
    if (!gl_ready)
    {
        /* No usable context, so repeat whatever the frontend showed last.
         * Reporting a frame we didn't draw would be a lie the tests can't see. */
        if (sample_video_cb)
            sample_video_cb(NULL, frame_width, frame_height, 0);
        return true;
    }

    const struct hw_geometry_size *next =
        &hw_geometry_sizes[sample_frame_count % HW_GEOMETRY_SIZE_COUNT];
    hw_geometry_resize(next->width, next->height);

    /* Run the whole size schedule on the hardware path, then again on the
     * software path, so the frontend meets both and the switch between them. */
    if ((sample_frame_count / HW_GEOMETRY_SIZE_COUNT) % 2u == 1u)
    {
        hw_geometry_present_software();
        return true;
    }

    gl.BindFramebuffer(GL_FRAMEBUFFER, (GLuint)hw_render.get_current_framebuffer());

    /* glClear ignores the viewport but honours the scissor box, so an
     * unscissored clear reaches every texel of the frontend's texture --
     * including the ones outside this frame. */
    gl.Disable(GL_SCISSOR_TEST);
    gl.ClearColor(HW_GEOMETRY_SENTINEL.r, HW_GEOMETRY_SENTINEL.g, HW_GEOMETRY_SENTINEL.b, 1.0f);
    gl.Clear(GL_COLOR_BUFFER_BIT);

    gl.Viewport(0, 0, (GLsizei)frame_width, (GLsizei)frame_height);
    gl.Enable(GL_SCISSOR_TEST);

    const GLsizei left   = (GLsizei)(frame_width / 2u);
    const GLsizei bottom = (GLsizei)(frame_height / 2u);
    const GLsizei right  = (GLsizei)frame_width - left;
    const GLsizei top    = (GLsizei)frame_height - bottom;

    hw_geometry_fill(0, 0, left, bottom, &HW_GEOMETRY_QUADRANTS[0]);
    hw_geometry_fill(left, 0, right, bottom, &HW_GEOMETRY_QUADRANTS[1]);
    hw_geometry_fill(0, bottom, left, top, &HW_GEOMETRY_QUADRANTS[2]);
    hw_geometry_fill(left, bottom, right, top, &HW_GEOMETRY_QUADRANTS[3]);

    gl.Disable(GL_SCISSOR_TEST);

    if (sample_video_cb)
        sample_video_cb(RETRO_HW_FRAME_BUFFER_VALID, frame_width, frame_height, 0);

    return true;
}

const struct sample_core_def sample_core = {
    .reset         = hw_geometry_reset,
    .load_game     = hw_geometry_load_game,
    .present_video = hw_geometry_present_video,
};
