# USD Viewer Messaging Extension [omni.usd_viewer.messaging]

This is an example of pure python Kit extension. It is intended to be copied and to serve as a template to create new ones.

## Allowed stage locations

`openStageRequest` only opens stages located under one of the roots listed in the
`/exts/<extension_name>/allowedStageRoots` setting (by default the USD Viewer samples).
Requests for any other URL are rejected with an `openedStageResult` error. Add your own
trusted directories or Nucleus folders in the app `.kit` file, for example:

```toml
[settings.exts."<extension_name>"]
allowedStageRoots = [
    "${omni.usd_viewer.samples}/samples_data",
    "omniverse://nucleus.example.com/Projects/Viewer",
]
```
