# {{ extension_display_name }} [{{ extension_name }}]

This is an example of a simple Kit Service extension. It is intended to be copied and to serve as a template to create new ones.

## `/generate_cube`

`POST /generate_cube` with `{"asset_name": "cube", "cube_scale": 100}` writes `<asset_name>.usda` to the
directory configured by `exts."{{ extension_name }}".output_dir` (default `${data}/{{ extension_name }}/generated`).
The cube is built on a private in-memory stage, so the stage open in the app is not affected.

- `asset_name` may only contain letters, digits, `_` and `-`; callers cannot choose the output directory.
- With `exts."{{ extension_name }}".api_key` empty (the default) the endpoint only accepts loopback clients.
  Set the key (for example `--/exts/{{ extension_name }}/api_key=<secret>`) to accept remote clients that send it
  in the `X-API-Key` header. If the service sits behind a reverse proxy on the same host, always set a key, since
  proxied requests arrive from loopback.
