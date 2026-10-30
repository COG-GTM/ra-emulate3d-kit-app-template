# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [Unreleased]
### Security
- `/generate_cube` writes only inside the configured `output_dir`, validates `asset_name`, no longer accepts
  `asset_write_location`, builds the cube on an in-memory stage instead of replacing the open stage, and requires
  an API key for non-loopback clients.

## [{{ version }}] - 2024-03-13
- Initial version based on kit service extension template
