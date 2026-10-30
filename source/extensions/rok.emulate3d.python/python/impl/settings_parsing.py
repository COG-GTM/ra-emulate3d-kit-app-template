## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
_TRUE_STRINGS = frozenset({"true", "1", "yes", "on"})


def parse_bool_setting(value) -> bool:
    """Strictly parse a Kit setting as a boolean.

    Only a real ``True``, the integer ``1`` or a string in ``_TRUE_STRINGS`` (case-insensitive)
    is treated as True. Everything else, including "false", "0", "no", "" and None, is False.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in _TRUE_STRINGS
    return False


def url_is_https(url) -> bool:
    return isinstance(url, str) and url.strip().lower().startswith("https://")


def resolve_trust_self_signed(url, requested) -> bool:
    """Only skip certificate verification when explicitly requested for an https url."""
    return url_is_https(url) and parse_bool_setting(requested)
