# Streaming Configuration Layers

These `.kit` files, known as `ApplicationLayerTemplates`, are used to define additional functionality added to the base application.

For streaming configuration layers, these templates define and configure the required streaming extensions.

:warning: **Important**: These layers are not standalone application templates. They must be used in conjunction with a base application template.

:lock: **Security**: Streaming layers list developer and Python-executing extensions (developer bundle, console, script editor, extension manager, debug tools) under `[settings.app.extensions] excluded` so they are never enabled for stream viewers. Keep the key spelled `excluded` and do not remove entries; use `repo launch -d` on the non-streaming application when developer tools are needed.
