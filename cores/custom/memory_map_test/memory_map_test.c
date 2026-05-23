/* memory_map_test — exercises SET_MEMORY_MAPS and core memory access. */

#include "sample_common.h"

#define SYSTEM_RAM_SIZE 65536u

static uint8_t system_ram[SYSTEM_RAM_SIZE];

static bool memmap_load_game(const struct retro_game_info *info)
{
    (void)info;
    static const struct retro_memory_descriptor descs[] = {
        {
            .flags      = RETRO_MEMDESC_SYSTEM_RAM,
            .ptr        = system_ram,
            .offset     = 0,
            .start      = 0,
            .select     = 0,
            .disconnect = 0,
            .len        = SYSTEM_RAM_SIZE,
            .addrspace  = NULL,
        },
    };
    struct retro_memory_map map = {
        .descriptors     = descs,
        .num_descriptors = 1,
    };
    sample_environ_cb(RETRO_ENVIRONMENT_SET_MEMORY_MAPS, &map);
    return true;
}

static void *memmap_get_memory_data(unsigned id)
{
    return (id == RETRO_MEMORY_SYSTEM_RAM) ? (void *)system_ram : NULL;
}

static size_t memmap_get_memory_size(unsigned id)
{
    return (id == RETRO_MEMORY_SYSTEM_RAM) ? SYSTEM_RAM_SIZE : 0u;
}

const struct sample_core_def sample_core = {
    .load_game       = memmap_load_game,
    .get_memory_data = memmap_get_memory_data,
    .get_memory_size = memmap_get_memory_size,
};
