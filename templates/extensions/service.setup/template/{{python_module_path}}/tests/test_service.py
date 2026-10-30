# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add support for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
# Import extension python module we are testing with absolute import path, as if we are an external user (other extension)
import tempfile
from pathlib import Path
from types import SimpleNamespace

import carb.settings
import omni.kit.test
import omni.usd
from fastapi import HTTPException
from pydantic import ValidationError

import {{ python_module }}
from {{ python_module }}.service import (
    SETTINGS_PREFIX,
    CubeDataModel,
    generate_cube,
    require_authorized_client,
    resolve_asset_path,
    router,
)


def _request(host, headers=None):
    return SimpleNamespace(client=SimpleNamespace(host=host), headers=headers or {})


# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of the module
# will make it auto-discoverable by omni.kit.test
class Test(omni.kit.test.AsyncTestCaseFailOnLogError):
    # Before running each test
    async def setUp(self):
        self._settings = carb.settings.get_settings()
        self._saved = {name: self._settings.get(f"{SETTINGS_PREFIX}/{name}") for name in ("output_dir", "api_key")}
        self._tmp = tempfile.TemporaryDirectory()
        self._output_dir = Path(self._tmp.name, "out")
        self._settings.set(f"{SETTINGS_PREFIX}/output_dir", str(self._output_dir))
        self._settings.set(f"{SETTINGS_PREFIX}/api_key", "")

    # After running each test
    async def tearDown(self):
        for name, value in self._saved.items():
            self._settings.set(f"{SETTINGS_PREFIX}/{name}", value if value is not None else "")
        self._tmp.cleanup()

    # Test to ensure that the router is properly initialized and not None
    async def test_router_initialization(self):
        # Check that router is not None
        self.assertIsNotNone(router, "Router should be initialized")

        # Optionally, check that router has the endpoint registered (by checking its routes)
        # This step assumes that the route '/generate_cube' should be one of the registered routes
        routes = [route for route in router.routes if route.path == "/generate_cube"]
        self.assertTrue(len(routes) > 0, "The generate_cube endpoint should be registered in the router")

    async def test_resolve_asset_path_stays_in_output_root(self):
        root = self._output_dir
        self.assertEqual(resolve_asset_path(root, "cube_01"), root.resolve() / "cube_01.usda")
        for bad in ("../x", "../../tmp/x", "/tmp/x", "a/b", "a\\b", "..", ".hidden", "", "x" * 65, "c\x00"):
            with self.assertRaises(ValueError, msg=bad):
                resolve_asset_path(root, bad)

    async def test_request_model_rejects_write_location(self):
        with self.assertRaises(ValidationError):
            CubeDataModel(asset_name="cube", asset_write_location="/tmp")
        with self.assertRaises(ValidationError):
            CubeDataModel(asset_name="cube", cube_scale=-1)

    async def test_generate_cube_writes_only_inside_output_dir(self):
        stage_before = omni.usd.get_context().get_stage()
        await generate_cube(CubeDataModel(asset_name="cube"))
        self.assertTrue((self._output_dir / "cube.usda").is_file())
        self.assertIs(omni.usd.get_context().get_stage(), stage_before, "the open stage must not be replaced")

        with self.assertRaises(HTTPException) as ctx:
            await generate_cube(CubeDataModel(asset_name="../../escaped"))
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertFalse(Path(self._tmp.name).parent.joinpath("escaped.usda").exists())

    async def test_authorization(self):
        await require_authorized_client(_request("127.0.0.1"))
        with self.assertRaises(HTTPException) as ctx:
            await require_authorized_client(_request("10.0.0.5"))
        self.assertEqual(ctx.exception.status_code, 403)

        self._settings.set(f"{SETTINGS_PREFIX}/api_key", "s3cret")
        await require_authorized_client(_request("10.0.0.5", {"X-API-Key": "s3cret"}))
        for headers in ({}, {"X-API-Key": "wrong"}):
            with self.assertRaises(HTTPException) as ctx:
                await require_authorized_client(_request("127.0.0.1", headers))
            self.assertEqual(ctx.exception.status_code, 401)
