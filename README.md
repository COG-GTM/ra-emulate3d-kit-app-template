# Emulate3D Kit App Sample
This repo is an example of how to build a Kit App which communicates with the Emulate3D World Stage server.

It is based on the 110.1.2 branch in [NVIDIA Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template).
See [Kit-App-Template_README.md](Kit-App-Template_README.md) for the NVIDIA README and [LICENSE](LICENSE) for NVIDIA licensing terms.

This examples contains a pre-made app and extension.
The extension contains the code to connect to the world stage server, found in [Emulate3dPybindExtension.cpp](/source/extensions/rok.emulate3d.python/plugins/rok.emulate3d.python/Emulate3dPybindExtension.cpp).

## Prerequisites
- Prerequisites in the NVIDIA [README](Kit-App-Template_README.md)
- Visual Studio 2022
- Emulate3D 2026 (available via the [PCDC](https://store.sim3d.com/demo3d_2026/product_compatibility_and_download_center))
- Emulate3D.Usd.Sdk 0.0.10 (available via the [PCDC](https://store.sim3d.com/demo3d_2026/product_compatibility_and_download_center))

## Building and launching
- Extract Emulate3D.Usd.Sdk to a known location, eg `C:\Emulate3D.Usd.Sdk`
- In [premake5.lua](source/extensions/rok.emulate3d.python/premake5.lua) replace <Emulate3D.Usd.Sdk directory> with the Emulate3D.Usd.Sdk install path, eg "C:\Emulate3D.Usd.Sdk".
- Run repo.bat with the build argument eg `.\repo.bat build`
- Launch the built app with `.\repo.bat launch`
- Select `ra.emulate3d.web.kit` to launch Omniverse with WebRTC capaibilities, or `rockwellautomation.emulate3d.omniverse.kit`to launch without

### Commandline arguments
Use `/ext/rok.emulate3d.python/url` and `/ext/rok.emulate3d.python/clientName` to auto connect to a url.
For example:
```
.\rockwellautomation.emulate3d.omniverse.kit.bat --/ext/rok.emulate3d.python/url="localhost:9081" --/ext/rok.emulate3d.python/clientName="Client"
```

To connect to an https server that uses a self-signed certificate, also pass `--/ext/rok.emulate3d.python/trustSelfSigned=true`.
Only `true`, `1`, `yes` or `on` (case-insensitive) enable it; any other value, including `"false"` or `0`, keeps certificate verification on.
The flag is ignored for non-https urls, and a warning is logged whenever certificate verification is disabled.
