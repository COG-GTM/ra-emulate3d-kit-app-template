# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""Allowlist check for stage URLs requested by a streaming client."""

import os
import posixpath
from typing import Iterable, Optional, Tuple
from urllib.parse import unquote, urlsplit

_Location = Tuple[str, str, str]  # (scheme, netloc, normalized path); scheme "" means a local path


def _normalize(url: str) -> Optional[_Location]:
    if not url or "${" in url or "\x00" in url:
        return None

    try:
        parts = urlsplit(url.replace("\\", "/"))
        scheme = parts.scheme.lower()
        netloc = parts.netloc.lower()
        parts.port  # raises ValueError on a malformed port
    except ValueError:
        return None

    # No scheme, a Windows drive letter ("c:/..."), or file: is a local path.
    if not scheme or len(scheme) == 1 or scheme == "file":
        if scheme == "file":
            if netloc not in ("", "localhost") or parts.query or parts.fragment:
                return None
            path = unquote(parts.path)
            if len(path) > 2 and path[0] == "/" and path[2] == ":":
                path = path[1:]  # file:///C:/dir -> C:/dir
        else:
            path = url
        return "", "", os.path.normcase(os.path.realpath(path))

    # Queries and fragments could select a different resource than the checked path.
    if not netloc or parts.query or parts.fragment or "?" in url or "#" in url:
        return None
    path = unquote(parts.path).replace("\\", "/")
    if any(segment in (".", "..") for segment in path.split("/")):
        return None
    path = posixpath.normpath("/" + path.lstrip("/"))
    return scheme, netloc, path


def _is_within(root: str, path: str, local: bool) -> bool:
    if local:
        try:
            return os.path.commonpath([root, path]) == root
        except ValueError:  # different drives
            return False
    return path == root or path.startswith(root.rstrip("/") + "/")


def is_stage_url_allowed(url: str, allowed_roots: Iterable[str]) -> bool:
    """Return True if ``url`` is one of ``allowed_roots`` or located beneath one of them.

    Roots and URLs must already have Kit tokens resolved. Remote roots match on
    scheme, host and path prefix; local roots match on the real (symlink-resolved) path.
    Empty or unresolved roots never match. Every file under a root is trusted, so
    roots must not be writable by untrusted users.
    """
    target = _normalize(url)
    if target is None:
        return False
    for root in allowed_roots:
        allowed = _normalize(root)
        if allowed is None or allowed[:2] != target[:2]:
            continue
        if _is_within(allowed[2], target[2], local=not allowed[0]):
            return True
    return False
