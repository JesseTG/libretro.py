# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
