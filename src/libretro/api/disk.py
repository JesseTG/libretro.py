from ctypes import CFUNCTYPE, POINTER, c_bool, c_uint, c_size_t, Structure

from .._utils import FieldsFromTypeHints, String
from .content import retro_game_info

retro_set_eject_state_t = CFUNCTYPE(c_bool, c_bool)
retro_get_eject_state_t = CFUNCTYPE(c_bool)
retro_get_image_index_t = CFUNCTYPE(c_uint)
retro_set_image_index_t = CFUNCTYPE(c_bool, c_uint)
retro_get_num_images_t = CFUNCTYPE(c_uint)


retro_replace_image_index_t = CFUNCTYPE(c_bool, c_uint, POINTER(retro_game_info))
retro_add_image_index_t = CFUNCTYPE(c_bool)
retro_set_initial_image_t = CFUNCTYPE(c_bool, c_uint, String)
retro_get_image_path_t = CFUNCTYPE(c_bool, c_uint, String, c_size_t)
retro_get_image_label_t = CFUNCTYPE(c_bool, c_uint, String, c_size_t)


class retro_disk_control_callback(Structure, metaclass=FieldsFromTypeHints):
    set_eject_state: retro_set_eject_state_t
    get_eject_state: retro_get_eject_state_t
    get_image_index: retro_get_image_index_t
    set_image_index: retro_set_image_index_t
    get_num_images: retro_get_num_images_t
    replace_image_index: retro_replace_image_index_t
    add_image_index: retro_add_image_index_t


class retro_disk_control_ext_callback(retro_disk_control_callback, metaclass=FieldsFromTypeHints):
    set_initial_image: retro_set_initial_image_t
    get_image_path: retro_get_image_path_t
    get_image_label: retro_get_image_label_t


__all__ = [
    "retro_disk_control_callback",
    "retro_disk_control_ext_callback",
    'retro_set_eject_state_t',
    'retro_get_eject_state_t',
    'retro_get_image_index_t',
    'retro_set_image_index_t',
    'retro_get_num_images_t',
    'retro_replace_image_index_t',
    'retro_add_image_index_t',
    'retro_set_initial_image_t',
    'retro_get_image_path_t',
    'retro_get_image_label_t',
]
