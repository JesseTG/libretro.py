from ctypes import CFUNCTYPE, POINTER, Structure, c_bool, c_char_p, c_size_t, c_uint
from dataclasses import dataclass

from libretro.api._utils import FieldsFromTypeHints
from libretro.api.content import retro_game_info

retro_set_eject_state_t = CFUNCTYPE(c_bool, c_bool)
retro_get_eject_state_t = CFUNCTYPE(c_bool)
retro_get_image_index_t = CFUNCTYPE(c_uint)
retro_set_image_index_t = CFUNCTYPE(c_bool, c_uint)
retro_get_num_images_t = CFUNCTYPE(c_uint)
retro_replace_image_index_t = CFUNCTYPE(c_bool, c_uint, POINTER(retro_game_info))
retro_add_image_index_t = CFUNCTYPE(c_bool)
retro_set_initial_image_t = CFUNCTYPE(c_bool, c_uint, c_char_p)
retro_get_image_path_t = CFUNCTYPE(c_bool, c_uint, c_char_p, c_size_t)
retro_get_image_label_t = CFUNCTYPE(c_bool, c_uint, c_char_p, c_size_t)


@dataclass(init=False)
class retro_disk_control_callback(Structure, metaclass=FieldsFromTypeHints):
    set_eject_state: retro_set_eject_state_t
    get_eject_state: retro_get_eject_state_t
    get_image_index: retro_get_image_index_t
    set_image_index: retro_set_image_index_t
    get_num_images: retro_get_num_images_t
    replace_image_index: retro_replace_image_index_t
    add_image_index: retro_add_image_index_t

    def __deepcopy__(self, _):
        return retro_disk_control_callback(
            set_eject_state=self.set_eject_state,
            get_eject_state=self.get_eject_state,
            get_image_index=self.get_image_index,
            set_image_index=self.set_image_index,
            get_num_images=self.get_num_images,
            replace_image_index=self.replace_image_index,
            add_image_index=self.add_image_index,
        )


@dataclass(init=False)
class retro_disk_control_ext_callback(retro_disk_control_callback, metaclass=FieldsFromTypeHints):
    set_initial_image: retro_set_initial_image_t
    get_image_path: retro_get_image_path_t
    get_image_label: retro_get_image_label_t

    def __deepcopy__(self, _):
        return retro_disk_control_ext_callback(
            set_eject_state=self.set_eject_state,
            get_eject_state=self.get_eject_state,
            get_image_index=self.get_image_index,
            set_image_index=self.set_image_index,
            get_num_images=self.get_num_images,
            replace_image_index=self.replace_image_index,
            add_image_index=self.add_image_index,
            set_initial_image=self.set_initial_image,
            get_image_path=self.get_image_path,
            get_image_label=self.get_image_label,
        )


__all__ = [
    "retro_disk_control_callback",
    "retro_disk_control_ext_callback",
    "retro_set_eject_state_t",
    "retro_get_eject_state_t",
    "retro_get_image_index_t",
    "retro_set_image_index_t",
    "retro_get_num_images_t",
    "retro_replace_image_index_t",
    "retro_add_image_index_t",
    "retro_set_initial_image_t",
    "retro_get_image_path_t",
    "retro_get_image_label_t",
]
