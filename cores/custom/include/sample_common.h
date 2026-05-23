/* sample_common.h — shared scaffolding for libretro.py custom test cores.
 *
 * Every core in cores/custom/ links against a single sample_common.c that
 * implements the trivial libretro entry points and delegates the
 * interesting parts (env-call registration, load_game, run, serialize)
 * to a per-core ``sample_core`` struct of function pointers.
 *
 * The pattern keeps each core focused on the env call(s) it exercises;
 * any hook left NULL falls through to a no-op default. SAMPLE_CORE_NAME
 * is supplied by the build system via -D and used in retro_system_info.
 */

#ifndef LIBRETRO_PY_SAMPLE_COMMON_H
#define LIBRETRO_PY_SAMPLE_COMMON_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "libretro.h"

/* --- Build-time configuration --------------------------------------------- */

#ifndef SAMPLE_CORE_NAME
#error "SAMPLE_CORE_NAME must be defined (see cores/custom/CMakeLists.txt)."
#endif

#ifndef SAMPLE_CORE_VERSION
#define SAMPLE_CORE_VERSION "0.1"
#endif

#ifndef SAMPLE_CORE_VALID_EXTENSIONS
#define SAMPLE_CORE_VALID_EXTENSIONS ""
#endif

#ifndef SAMPLE_CORE_WIDTH
#define SAMPLE_CORE_WIDTH 256u
#endif

#ifndef SAMPLE_CORE_HEIGHT
#define SAMPLE_CORE_HEIGHT 224u
#endif

#ifndef SAMPLE_CORE_FPS
#define SAMPLE_CORE_FPS 60.0
#endif

#ifndef SAMPLE_CORE_SAMPLE_RATE
#define SAMPLE_CORE_SAMPLE_RATE 30000.0
#endif

#ifndef SAMPLE_CORE_PIXEL_FORMAT
#define SAMPLE_CORE_PIXEL_FORMAT RETRO_PIXEL_FORMAT_RGB565
#endif

/* --- Shared state set by the libretro frontend --------------------------- */

extern retro_environment_t       sample_environ_cb;
extern retro_video_refresh_t     sample_video_cb;
extern retro_audio_sample_t      sample_audio_cb;
extern retro_audio_sample_batch_t sample_audio_batch_cb;
extern retro_input_poll_t        sample_input_poll_cb;
extern retro_input_state_t       sample_input_state_cb;

extern unsigned sample_frame_count;

/* --- Per-core definition -------------------------------------------------- */

struct sample_core_def
{
    void (*init)(void);
    void (*deinit)(void);
    void (*reset)(void);
    void (*register_env_calls)(void);
    bool (*load_game)(const struct retro_game_info *info);
    void (*unload_game)(void);
    void (*run_frame)(void);
    size_t (*serialize_size)(void);
    bool (*serialize)(void *data, size_t size);
    bool (*unserialize)(const void *data, size_t size);
    void *(*get_memory_data)(unsigned id);
    size_t (*get_memory_size)(unsigned id);
};

/* Every custom core defines exactly one of these. */
extern const struct sample_core_def sample_core;

#endif /* LIBRETRO_PY_SAMPLE_COMMON_H */
