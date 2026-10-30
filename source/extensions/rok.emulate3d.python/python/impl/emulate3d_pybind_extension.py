## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.ext
import omni.usd
import threading
import carb.settings
from .._rok_emulate3d_python_lib import *
from .connection_ui import ConnectionUI
from .settings_parsing import resolve_trust_self_signed

# Global public interface object.
_bound_interface = None

# Public API.
def get_bound_interface() -> IRokEmulate3dPythonInterface:
    return _bound_interface


# Use the extension entry points to acquire and release the interface.
class Emulate3DPybindExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()

        global _bound_interface
        _bound_interface = acquire_bound_interface()
        self.subscription_handle = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(self.on_update, name="UPDATE_SUB")
        self._connection_ui = None
        self.act_as_client = True

        settings = carb.settings.get_settings()
        self.url = settings.get("/ext/rok.emulate3d.python/url")
        self.clientName = settings.get("/ext/rok.emulate3d.python/clientName")
        self.trustSelfSigned = resolve_trust_self_signed(self.url, settings.get("/ext/rok.emulate3d.python/trustSelfSigned"))

    def on_startup(self, _ext_id):
        self.update_rtx_settings()
        self.find_create_default_stage()
        print("[rok.emulate3d.python] Plugin started")
        if self.act_as_client:
            # Create and initialize connection UI
            self._connection_ui = ConnectionUI(get_bound_interface(), self.find_create_default_stage)
            if (self.url and self.clientName):
                self._connection_ui._add_server_connection(self.clientName, self.url, self.trustSelfSigned, True)

        else:
            context = omni.usd.get_context()
            interface = get_bound_interface()
            print("[rok.emulate3d.python] Starting gRPC server...")
            stage_id = context.get_stage_id()
            interface.start_server(stage_id)

    # RTX Real-Time 2.0 is the default render mode only since Kit 108. Users upgrading from our
    # old Kit 107 app carry over a user.config.json where it's disabled, so the will app
    # open in RTX - Minimal by default. Rather than make users enable it manually (via Preferences ->
    # Rendering), we can force it on here at the extensions startup.
    def update_rtx_settings(self):
        # Only write a setting when it isn't already correct since setting an rtx related option
        # displays a 'takes effect next launch' popup, which we'd rather not display every app startup.
        settings = carb.settings.get_settings()
        rtx_settings = {
            "/persistent/rtx/modes/rt2/enabled": True,   # Enable the Real-Time 2.0 mode
            "/persistent/rtx/modes/pt/enabled": True,    # Enable the Interactive (Path Tracing) mode
            "/rtx/rendermode": "RaytracedLighting",      # Make Real-Time 2.0 the active mode
        }
        for key, value in rtx_settings.items():
            if settings.get(key) != value:
                settings.set(key, value)

    def on_update(self, p):
        interface = get_bound_interface()
        interface.process_frames()

    def on_shutdown(self):
        if self._connection_ui:
            self._connection_ui.destroy()
            self._connection_ui = None
        global _bound_interface
        release_bound_interface(_bound_interface)
        _bound_interface = None

    def find_create_default_stage(self):
        context = omni.usd.get_context()
        usd_stage = context.get_stage()
        if not usd_stage:
            print("[rok.emulate3d.python] USD stage is not initialized, creating a new one.")
            context.new_stage("TestStage.usd")
            usd_stage = context.get_stage()
            default_prim = usd_stage.DefinePrim("/World", "Xform")
            usd_stage.SetDefaultPrim(default_prim)

            # Add a default dome light to illuminate the scene
            from pxr import UsdLux, Gf, Sdf
            light = UsdLux.DomeLight.Define(usd_stage, "/World/DomeLight")
            light.CreateIntensityAttr(1000)
            light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
            # Make the dome light invisible to camera to avoid white background
            light.GetPrim().CreateAttribute("visibleInPrimaryRay", Sdf.ValueTypeNames.Bool).Set(False)
        return usd_stage