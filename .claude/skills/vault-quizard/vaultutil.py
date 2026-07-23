"""Small helpers shared by build_quiz.py and reject.py."""
from __future__ import annotations

import os
from typing import Optional


def find_vault_root(start: str) -> Optional[str]:
    """Walk up from `start` looking for the `.obsidian` marker directory.

    Returns the vault root, or None if no `.obsidian` is found on the way up.
    Reliable when the start path is inside the vault (a draft file, or a CWD
    under the vault); returns None otherwise, so callers can fall back to an
    explicit `--vault-root` or the `NOTES_PHD_VAULT` env var.
    """
    d = os.path.abspath(start)
    if os.path.isfile(d):
        d = os.path.dirname(d)
    while True:
        if os.path.isdir(os.path.join(d, ".obsidian")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def resolve_vault_root(explicit: Optional[str], start: str) -> Optional[str]:
    """Vault root from, in order: an explicit flag, $NOTES_PHD_VAULT, discovery."""
    if explicit:
        return os.path.abspath(explicit)
    env = os.environ.get("NOTES_PHD_VAULT")
    if env:
        return os.path.abspath(env)
    return find_vault_root(start)


def normalize_ws(s: str) -> str:
    """Collapse every run of whitespace to a single space.

    Used so a quote that wraps across a line break in the markdown source still
    matches -- line wrapping is a formatting artifact, not a content difference.
    This is the only tolerance applied; it does not weaken the fabrication check,
    since you cannot fabricate a passage and have it pass on whitespace alone.
    """
    return " ".join(s.split())
