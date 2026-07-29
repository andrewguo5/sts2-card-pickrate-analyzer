"""
Patch taxonomy for the STS2 card pick-rate analyzer.

WHY THIS FILE IS HAND-CURATED
-----------------------------
How STS2's versions relate to each other cannot be derived from the version
string. The game ships on two tracks — a beta branch and the main branch — and
only someone following the release notes knows which release incorporated which
beta versions. This file records that knowledge as a single flat, chronological,
append-only list.

THE ONE STRUCTURAL RULE
-----------------------
Each entry is a tuple. Its shape — not its tag — carries the meaning:

    (version, tag)               -> a standalone release (no children)
    (version, tag, [children])   -> a release that INCORPORATED other versions;
                                    the listed versions nest under it in the tree

The `tag` is DECORATIVE — a label shown in the UI, nothing branches on it. What
determines whether a release went "to main" is simply whether a children list is
present (it may be empty: `(version, tag, [])` still means "to main, incorporated
nothing new"). The parser keys off the tuple length, never the tag text.

A version named in some parent's children list ALSO keeps its own top-level row,
so a beta version can appear both standalone and nested under the release that
rolled it up.

TAGS (decorative)
-----------------
  "Beta Patch"   / "Beta Hotfix"  - releases to the beta branch
  "Hotfix"                        - hotfix to main
  "Patch"                         - brings main in line with beta
  "Major Update"                  - large release bringing main in line with beta
Add new tag strings freely; they only affect the displayed label.

HOW TO EDIT
-----------
Append new releases to the END of PATCHES (the list is oldest-first, so newest
lives at the bottom). When a Patch or Major Update ships, add it with the list of
beta versions it incorporated as its third element.


"""

# Oldest-first, append-only. Fill in each tag; add a [children] list to any
# release that brought main in line with beta.
PATCHES = [
    ("v0.98.0",   "Release"),
    ("v0.98.1",   "Hotfix"),
    ("v0.98.2",   "Hotfix"),
    ("v0.98.3",   "Hotfix"),
    ("v0.99.0",   "Beta Patch"),
    ("v0.99.1",   "Patch", ["v0.99.0"]),
    ("v0.100.0",  "Beta Patch"),
    ("v0.101.0",  "Beta Patch"),
    ("v0.102.0",  "Beta Patch"),
    ("v0.103.0",  "Beta Patch"),
    ("v0.103.1",  "Beta Hotfix"),
    ("v0.103.2",  "Major Update 1", [
        "v0.103.1", "v0.103.0", "v0.102.0", "v0.101.0", "v0.100.0"
    ]),
    ("v0.104.0",  "Beta Patch"),
    ("v0.105.0",  "Beta Patch"),
    ("v0.105.1",  "Beta Hotfix"),
    ("v0.106.0",  "Beta Patch"),
    ("v0.106.1",  "Beta Patch"),
    ("v0.107.0",  "Beta Patch"),
    ("v0.107.1",  "Major Update 2", [
        "v0.107.0", "v0.106.1", "v0.106.0", "v0.105.1", "v0.105.0", "v0.104.0"
    ]),
    ("v0.108.0",  "Beta Patch"),
    ("v0.109.0",  "Beta Patch"),
    ("v0.109.1",  "Beta Hotfix"),
]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
# The single structural rule (see module docstring): an entry is a parent iff it
# carries a children list, detected by tuple length — NEVER by the tag string.
_PARENT_TUPLE_LENGTH = 3


def _tag_for(version: str) -> str:
    """Return the decorative tag for a version, or the version itself if unknown."""
    for entry in PATCHES:
        if entry[0] == version:
            return entry[1]
    return version


def build_patch_tree() -> list[dict]:
    """Build the display tree of patches, newest release first.

    The tree mirrors PATCHES but reversed (file order is oldest-first, so the
    newest release leads the returned list). Each node is::

        {"version": str, "tag": str, "children": [ {"version", "tag"}, ... ]}

    A release with a children list becomes a parent node; its children are
    resolved to their own tags and listed in the order given in the taxonomy.
    Standalone releases carry an empty ``children`` list. Every version keeps its
    own top-level node even when it also nests under a parent.
    """
    tree = []
    for entry in PATCHES:
        version, tag = entry[0], entry[1]
        children = []
        if len(entry) == _PARENT_TUPLE_LENGTH:
            children = [
                {"version": child, "tag": _tag_for(child)}
                for child in entry[2]
            ]
        tree.append({"version": version, "tag": tag, "children": children})

    tree.reverse()  # oldest-first taxonomy -> newest-first display
    return tree

