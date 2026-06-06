"""Test-time namespace bridge for the prototype checkout.

The future `synapt-runner` package is intentionally PEP 420 compliant and does
not ship `synapt/__init__.py`. The current development environment may already
have the recall package installed as a regular `synapt` package, which shadows
this checkout during direct prototype tests. Extend that package path only in
tests so the prototype can be verified before the real repo carve-out.
"""

from __future__ import annotations

from pathlib import Path

import synapt


LOCAL_SYNAPT_NAMESPACE = Path(__file__).resolve().parents[1] / "synapt"

if hasattr(synapt, "__path__"):
    namespace_path = str(LOCAL_SYNAPT_NAMESPACE)
    if namespace_path not in synapt.__path__:
        synapt.__path__.append(namespace_path)
