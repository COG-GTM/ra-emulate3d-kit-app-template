## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import omni.ui as ui
import omni.kit.ui
import omni.usd
import asyncio
from .settings_parsing import url_is_https

_STYLE_CONNECTION_ROW = {
    "Rectangle": {"background_color": 0x00000000},
    "Rectangle:hovered": {"background_color": 0x20FFFFFF},
}
_STYLE_ERROR_LABEL = {
    "color": 0xFF6B6BFF
}
_STYLE_DISCONNECT_BUTTON = {
    "Button": {"background_color": 0xFF1E1E8B},
    "Button:hovered": {"background_color": 0xFF2828C8},
}
_STYLE_TRUST_CERT_PANEL = {
    "background_color": 0xFF333333,
    "border_radius": 4,
}

class ServerConnection:
    def __init__(self, clientName: str, url: str):
        self.clientName = clientName
        self.url = url

    def __str__(self) -> str:
        return f"{self.clientName}@{self.url}"


class ConnectionUI:
    """UI and client management for Emulate3D connection settings."""

    def __init__(self, bound_interface, stage_creation_callback):
        self._bound_interface = bound_interface
        self._stage_creation_callback = stage_creation_callback
        self._window = None
        self._toolbar_button = None
        self._url_field = None
        self._name_field = None
        self._trust_cert_row = None
        self._trust_cert_checkbox = None
        self._error_label = None
        self._connections_collapsable = None
        self._connections_container = None
        self._connections: list[ServerConnection] = []
        self.create_ui()

    def create_ui(self):
        """Create the menu item and connection settings window."""
        # Add menu item
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._toolbar_button = editor_menu.add_item(
                "Window/Emulate3D Connection Settings",
                self._show_window,
            )

        # Create UI window
        self._window = ui.Window("Emulate3D Connection Settings", width=485, height=435, padding_x=20, padding_y=20)

        with self._window.frame:
            with ui.VStack(spacing=16):
                with ui.VStack(spacing=4, height=48):
                    ui.Label("Server URL", alignment=ui.Alignment.LEFT_CENTER)
                    self._url_field = ui.StringField(height=30)
                    self._url_field.model.set_value("https://localhost:9081")
                    self._url_field.model.add_value_changed_fn(self._on_url_changed)

                with ui.VStack(spacing=4, height=48):
                    ui.Label("Client Name", alignment=ui.Alignment.LEFT_CENTER)
                    self._name_field = ui.StringField(height=30)
                    self._name_field.model.set_value("Omniverse")

                with ui.VStack(spacing=6):
                    self._trust_cert_row = ui.ZStack(height=0)
                    with self._trust_cert_row:
                        ui.Rectangle(style=_STYLE_TRUST_CERT_PANEL)
                        with ui.HStack(spacing=4, style={"margin": 4}):
                            self._trust_cert_checkbox = ui.CheckBox(width=20, height=20, alignment=ui.Alignment.CENTER)
                            ui.Label("Trust self-signed certificates", alignment=ui.Alignment.LEFT_CENTER)
                    self._trust_cert_row.visible = self._url_is_https(self._url_field.model.get_value_as_string())

                    ui.Button("Connect", clicked_fn=self._on_connect_clicked, height=40)
                    self._error_label = ui.Label("", visible=False, word_wrap=True, height=0, alignment=ui.Alignment.CENTER, style=_STYLE_ERROR_LABEL)
                    self._connections_collapsable = ui.CollapsableFrame()
                    with self._connections_collapsable:
                        self._connections_container = ui.Frame()

        asyncio.ensure_future(self._build_active_connections())

    def destroy(self):
        """Clean up UI resources."""
        if self._toolbar_button:
            editor_menu = omni.kit.ui.get_editor_menu()
            if editor_menu:
                editor_menu.remove_item(self._toolbar_button)
            self._toolbar_button = None
        if self._window:
            self._window.destroy()
            self._window = None

    async def _build_active_connections(self):
        await omni.kit.app.get_app().next_update_async()
        self._connections_collapsable.title = f"Active Connections ({len(self._connections)})"

        self._connections_container.clear()
        with self._connections_container:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=2):
                    for connection in self._connections:
                        with ui.ZStack(height=28):
                            ui.Rectangle(style=_STYLE_CONNECTION_ROW)
                            with ui.HStack():
                                ui.Spacer(width=6)
                                ui.Label(str(connection), alignment=ui.Alignment.LEFT_CENTER)
                                ui.Button("Disconnect", width=90, style=_STYLE_DISCONNECT_BUTTON, clicked_fn=lambda c=connection: self._on_disconnect_clicked(c))

    def _show_window(self, *args):
        """Show the connection settings window."""
        if self._window:
            self._window.visible = True

    def _url_is_https(self, url: str) -> bool:
        return url_is_https(url)

    def _url_has_protocol(self, url: str) -> bool:
        lowered = url.strip().lower()
        return lowered.startswith("http://") or lowered.startswith("https://")

    def _on_url_changed(self, model):
        """Show/hide the self-signed certificate checkbox depending on if _url_field is a https url"""
        if self._trust_cert_row is not None:
            self._trust_cert_row.visible = self._url_is_https(model.get_value_as_string())

    def _on_connect_clicked(self):
        """Handle connect button click."""
        self._set_error_text("")
        url = self._url_field.model.get_value_as_string().strip()
        name = self._name_field.model.get_value_as_string().strip()

        if not url:
            self._set_error_text("Server URL cannot be empty")
            return
        if not name:
            self._set_error_text("Client Name cannot be empty")
            return
        if not self._url_has_protocol(url):
            self._set_error_text("Server URL must start with http:// or https://")
            return
        if any(c.url == url for c in self._connections):
            self._set_error_text(f"Already connected to {url}")
            return

        trust_self_signed = self._url_is_https(url) and self._trust_cert_checkbox.model.get_value_as_bool()
        self._add_server_connection(name, url, trust_self_signed)

    def _add_server_connection(self, name: str, url: str, trust_self_signed: bool = False, closeOnSuccess=False):
        trust_self_signed = trust_self_signed is True and self._url_is_https(url)
        self._url_field.model.set_value(url)
        self._name_field.model.set_value(name)
        self._trust_cert_checkbox.model.set_value(trust_self_signed)

        # Ensure stage exists
        self._stage_creation_callback()

        context = omni.usd.get_context()
        stage_id = context.get_stage_id()

        if trust_self_signed:
            carb.log_warn(f"[rok.emulate3d.python] TLS certificate verification is DISABLED for {url} (trust self-signed certificates).")
        elif self._url_is_https(url):
            print(f"[rok.emulate3d.python] TLS certificate verification is enabled for {url}.")
        print(f"[rok.emulate3d.python] Connecting to {url}...")
        if self._bound_interface.connect_client(name, stage_id, url, trust_self_signed):
            print(f"[rok.emulate3d.python] Connected to {url} successfully.")
            self._connections.append(ServerConnection(name, url))
            if closeOnSuccess:
                self._window.visible = False
            asyncio.ensure_future(self._build_active_connections())
        else:
            print(f"[rok.emulate3d.python] Failed to connect to {url}. Check if the server is running and the URL is correct.")
            error_msg = f"Failed to connect to {url}"
            # Suggest enabling trust self-signed certificates if the URL is https and the checkbox is not checked
            if self._url_is_https(url) and not trust_self_signed:
                error_msg += ". If the server uses a self-signed certificate, enable 'Trust self-signed certificates' and reconnect."
            self._set_error_text(error_msg)

    def _on_disconnect_clicked(self, connection: ServerConnection):
        """Handle disconnect button click for a specified connection"""
        print(f"[rok.emulate3d.python] Disconnecting from {connection.url}...")
        self._bound_interface.disconnect_client(connection.url)
        self._connections.remove(connection)
        asyncio.ensure_future(self._build_active_connections())

    def _set_error_text(self, text: str):
        self._error_label.text = text
        self._error_label.visible = len(text) > 0
