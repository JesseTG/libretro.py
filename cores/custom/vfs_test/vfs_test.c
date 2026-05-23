/* vfs_test — exercises RETRO_ENVIRONMENT_GET_VFS_INTERFACE (v3). */

#include "sample_common.h"

static struct retro_vfs_interface *vfs;

static bool vfs_load_game(const struct retro_game_info *info)
{
    (void)info;
    struct retro_vfs_interface_info req = {
        .required_interface_version = 3,
        .iface = NULL,
    };
    if (sample_environ_cb(RETRO_ENVIRONMENT_GET_VFS_INTERFACE, &req))
        vfs = req.iface;
    return true;
}

static void vfs_run_frame(void)
{
    if (!vfs || sample_frame_count != 0)
        return;

    struct retro_vfs_file_handle *fh = vfs->open(
        "libretro_py_vfs_test.tmp",
        RETRO_VFS_FILE_ACCESS_READ_WRITE | RETRO_VFS_FILE_ACCESS_UPDATE_EXISTING,
        RETRO_VFS_FILE_ACCESS_HINT_NONE);
    if (!fh)
        return;

    static const char payload[] = "libretro.py vfs round-trip";
    (void)vfs->write(fh, payload, sizeof(payload) - 1);
    (void)vfs->close(fh);
}

const struct sample_core_def sample_core = {
    .load_game = vfs_load_game,
    .run_frame = vfs_run_frame,
};
