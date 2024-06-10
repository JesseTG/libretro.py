# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> [!ATTENTION]
> Until libretro.py reaches version 1.x,
> breaking changes may be introduced
> at any time without warning.

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
