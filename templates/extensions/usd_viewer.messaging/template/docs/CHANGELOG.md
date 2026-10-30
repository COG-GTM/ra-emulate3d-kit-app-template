# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [0.1.2] - 2026-10-30
### Security
- `openedStageResult` errors return the client's original `url` and a generic error instead of the resolved server path and loader message
- `loadingStateResponse` no longer returns the open stage's root layer identifier

## [0.1.1] - 2025-02-13
### Removed
- Redundant openedStageResult event dispatch

## [0.1.0] - 2024-04-26
- Initial version of basic python extension template