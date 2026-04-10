# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> [!ATTENTION]
> Until libretro.py reaches version 1.x,
> breaking changes may be introduced
> at any time without warning.

## [Unreleased]

I'm still here! I've had many "I'll-get-around-to-it-someday" tasks
on my to-do list for libretro.py. Well, _someday has come_.
This release primarily addresses stability and API consistency;
the most notable change is full type coverage.

### Added

- Type annotations to all public-facing types and functions in libretro.py.
  Too many to list here, but the library has 100% coverage.
- Type checking with Pyright to the CI pipeline.
  _All future pull requests must pass type-checking._
- Additional symbols to `libretro.api` to match [`libretro.h`][libretro.h]
- The `libretro.ctypes` module for type declarations
  that describe the behavior documented by [`ctypes`][ctypes]
- Added `PathDriver.file_browser_start_dir`,
  and implement it in `ExplicitPathDriver` and `TempDirPathDriver`.
- Added `libretro.typing`, which contains types that enforce `ctypes`'s
  documented rules statically while falling back to it at runtme.
- Added linting pipelines to GitHub Actions for Python 3.12, 3.13, and 3.14.
  _All future pull requests must pass linting checks for these versions._
- Added types for each VFS operation in `libretro.drivers.vfs.history`.
- Fields to `retro_vfs_file_handle` and `retro_vfs_dir_handle`
  that are helpful for `FileSystemDriver` implementations.
- Add `SessionBuilder.with_rumble`.
- Add `AnySession` as a type alias of `Session` with
  just the base driver protocols as its type parameters.

### Fixed

- Fix a compatibility issue with Python 3.14 due to `FieldsFromTypeHints`
  relying on behavior that was changed since Python 3.12.

### Changed

- **BREAKING:** Raise minimum required Python version to 3.12.
- **BREAKING:** Separate `RumbleDriver` from `InputDriver`.
- **BREAKING:** Make `Session` a subclass of `CompositeEnvironmentDriver`.
- **BREAKING:** Move all libretro callback struct creation
  into `CompositeEnvironmentDriver`.
- **BREAKING:** Move compatibility shims into `libretro.compat`.
- **BREAKING:** Move memory-related constants (e.g. `RETRO_MEMORY_SAVE_RAM`)
  into `libretro.api.memory`.
