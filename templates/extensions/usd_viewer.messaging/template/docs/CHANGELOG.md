# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [Unreleased]
### Security
- `openStageRequest` only opens `./samples/...` (inside `omni.usd_viewer.samples`) or locations inside the
  `exts."<extension>".allowedStageRoots` setting; everything else is answered with an `openedStageResult` error.
  Client URLs are no longer expanded with the carb token resolver, and other `./` paths are no longer resolved
  against `${app}/..`.
- Failed loads report the client's requested URL instead of the resolved server path.

## [0.1.1] - 2025-02-13
### Removed
- Redundant openedStageResult event dispatch

## [0.1.0] - 2024-04-26
- Initial version of basic python extension template