## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
# Standalone tests (no Kit runtime needed):
#   python -m unittest discover -s source/extensions/rok.emulate3d.python/python/tests
import importlib.util
import pathlib
import unittest

_MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "impl" / "settings_parsing.py"
_spec = importlib.util.spec_from_file_location("settings_parsing", _MODULE_PATH)
settings_parsing = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(settings_parsing)

parse_bool_setting = settings_parsing.parse_bool_setting
resolve_trust_self_signed = settings_parsing.resolve_trust_self_signed


class ParseBoolSettingTests(unittest.TestCase):
    def test_false_like_values_are_false(self):
        for value in ["false", "False", "FALSE", "0", "no", "off", "", "  ", "nope", "2", None, False, 0, 2, -1, 0.0, 1.0, [], ["true"], {}]:
            with self.subTest(value=value):
                self.assertIs(parse_bool_setting(value), False)

    def test_true_like_values_are_true(self):
        for value in [True, 1, "true", "True", " TRUE ", "1", "yes", "YES", "on"]:
            with self.subTest(value=value):
                self.assertIs(parse_bool_setting(value), True)


class ResolveTrustSelfSignedTests(unittest.TestCase):
    def test_quoted_false_keeps_verification_on(self):
        self.assertFalse(resolve_trust_self_signed("https://sim.acme.internal:9081", "false"))
        self.assertFalse(resolve_trust_self_signed("https://sim.acme.internal:9081", "0"))

    def test_unset_keeps_verification_on(self):
        self.assertFalse(resolve_trust_self_signed("https://sim.acme.internal:9081", None))

    def test_explicit_true_on_https_disables_verification(self):
        self.assertTrue(resolve_trust_self_signed("https://sim.acme.internal:9081", "true"))
        self.assertTrue(resolve_trust_self_signed(" HTTPS://sim.acme.internal:9081", True))

    def test_non_https_urls_never_trust(self):
        for url in ["http://localhost:9081", "localhost:9081", "", None]:
            with self.subTest(url=url):
                self.assertFalse(resolve_trust_self_signed(url, True))


if __name__ == "__main__":
    unittest.main()
