# Developer Bundle Extensions

## Overview

The Developer Bundle Extension (`omni.kit.developer.bundle`) provides a set of developer focused tools designed to enhance the development and debugging process within Omniverse Kit applications. Each of the extensions within the bundle aims streamline a specific aspects of Omniverse application and extension development.

---

## Enabling the Developer Bundle
Most application templates within the Kit App Template repository have `omni.kit.developer.bundle` configured within the `.kit` file by default. The USD Explorer template does not (nor does it ship the Python `Console` window), since it is commonly streamed to reviewers who must not run code on the host. For applications that do not include it, the Developer Bundle can be added temporarily at launch time using the `--dev-bundle` or `-d` flag.

**Linux**
```bash
./repo.sh launch --dev-bundle
```

**Windows**
```powershell
.\repo.bat launch --dev-bundle
```

The `launch` tool will prompt for a selection of a `.kit` file to launch. Select the desired UI based application. The developer bundle is not currently suitable for headless services.

The streaming layers (`default_stream.kit`, `nvcf_stream.kit`) add `omni.kit.developer.bundle`, `omni.kit.window.console`, `omni.kit.window.script_editor` and `omni.kit.debug.vscode` to `app.extensions.excluded`, so these Python execution surfaces are never available to streamed viewers. Keep them excluded in any custom streaming layer.

---

## Developer Bundle Extensions

Developer Utilities are designed to assist developers in various aspects of application development, from debugging to extension management. These utilities offer insight into the internal workings of an application and its extensions.

- **[Developer > Extensions] omni.kit.window.extensions**: The most popular utility, this tool manages available extensions. It provides quick access to the extension registry and local extensions, simplifying the process of adding dependencies for developer extensions and applications.

- **[Developer > Commands] omni.kit.window.commands**: Captures the command history within a running application. It is particularly useful for developers who interact with the UI, allowing them to capture the commands used to execute specific functionalities.

- **[Developer > Script Editor] omni.kit.window.script_editor**: A simplified script editor for running short code snippets directly within the application. It's a helpful tool for testing small pieces of code before integrating them into a project. Additionally, it offers useful sample scripts that can be executed live.

- **[Developer > VS Code Link] omni.kit.debug.vscode**: VSCode python debugger support window.  This utility allows developers to step through their python code in VSCode while running the application.

- **[Developer > Debug Settings] omni.kit.debug.settings**: This utility provides a detailed view of the configurable settings for extensions within an application, making it easier to tweak and optimize extension behavior.

---

**:warning: The Developer Bundle extensions require a UI based application with a menu bar to run properly. They will not work as expected for headless services or in applications that do not display a menu bar**