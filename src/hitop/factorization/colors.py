"""Central color rule for rendering factorization hierarchy diagrams.

One shared 24-color palette is applied across every factorization so
diagrams are visually consistent (see docs/factorizations.md). Factor,
Superspectrum, Spectrum, and Subfactor nodes each draw a distinct color
directly from the palette, spread evenly across the whole tree in
depth-first order, so a diagram reads as one smooth gradient sweep no
matter how many such nodes a given factorization has. Component and Trait
nodes are not part of the palette; each takes a lightened, slightly
desaturated shade of its own parent's color, one step per level below the
nearest palette-colored ancestor.
"""

from __future__ import annotations

import colorsys
import copy
from typing import Any

# fmt: off
PALETTE: list[str] = [
    "#1E3A5F", "#264B7D", "#2F5FA3", "#3F7EB8", "#4D98C7", "#4B8CC7",
    "#5A9ED4", "#6AAFE0", "#7ABEE1", "#8ACCE6", "#9EDAED", "#B1E0F0",
    "#9FC0E9", "#AEB8E3", "#BCA2DF", "#CA92DA", "#DDA5DD", "#E7B9DF",
    "#EECAE1", "#F8B7C5", "#FF8FA4", "#FFB3BA", "#FFBCC4", "#FFCCD6",
]
# fmt: on

PALETTE_LEVELS = {"Factor", "Superspectrum", "Spectrum", "Subfactor"}

_LIGHTNESS_STEP = 0.09
_MAX_LIGHTNESS = 0.93
_SATURATION_DECAY = 0.94


def _hex_to_rgb01(color: str) -> tuple[float, float, float]:
    stripped = color.lstrip("#")
    r, g, b = (int(stripped[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return (r, g, b)


def _rgb01_to_hex(rgb: tuple[float, float, float]) -> str:
    clamped = (max(0.0, min(1.0, c)) for c in rgb)
    return "#" + "".join(f"{round(c * 255):02X}" for c in clamped)


def _lighten(color: str, steps: int) -> str:
    """Return a lighter, slightly desaturated shade of ``color``, ``steps`` levels down."""

    if steps <= 0:
        return color
    r, g, b = _hex_to_rgb01(color)
    h, lightness, s = colorsys.rgb_to_hls(r, g, b)
    lightness = min(_MAX_LIGHTNESS, lightness + steps * _LIGHTNESS_STEP)
    s = s * (_SATURATION_DECAY**steps)
    return _rgb01_to_hex(colorsys.hls_to_rgb(h, lightness, s))


def _collect_palette_nodes(node: dict[str, Any], out: list[dict[str, Any]]) -> None:
    if node.get("level") in PALETTE_LEVELS:
        out.append(node)
    for child in node.get("children") or []:
        _collect_palette_nodes(child, out)


def _assign_palette_colors(root: dict[str, Any]) -> None:
    """Spread the palette evenly across every Factor/Superspectrum/Spectrum/Subfactor node.

    Nodes are visited depth-first in the order the tree is written in the
    hierarchy YAML, so the resulting color sweep follows the tree's own
    reading order -- matching how the original HiTOP figures color a whole
    branch consistently from left to right.
    """

    eligible: list[dict[str, Any]] = []
    _collect_palette_nodes(root, eligible)
    count = len(eligible)
    for index, node in enumerate(eligible):
        palette_index = round(index * (len(PALETTE) - 1) / (count - 1)) if count > 1 else 0
        node["color"] = PALETTE[palette_index]


def _fill_derived_colors(node: dict[str, Any], *, parent_color: str | None, depth: int) -> None:
    if node.get("level") in PALETTE_LEVELS:
        color = node["color"]
        depth = 0
    else:
        depth += 1
        color = _lighten(parent_color, depth) if parent_color else None
        node["color"] = color
    for child in node.get("children") or []:
        _fill_derived_colors(child, parent_color=color, depth=depth)


def annotate_colors(hierarchy: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of ``hierarchy`` with a ``color`` field added to every node.

    Factor/Superspectrum/Spectrum/Subfactor nodes each get their own color
    drawn from :data:`PALETTE` (see module docstring for the distribution
    rule). Component/Trait (and any other non-palette ``level``) nodes get
    a lightened shade of their own parent's color, one step per level below
    the nearest palette-colored ancestor.
    """

    tree = copy.deepcopy(hierarchy)
    _assign_palette_colors(tree)
    _fill_derived_colors(tree, parent_color=None, depth=0)
    return tree
