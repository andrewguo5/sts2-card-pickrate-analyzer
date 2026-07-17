#!/usr/bin/env python3
"""Gate test for patch_taxonomy.py — the hand-curated patch list.

WHY THIS EXISTS
---------------
``patch_taxonomy.py`` is edited by hand on patch day (see
``docs/PATCH_RELEASE.md``). A typo there — a malformed tuple, a duplicated
version, a child that names a version no top-level entry defines — would ship a
broken patch tree to production silently. This script is the guard: run it
before pushing to qa or main, and it fails loudly (non-zero exit) on exactly
those errors.

It is a plain executable script on purpose — no pytest dependency — so it runs
anywhere Python does and gates a push via its exit code:

    python3 backend/test_patch_taxonomy.py && git push ...

Each check raises AssertionError with a message that names the offending entry,
so a failure tells you which line of the taxonomy to fix.
"""

import sys
from pathlib import Path

# Allow running from the repo root or from backend/ — patch_taxonomy is a flat
# top-level module in backend/, mirroring how the app imports it.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from patch_taxonomy import PATCHES, build_patch_tree

_STANDALONE_TUPLE_LENGTH = 2
_PARENT_TUPLE_LENGTH = 3


def test_every_entry_is_a_2_or_3_tuple() -> None:
    """Each entry has the shape (version, tag) or (version, tag, [children])."""
    for entry in PATCHES:
        assert isinstance(entry, tuple), (
            f"Entry is not a tuple: {entry!r}"
        )
        assert len(entry) in (_STANDALONE_TUPLE_LENGTH, _PARENT_TUPLE_LENGTH), (
            f"Entry must be a 2- or 3-tuple, got length {len(entry)}: {entry!r}"
        )
        version, tag = entry[0], entry[1]
        assert isinstance(version, str) and version, (
            f"Version must be a non-empty string: {entry!r}"
        )
        assert isinstance(tag, str) and tag, (
            f"Tag must be a non-empty string: {entry!r}"
        )
        if len(entry) == _PARENT_TUPLE_LENGTH:
            assert isinstance(entry[2], list), (
                f"Children (3rd element) must be a list: {entry!r}"
            )
            for child in entry[2]:
                assert isinstance(child, str) and child, (
                    f"Each child must be a non-empty string: {entry!r}"
                )


def test_top_level_versions_are_unique() -> None:
    """No version string appears twice as a top-level entry."""
    seen = set()
    for entry in PATCHES:
        version = entry[0]
        assert version not in seen, (
            f"Duplicate top-level version: {version!r}"
        )
        seen.add(version)


def test_every_child_names_a_top_level_entry() -> None:
    """Every version listed inside a parent's children exists on its own row.

    The taxonomy's structural invariant: a grouped beta version keeps its own
    top-level entry even while it nests under the release that incorporated it.
    A child naming a version with no top-level row is a typo.
    """
    top_level = {entry[0] for entry in PATCHES}
    for entry in PATCHES:
        if len(entry) == _PARENT_TUPLE_LENGTH:
            for child in entry[2]:
                assert child in top_level, (
                    f"Child {child!r} of {entry[0]!r} has no top-level entry"
                )


def test_build_patch_tree_does_not_raise() -> None:
    """The tree builder runs cleanly and returns one node per entry."""
    tree = build_patch_tree()
    assert len(tree) == len(PATCHES), (
        f"Tree has {len(tree)} nodes, expected {len(PATCHES)}"
    )


def main() -> int:
    tests = [
        test_every_entry_is_a_2_or_3_tuple,
        test_top_level_versions_are_unique,
        test_every_child_names_a_top_level_entry,
        test_build_patch_tree_does_not_raise,
    ]
    for test in tests:
        try:
            test()
        except AssertionError as error:
            print(f"FAIL  {test.__name__}\n      {error}")
            return 1
        print(f"ok    {test.__name__}")
    print(f"\nAll {len(tests)} checks passed — patch_taxonomy.py is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