- **BREAKING:** Change the values of some names in `SensorType`.
- **BREAKING:** Rename `MessageInterface` to `MessageDriver`.
- **BREAKING:** Rename `LoggerMessageInterface` to `LoggerMessageDriver`.
- **BREAKING:** Move `ConstantPowerDriver` into `libretro.drivers.power.constant`.
- **BREAKING:** Remove validation logic from `SensorDriver`.
- **BREAKING:** Rename `FileSystemInterface` to `FileSystemDriver`.
- **BREAKING:** Rename `StandardFileSystemInterface` to `DefaultFileSystemDriver`.
- **BREAKING:** Rename `HistoryFileSystemInterface` to `HistoryFileSystemDriver`.
- Refactor `FileSystemInterface` to primarily expose its VFS methods on itself,
  rather than through `FileHandle` or `DirectoryHandle`
  (although they're still available).
- Make `justfile` recipes operate in the current environment
  instead of forcibly creating a virtual environment.
- Add type parameters to `CompositeEnvironmentDriver` for each driver
  so that test script authors don't have to check classes
  before accessing installed drivers.
- Catch exceptions raised in `EnvironmentDriver`'s callbacks
  (including those returned to the core),
  and allow subclasses to handle those exceptions
  once control returns from the core.
- `Session` re-raises exceptions that occur during callbacks
  once control returns from the core.
- Change all uses of `c_void_p` to `c_void_ptr`,
  to avoid implicit conversions to `int`.
- Allow `TempDirPathDriver` to ignore exceptions that are raised
  while deleting the temporary directories.
- Update required `moderngl-window` version for the `opengl` extra to `3.*`.
- Redefine all function pointer types to use `TypedFunctionPointer`,
  and their arguments to use various helper types like `CIntArg`.
- `PointerState.pointers` is now a `tuple` instead of a `Sequence`.
- Allow `CoreInterface` and `Core`'s `set_...` methods to accept
  Python `Callable`s as well as corresponding function pointers.

### Deprecated

- Deprecate `SessionBuilder` in favor of creating `Session` directly.

### Removed

- **BREAKING:** Remove `GeneratorLocationDriver`.
- **BREAKING:** Remove `retro_log_callback.__call__`.
  It served no purpose as a helper method,
  since the callback is meant for cores.
- Removed `flake8` from the repo's linters.
- Removed the `_type_` field from all `IntEnum` subclasses.

## [0.6.0] - 2025-01-27

### Added

- Added `MicrophoneDriver.microphones` to list all allocated `Microphone`s.
- Added `Session.mic`.

### Changed

- **BREAKING:** Rename `GeneratorCameraDriver` to `IterableCameraDriver`.

## [0.5.0] - 2024-11-30

Thanks to @JSensebe for his contributions!

### Changed

- **BREAKING:** Rename `SensorInterface` to `SensorDriver`.
- **BREAKING:** Rename `GeneratorSensorInterface` to `IterableSensorDriver`
  and some accompanying type aliases.
- **BREAKING:** Decouple `SensorDriver` and `InputDriver` so that
  the former is no longer part of the latter.
- Use `InputDriver.max_users` to filter sensor input
  regardless of the underlying sensor driver.

### Added

- Add `SensorDriver.poll`.
- Add `SessionBuilder.with_sensor`.
- Add `Session.set_controller_port_device`.

### Fixed

- Improved documentation for `IterableSensorDriver`.
- Fix a `GET_VARIABLE` dereference error.

## [0.4.0] - 2024-10-23

### Changed

- **BREAKING:** Rename `RumbleInterface` to `RumbleDriver`.
- **BREAKING:** Rename `DefaultRumbleDriver` to `DictRumbleDriver`.
- **BREAKING:** Rename `GeneratorInputDriver` to `IterableInputDriver`.

### Fixed

- Fix the rumble driver raising an exception when setting the rumble state.

## [0.3.1] - 2024-10-17

### Changed

- Updated moderngl to 5.12.

### Fixed

- Prevented unhandled OpenGL errors in cores from
  cascading into the frontend as exceptions
  raised from `moderngl` or PyOpenGL.

## [0.3.0] - 2024-09-25

### Added

- Add `TempDirPathDriver`.
- Added various runnable scripts for test purposes.
- Add a new guide for taking a capture with RenderDoc.
- Add labels to OpenGL objects created by `ModernGlVideoDriver`.
- Add debug groups to important methods within `ModernGlVideoDriver`.

### Changed

- **BREAKING:** Rename `DefaultPathDriver` to `ExplicitPathDriver`.
- Make `TempDirPathDriver` the default path driver used by `SessionBuilder`.

### Fixed

- Improved documentation for parts of `SessionBuilder` and `VideoDriver`
- Removed a `glClear` call in `ModernGlVideoDriver` that was left in by accident.
- Clear the `glGetError` queue at various places in `ModernGlVideoDriver`
  to prevent PyOpenGL from misreporting errors that came from moderngl or the loaded core.

### Removed

- **BREAKING:** Remove `VideoDriverInitArgs`.

## [0.2.0] - 2024-09-12

Thanks to @JSensebe for his contributions!

### Added

- Add `Language.GALICIAN` and `Language.NORWEGIAN`
  to correspond with additions to `libretro.h`.
- Add a live documentation website [here](https://libretropy.readthedocs.io/en/latest).
  ([#11](https://github.com/JesseTG/libretro.py/issues/11))
- Allow `ArrayVideoDriver.screenshot()` to rotate the returned frame
  ([#3](https://github.com/JesseTG/libretro.py/issues/3))
- Add 16-bit pixel format support to `ArrayVideoDriver.screenshot()`.
  ([#5](https://github.com/JesseTG/libretro.py/issues/5))

### Changed

- **BREAKING:** Rename `KeyboardState.return_` to `KeyboardState.return_key`
- **BREAKING:** Rename `KeyboardState.break_` to `KeyboardState.break_key`

### Fixed

- Fix `Core.unserialize` being unable to accept `bytes` objects.
  ([#4](https://github.com/JesseTG/libretro.py/issues/4))
- Fix an exception when a core sets its geometry before its initial AV info is fetched.
  ([#6](https://github.com/JesseTG/libretro.py/issues/6))
- Fix a crash when a core uses `retro_led_interface`.
  ([#7](https://github.com/JesseTG/libretro.py/issues/7))
- Fix an exception when passing a frame pitch inconsistent with the configured video format.
  ([#8](https://github.com/JesseTG/libretro.py/issues/8))

## [0.1.11] - 2024-06-10

### Changed

- Raise a warning when the core's requested maximum framebuffer size
  is larger than what the OpenGL implementation can provide.

## [0.1.10] - 2024-06-07

### Fixed

- Fix `ModernGlVideoDriver.geometry` having an incorrect return type.
- Fix `ModernGlVideoDriver` failing to import in Python 3.11.

## [0.1.9] - 2024-06-07

### Fixed

- Remove some methods or other constructs that were added in Python 3.12,
  to ensure compatibility with Python 3.11.

## [0.1.8] - 2024-06-05

### Fixed

- Fixed an incorrect `import` shim in `_typing.py`,
  resulting in the library failing to import on Python 3.12.

## [0.1.7] - 2024-06-05

### Changed

- **BREAKING**: Raise the minimum required Python version to 3.11.

### Fixed

- Remove syntax that prevented compatibility with Python 3.10 and 3.11.
- Added aliases to `typing` symbols as needed if using a Python version older than 3.12.
- Added `typing_extensions` as a dependency if using a Python version older than 3.12.

## [0.1.6] - 2024-06-03

### Changed

- Don't catch a failure to import `OpenGL` in `moderngl.py`.

## [0.1.5] - 2024-06-03

### Fixed

- Allow `ModernGlVideoDriver`'s import of PyOpenGL
  to fail with an `AttributeError`.

## [0.1.4] - 2024-06-03

### Fixed

- Prevent a failure to import PyOpenGL from stopping `ModernGlVideoDriver`
  from being imported.

## [0.1.3] - 2024-06-02

### Fixed

- Fixed a bug where logging invalid UTF-8 characters in `UnformattedLogDriver` would raise an exception.
- Fixed a bug where fetching an unset option from a `DictOptionDriver` wouldn't register the default value for next time.
- Fixed a bug where `ModernGlVideoDriver` would try to use OpenGL debugging features even if they weren't available.

## [0.1.2] - 2024-05-31

### Fixed

- Fixed the GLSL shaders used by `ModernGlVideoDriver` not being included in distributions.

## [0.1.1] - 2024-05-31

### Changed

- Added `moderngl`'s `headless` extra when installing this package's `opengl` extra.

### Fixed

- Fixed a bug where `ModernGlVideoDriver` couldn't be used
  without the `moderngl_window` package installed.

## [0.1.0] - 2024-05-31

### Added

- Added OpenGL support via `ModernGlVideoDriver`.
- Added support for switching video drivers at runtime
  using `MultiVideoDriver`.
- Added `pre-commit` hooks to enforce code style.

### Changed

- Added API documentation for `VideoDriver`.
- Allow `VideoDriver.can_dupe` to be settable and deletable.
- Don't allow `VideoDriver.get_system_av_info` to return `None`.
- **BREAKING**: Rename `AbstractSoftwareVideoDriver` to `SoftwareVideoDriver`.

### Fixed

- Swap the red and blue channels in `ArrayVideoDriver`.
- Immediately reinitialize the video driver when a core calls
  `RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO`, as the docs specify.

### Removed

- **BREAKING:** Removed `PillowVideoDriver`; use `ArrayVideoDriver` instead.

## [0.0.1] - 2024-04-22

### Changed

- Allow the callbacks in `Core` to accept `Callable`s with equivalent signatures,
  rather than strictly enforcing the use of the `retro_*` `CFUNCTYPE`s.
- Allow `Core.cheat_set` to accept a `str` as the cheat code.
- **BREAKING**: Don't allow the cheat code passed to `Core.cheat_set`
  to be a `memoryview` or `Buffer`,
  as these don't typically represent strings.

## [0.0.0] - 2024-04-11

### Added

- Everything.

[libretro.h]: https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h
[ctypes]: https://docs.python.org/3/library/ctypes.html