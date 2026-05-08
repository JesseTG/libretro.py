Supported Environment Calls
===========================

This page lists the :term:`environment call`s supported by libretro.py
and the driver interfaces that handle them.

.. note::
  The presence of an envcall on this table *only*
  implies that it has a :term:`driver` protocol
  and at least one implementation that's usable for testing.

  This does *not* mean that the driver uses actual hardware resources;
  it just means that the driver is able to convince the :term:`core`
  that it does.


.. list-table::
    :header-rows: 1

    * - Environment Call
      - Implementation
    * - :attr:`~.EnvironmentCall.SET_ROTATION`
      - :attr:`.VideoDriver.rotation`
    * - :attr:`~.EnvironmentCall.GET_OVERSCAN`
      - :attr:`.CompositeEnvironmentDriver.overscan`
    * - :attr:`~.EnvironmentCall.GET_CAN_DUPE`
      - :attr:`.VideoDriver.can_dupe`
    * - :attr:`~.EnvironmentCall.SET_MESSAGE`
      - :meth:`.MessageDriver.set_message`
    * - :attr:`~.EnvironmentCall.SHUTDOWN`
      - :attr:`.CompositeEnvironmentDriver.is_shutdown`
    * - :attr:`~.EnvironmentCall.SET_PERFORMANCE_LEVEL`
      - :attr:`.CompositeEnvironmentDriver.performance_level`
    * - :attr:`~.EnvironmentCall.GET_SYSTEM_DIRECTORY`
      - :attr:`.PathDriver.system_dir`
    * - :attr:`~.EnvironmentCall.SET_PIXEL_FORMAT`
      - :attr:`.VideoDriver.pixel_format`
    * - :attr:`~.EnvironmentCall.SET_INPUT_DESCRIPTORS`
      - :attr:`.InputDriver.descriptors`
    * - :attr:`~.EnvironmentCall.SET_KEYBOARD_CALLBACK`
      - :attr:`.InputDriver.keyboard_callback`
    * - :attr:`~.EnvironmentCall.SET_DISK_CONTROL_INTERFACE`
      - Not supported
    * - :attr:`~.EnvironmentCall.SET_HW_RENDER`
      - :meth:`.VideoDriver.set_context`
    * - :attr:`~.EnvironmentCall.SET_HW_RENDER_EXPERIMENTAL`
      - Not supported
    * - :attr:`~.EnvironmentCall.GET_VARIABLE`
      - :meth:`.OptionDriver.get_variable`
    * - :attr:`~.EnvironmentCall.SET_VARIABLES`
      - :meth:`.OptionDriver.set_variables`
    * - :attr:`~.EnvironmentCall.GET_VARIABLE_UPDATE`
      - :attr:`.OptionDriver.variable_updated`
    * - :attr:`~.EnvironmentCall.SET_SUPPORT_NO_GAME`
      - :attr:`.ContentDriver.support_no_game`
    * - :attr:`~.EnvironmentCall.GET_LIBRETRO_PATH`
      - :attr:`.PathDriver.libretro_path`
    * - :attr:`~.EnvironmentCall.SET_FRAME_TIME_CALLBACK`
      - :attr:`.TimingDriver.frame_time_callback`
    * - :attr:`~.EnvironmentCall.SET_AUDIO_CALLBACK`
      - :attr:`.AudioDriver.callbacks`
    * - :attr:`~.EnvironmentCall.GET_RUMBLE_INTERFACE`
      - :meth:`.RumbleDriver.set_rumble_state`
    * - :attr:`~.EnvironmentCall.GET_INPUT_DEVICE_CAPABILITIES`
      - :attr:`.InputDriver.device_capabilities`
    * - :attr:`~.EnvironmentCall.GET_SENSOR_INTERFACE`
      - :class:`.SensorDriver`
    * - :attr:`~.EnvironmentCall.GET_CAMERA_INTERFACE`
      - Not supported
    * - :attr:`~.EnvironmentCall.GET_LOG_INTERFACE`
      - :class:`.LogDriver`
    * - :attr:`~.EnvironmentCall.GET_PERF_INTERFACE`
      - :class:`.PerfDriver`
    * - :attr:`~.EnvironmentCall.GET_LOCATION_INTERFACE`
      - Not supported
    * - :attr:`~.EnvironmentCall.GET_CORE_ASSETS_DIRECTORY`
      - :attr:`.PathDriver.core_assets_dir`
    * - :attr:`~.EnvironmentCall.GET_SAVE_DIRECTORY`
      - :attr:`.PathDriver.save_dir`
    * - :attr:`~.EnvironmentCall.SET_SYSTEM_AV_INFO`
      - :attr:`.AudioDriver.system_av_info`, :attr:`.VideoDriver.system_av_info`
    * - :attr:`~.EnvironmentCall.SET_PROC_ADDRESS_CALLBACK`
      - :attr:`.CompositeEnvironmentDriver.proc_address_callback`
    * - :attr:`~.EnvironmentCall.SET_SUBSYSTEM_INFO`
      - :attr:`.ContentDriver.subsystem_info`
    * - :attr:`~.EnvironmentCall.SET_CONTROLLER_INFO`
      - :attr:`.InputDriver.controller_info`
    * - :attr:`~.EnvironmentCall.SET_MEMORY_MAPS`
      - :attr:`.CompositeEnvironmentDriver.memory_maps`
    * - :attr:`~.EnvironmentCall.SET_GEOMETRY`
      - :attr:`.VideoDriver.geometry`
    * - :attr:`~.EnvironmentCall.GET_USERNAME`
      - :attr:`.UserDriver.username`
    * - :attr:`~.EnvironmentCall.GET_LANGUAGE`
      - :attr:`.UserDriver.language`
    * - :attr:`~.EnvironmentCall.GET_CURRENT_SOFTWARE_FRAMEBUFFER`
      - :meth:`.VideoDriver.get_software_framebuffer`
    * - :attr:`~.EnvironmentCall.GET_HW_RENDER_INTERFACE`
      - :attr:`.VideoDriver.hw_render_interface`
    * - :attr:`~.EnvironmentCall.SET_SUPPORT_ACHIEVEMENTS`
      - :attr:`.CompositeEnvironmentDriver.support_achievements`
    * - :attr:`~.EnvironmentCall.SET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE`
      - Not supported
    * - :attr:`~.EnvironmentCall.SET_SERIALIZATION_QUIRKS`
      - :attr:`.CompositeEnvironmentDriver.serialization_quirks`
    * - :attr:`~.EnvironmentCall.SET_HW_SHARED_CONTEXT`
      - :attr:`.VideoDriver.shared_context`
    * - :attr:`~.EnvironmentCall.GET_VFS_INTERFACE`
      - :class:`.FileSystemDriver`
    * - :attr:`~.EnvironmentCall.GET_LED_INTERFACE`
      - :meth:`.LedDriver.set_led_state`
    * - :attr:`~.EnvironmentCall.GET_AUDIO_VIDEO_ENABLE`
      - :attr:`.CompositeEnvironmentDriver.av_enable`
    * - :attr:`~.EnvironmentCall.GET_MIDI_INTERFACE`
      - :class:`.MidiDriver`
    * - :attr:`~.EnvironmentCall.GET_FASTFORWARDING`
      - :attr:`.TimingDriver.throttle_state`
    * - :attr:`~.EnvironmentCall.GET_TARGET_REFRESH_RATE`
      - :attr:`.TimingDriver.target_refresh_rate`
    * - :attr:`~.EnvironmentCall.GET_INPUT_BITMASKS`
      - :attr:`.InputDriver.bitmasks_supported`
    * - :attr:`~.EnvironmentCall.GET_CORE_OPTIONS_VERSION`
      - :attr:`.OptionDriver.version`
    * - :attr:`~.EnvironmentCall.SET_CORE_OPTIONS`
      - :meth:`.OptionDriver.set_options`
    * - :attr:`~.EnvironmentCall.SET_CORE_OPTIONS_INTL`
      - :meth:`.OptionDriver.set_options_intl`
    * - :attr:`~.EnvironmentCall.SET_CORE_OPTIONS_DISPLAY`
      - :meth:`.OptionDriver.set_display`
    * - :attr:`~.EnvironmentCall.GET_PREFERRED_HW_RENDER`
      - :attr:`.VideoDriver.preferred_context`
    * - :attr:`~.EnvironmentCall.GET_DISK_CONTROL_INTERFACE_VERSION`
      - Not supported
    * - :attr:`~.EnvironmentCall.SET_DISK_CONTROL_EXT_INTERFACE`
      - Not supported
    * - :attr:`~.EnvironmentCall.GET_MESSAGE_INTERFACE_VERSION`
      - :attr:`.MessageDriver.version`
    * - :attr:`~.EnvironmentCall.SET_MESSAGE_EXT`
      - :meth:`.MessageDriver.set_message`
    * - :attr:`~.EnvironmentCall.GET_INPUT_MAX_USERS`
      - :attr:`.InputDriver.max_users`
    * - :attr:`~.EnvironmentCall.SET_AUDIO_BUFFER_STATUS_CALLBACK`
      - :attr:`.AudioDriver.buffer_status`
    * - :attr:`~.EnvironmentCall.SET_MINIMUM_AUDIO_LATENCY`
      - :attr:`.AudioDriver.minimum_latency`
    * - :attr:`~.EnvironmentCall.SET_FASTFORWARDING_OVERRIDE`
      - :attr:`.TimingDriver.fastforwarding_override`
    * - :attr:`~.EnvironmentCall.SET_CONTENT_INFO_OVERRIDE`
      - :attr:`.ContentDriver.overrides`
    * - :attr:`~.EnvironmentCall.GET_GAME_INFO_EXT`
      - :attr:`.ContentDriver.game_info_ext`
    * - :attr:`~.EnvironmentCall.SET_CORE_OPTIONS_V2`
      - :meth:`.OptionDriver.set_options_v2`
    * - :attr:`~.EnvironmentCall.SET_CORE_OPTIONS_V2_INTL`
      - :meth:`.OptionDriver.set_options_v2_intl`
    * - :attr:`~.EnvironmentCall.SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK`
      - :attr:`.OptionDriver.update_display_callback`
    * - :attr:`~.EnvironmentCall.SET_VARIABLE`
      - :meth:`.OptionDriver.set_variable`
    * - :attr:`~.EnvironmentCall.GET_THROTTLE_STATE`
      - :attr:`.TimingDriver.throttle_state`
    * - :attr:`~.EnvironmentCall.GET_SAVESTATE_CONTEXT`
      - :attr:`.CompositeEnvironmentDriver.savestate_context`
    * - :attr:`~.EnvironmentCall.GET_HW_RENDER_CONTEXT_NEGOTIATION_INTERFACE_SUPPORT`
      - Not supported
    * - :attr:`~.EnvironmentCall.GET_JIT_CAPABLE`
      - :attr:`.CompositeEnvironmentDriver.jit_capable`
    * - :attr:`~.EnvironmentCall.GET_MICROPHONE_INTERFACE`
      - :class:`.MicrophoneDriver`
    * - :attr:`~.EnvironmentCall.SET_NETPACKET_INTERFACE`
      - Not supported
    * - :attr:`~.EnvironmentCall.GET_DEVICE_POWER`
      - :attr:`.PowerDriver.device_power`
    * - :attr:`~.EnvironmentCall.GET_PLAYLIST_DIRECTORY`
      - :attr:`.PathDriver.playlist_dir`
    * - :attr:`~.EnvironmentCall.GET_FILE_BROWSER_START_DIRECTORY`
      - :attr:`.PathDriver.file_browser_start_dir`
