"""Read the vendored-upstream provenance record.

The JSON file is written by `anticloud.vendor` at clone time. Nothing here is
typed by hand, so the licence and commit shown are always the real ones.
"""

from __future__ import annotations

import json
import os

NAME = "L_VLLM"
SLUG = "vllm-project/vllm"
URL = "https://github.com/vllm-project/vllm"
PROV_FILENAME = ".anticloud-provenance.json"


def project_root() -> str:
    """<project>/src/l_vllm_anticloud/provenance.py -> <project>"""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", ".."))


def upstream_dir() -> str:
    return os.path.join(project_root(), "UPSTREAM")


def load_provenance() -> dict:
    d = {
        "name": NAME,
        "slug": SLUG,
        "url": URL,
        "domain": "",
        "role": "",
        "commit": "",
        "commit_date": "",
        "licence": "not vendored",
        "licence_class": "unknown",
        "size_mb": 0,
    }
    fp = os.path.join(upstream_dir(), PROV_FILENAME)
    if os.path.exists(fp):
        try:
            with open(fp, "r", encoding="utf-8") as fh:
                d.update(json.load(fh))
        except (OSError, ValueError):
            pass
    return d


def is_vendored() -> bool:
    return os.path.isdir(os.path.join(upstream_dir(), ".git"))
