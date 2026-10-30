# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import hmac
import ipaddress
import re
from pathlib import Path

import carb.settings
import carb.tokens
from fastapi import Depends, HTTPException, Request
from pxr import Usd, UsdGeom
from pydantic import BaseModel, Field
from pydantic.version import VERSION as PYDANTIC_VERSION
from omni.services.core.routers import ServiceAPIRouter

SETTINGS_PREFIX = "/exts/{{ extension_name }}"
DEFAULT_OUTPUT_DIR = "${data}/{{ extension_name }}/generated"
API_KEY_HEADER = "X-API-Key"
ASSET_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")

router = ServiceAPIRouter(tags=["{{ extension_display_name }}"])


def _setting(name: str):
    return carb.settings.get_settings().get(f"{SETTINGS_PREFIX}/{name}")


def get_output_root() -> Path:
    """Directory that generated assets are written to (setting `output_dir`)."""
    configured = _setting("output_dir") or DEFAULT_OUTPUT_DIR
    return Path(carb.tokens.get_tokens_interface().resolve(configured)).resolve()


def resolve_asset_path(output_root: Path, asset_name: str) -> Path:
    """Return the `.usda` path for `asset_name`, guaranteed to be directly inside `output_root`."""
    if not isinstance(asset_name, str) or not ASSET_NAME_PATTERN.fullmatch(asset_name):
        raise ValueError(
            "asset_name must be 1-64 characters of letters, digits, '_' or '-', starting with a letter or digit"
        )
    root = Path(output_root).resolve()
    asset_path = (root / f"{asset_name}.usda").resolve()
    if asset_path.parent != root:
        raise ValueError("asset_name resolves outside the output directory")
    return asset_path


async def require_authorized_client(request: Request):
    """Require the configured API key; without one, only accept loopback clients."""
    api_key = _setting("api_key") or ""
    if api_key:
        supplied = request.headers.get(API_KEY_HEADER, "")
        if not hmac.compare_digest(supplied.encode("utf-8"), str(api_key).encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        return

    host = request.client.host if request.client else ""
    try:
        if ipaddress.ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    raise HTTPException(status_code=403, detail="Remote access requires an API key to be configured")


class CubeDataModel(BaseModel):
    """Model of a request for generating a cube."""

    if PYDANTIC_VERSION.startswith("1."):
        class Config:
            extra = "forbid"
    else:
        model_config = {"extra": "forbid"}

    asset_name: str = Field(
        default="cube",
        title="Asset Name",
        description=(
            "File name of the asset to be generated (letters, digits, '_' or '-'); .usda will be appended "
            "and the file is written to the service's configured output directory"
        ),
    )

    cube_scale: float = Field(
        default=100,
        gt=0,
        le=1_000_000,
        title="Cube Scale",
        description="Scale of the cube",
    )


@router.post(
    "/generate_cube",
    summary="Generate a cube",
    description="An endpoint to generate a usda file containing a cube of given scale",
    dependencies=[Depends(require_authorized_client)],
)
async def generate_cube(cube_data: CubeDataModel):
    print("[{{ extension_name }}] generate_cube was called")

    output_root = get_output_root()
    try:
        asset_file_path = resolve_asset_path(output_root, cube_data.asset_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Build the cube on a private in-memory stage so the app's open stage is untouched
    stage = Usd.Stage.CreateInMemory()

    # Set the default prim
    default_prim = UsdGeom.Xform.Define(stage, "/World").GetPrim()
    stage.SetDefaultPrim(default_prim)

    # Create cube
    cube = UsdGeom.Cube.Define(stage, "/World/Cube")
    cube.CreateSizeAttr(cube_data.cube_scale)

    # save stage
    output_root.mkdir(parents=True, exist_ok=True)
    if not stage.GetRootLayer().Export(str(asset_file_path)):
        raise HTTPException(status_code=500, detail="Failed to write the generated asset")
    print(f"[{{ extension_name }}] Wrote a cube to this path: {asset_file_path}")
    return f"[{{ extension_name }}] Wrote a cube to {asset_file_path.name}"
