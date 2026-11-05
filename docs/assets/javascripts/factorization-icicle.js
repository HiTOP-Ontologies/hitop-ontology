/**
 * Generic D3 icicle/partition renderer for HiTOP factorization trees.
 *
 * Input is the JSON produced by scripts/generate_factorization_diagram_data.py
 * (see factorizations/<id>/v<n>/<version>_diagram.json): a tree of
 * {label, level, code, kind, branch, children}, where `branch` is the index
 * of the node's top-level ancestor and is constant through a whole subtree.
 *
 * Rows are assigned by semantic `level` (Factor < Superspectrum < Spectrum <
 * Subfactor < {Component, Trait} -- the same order docs/codesystem.md uses
 * for the F/S/P/U/C/T segment letters), never by raw tree depth: two nodes
 * with the same level always share a row, and e.g. a Superspectrum can
 * never land on the same row as a Spectrum even though both can be direct
 * children of the same parent (the tree is intentionally irregular --
 * branches skip levels, see docs/factorizations.md section 4). Component
 * and Trait are the one deliberate exception: they share a single bottom
 * row, matching the official HiTOP figure's own combined "Homogeneous
 * Symptom Components / Maladaptive Traits" row. A level string outside
 * this vocabulary falls back to one row below its parent's row.
 *
 * Column widths are NOT plain d3.partition() proportions. A pure
 * leaf-count-proportional icicle gives a node with few descendants (e.g. a
 * Subfactor with only three Components) an arbitrarily thin slice. Instead
 * every node's minimum width is measured bottom-up first from its own
 * *longest single word* (not its whole label -- the label itself is
 * allowed to wrap across lines, see below), and widths are then allocated
 * top-down: each sibling gets at least its own minimum, and whatever width
 * is left over is distributed proportionally to leaf count exactly like
 * the old icicle did. A tree whose combined minimums exceed the viewport
 * renders wider than it and scrolls horizontally rather than shrinking
 * anything below one word wide -- see computeMinWidths/layoutWidths.
 *
 * Text layout: every label (structural box or leaf-group entry) is real
 * HTML in a <foreignObject>, not SVG <text> -- this is what lets the
 * browser's own line-breaking and dictionary hyphenation
 * (`hyphens: auto`, `lang="en"`) wrap a label across lines and, only if a
 * single word still doesn't fit, hyphenate it at a linguistically correct
 * break point, instead of ever truncating with an ellipsis. Each box's
 * row height is measured from its actual wrapped content at its final
 * allocated width (a hidden probe element, remeasured on every resize),
 * so nothing is ever clipped, scrollable, or cut off -- everything is
 * always fully visible.
 *
 * Color: every node's fill comes straight from its own `color` field in the
 * source JSON, pre-computed by the single, cross-factorization color rule
 * in hitop.factorization.colors (see docs/factorizations.md section 7):
 * one fixed 24-color palette spread evenly across every Factor/
 * Superspectrum/Spectrum/Subfactor node, and Component/Trait nodes taking a
 * lightened shade of their own parent's color. This renderer does not
 * recompute or reinterpret that color in any way -- it is the single
 * source of truth so every consumer of the diagram JSON renders identical
 * colors. Text color is still picked per-box at render time from the
 * fill's relative luminance, so label contrast stays correct regardless of
 * how light or dark a given palette color is.
 *
 * Structure: a thin gap is left between rows so a connector line can be
 * drawn from each parent box down into every child box/leaf-group, even
 * when they are several rows apart (a skipped level). A node marked
 * `provisional: true` in the source hierarchy.yaml is marked *only* by a
 * dashed incoming connector line for an individually-boxed node (the box
 * itself carries no extra outline), or, inside a leaf list, by a
 * dashed-outline pill instead of a solid-fill one -- a leaf-group member
 * has no connector line of its own, so the pill outline is its sole
 * marker.
 *
 * Leaf density: a parent's children that are leaves (no further children)
 * are never given one sliver box each. They are grouped by shared `level`
 * into one leaf-group box spanning just the width that run occupies (not
 * the parent's full width, so sibling subtrees keep their own share), and
 * presented as a wrapped group of small pill-shaped tags (the same
 * flex-wrap "chip group" pattern Material Design, Carbon, and most other
 * major design systems use for a dense set of short labels) rather than a
 * plain wrapped sentence -- each tag is individually click/keyboard-
 * focusable, and always normal weight, non-italic, at a small size
 * matching the structural-box level caption, since a Component/Trait is
 * not a structural row header.
 *
 * Interactivity: the legend beneath the diagram always reflects the
 * children of whatever node was last clicked (defaulting to the factor's
 * own top-level branches before any click) -- see renderLegend/selectNode.
 * A share/download toolbar sits above the diagram; downloads offer SVG,
 * PNG, and PDF, all built from a second, <foreignObject>-free render of
 * the same layout (see buildExportSvg's docstring for why that's a
 * separate code path rather than a clone of the interactive SVG).
 *
 * One renderer serves every factorization: call
 * renderFactorizationIcicle(container, data) once per page with that
 * factorization's own diagram JSON.
 *
 * Depends on a globally loaded d3 (v7) script tag preceding this file.
 */
(function (global) {
  "use strict";

  var MIN_ROW_HEIGHT = 40;
  var ROW_GAP = 15;
  var SIB_GAP = 1.5;

  var LABEL_WIDTH_PADDING = 20;
  var CHIP_WIDTH_PADDING = 16;
  var GROUP_MIN_WIDTH = 64;

  // Canonical row order, matching docs/codesystem.md's F/S/P/U/C/T segment
  // sequence, except Component and Trait are deliberately merged into one
  // shared bottom row (see module docstring).
  var LEVEL_RANK_MAP = {
    factor: 0,
    superspectrum: 1,
    spectrum: 2,
    subfactor: 3,
    component: 4,
    trait: 4,
  };

  // Only Component and Trait leaves are ever merged into one shared
  // leaf-group box (see module docstring). A Factor/Superspectrum/Spectrum/
  // Subfactor node is always its own individual box, even if it happens to
  // be a leaf (no children) and even if a sibling shares its exact level --
  // e.g. "Sexual Problems" and "Eating Pathology" are both leaf Subfactors
  // but must stay two separate boxes, never combined into one.
  var GROUPABLE_LEAF_LEVELS = { component: true, trait: true };
  function isGroupableLeafLevel(levelLabel) {
    return !!GROUPABLE_LEAF_LEVELS[String(levelLabel || "").trim().toLowerCase()];
  }

  var LABEL_FONT = 11;
  var CHIP_FONT_SIZE = 9.5;

  // Static-export sizing (see buildExportSvg). Kept at module scope since
  // none of it depends on a particular diagram instance.
  var EXPORT_LABEL_PAD_X = 8;
  var EXPORT_LABEL_PAD_Y = 6;
  var EXPORT_SUBLABEL_FONT = 9;
  var EXPORT_SUBLABEL_GAP = 3;
  var EXPORT_CHIP_ROW_GAP = 3;
  var EXPORT_CHIP_COL_GAP = 5;
  var SVG_NS = "http://www.w3.org/2000/svg";

  var A4_WIDTH_MM = 210;
  var A4_HEIGHT_MM = 297;
  var A4_MARGIN_MM = 10;
  var PNG_DPI = 200;
  var PDF_DPI = 200;
  var MM_PER_INCH = 25.4;
  var CSS_PX_PER_INCH = 96;
  var PT_PER_INCH = 72;

  function canonicalRank(levelLabel) {
    var key = String(levelLabel || "").trim().toLowerCase();
    return Object.prototype.hasOwnProperty.call(LEVEL_RANK_MAP, key)
      ? LEVEL_RANK_MAP[key]
      : -1;
  }

  function textColorFor(fillHex) {
    var rgb = d3.rgb(fillHex);
    var luminance = (0.2126 * rgb.r + 0.7152 * rgb.g + 0.0722 * rgb.b) / 255;
    return luminance > 0.6 ? "#12141a" : "#ffffff";
  }

  function renderPlaceholder(container, meta) {
    container.innerHTML = "";
    var box = document.createElement("div");
    box.className = "hitop-icicle-placeholder";
    box.textContent =
      (meta && meta.label ? meta.label : "This factorization") +
      ": the tree has not been curated yet (meta.status: " +
      (meta && meta.status ? meta.status : "draft") +
      "). The diagram appears once hierarchy is populated in the YAML file.";
    container.appendChild(box);
  }

  function describeNode(dData) {
    var parts = [];
    parts.push("<strong>" + dData.label + "</strong>");
    parts.push("Level: " + dData.level);
    parts.push("Code: " + dData.code);
    if (dData.kind === "collection") {
      parts.push("Kind: factorization-local grouping (skos:Collection)");
    }
    if (dData.kind === "partial") {
      parts.push("Kind: partial overlap with a core concept (not equivalence)");
      const escapeText = value => String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
      if (dData.id) parts.push("Local ID: " + escapeText(dData.id));
      if (dData.mapping_note) parts.push("Mapping: " + escapeText(dData.mapping_note));
    }
    if (dData.bridge && dData.bridge.length) {
      parts.push("Bridge: " + dData.bridge.join(", "));
    }
    if (dData.provisional) {
      parts.push("Status: provisional (shown with dashed outlines or connectors)");
    }
    return parts.join("<br>");
  }

  /**
   * Reorder a raw hierarchy node's children so every run of leaf children
   * sharing the same `level` is contiguous (grouped in first-appearance
   * order), followed by non-leaf children (each recursively prepared the
   * same way). This is what lets the renderer later collapse each
   * contiguous leaf run into one bounding box spanning exactly that run's
   * own allocated width, without overlapping a non-leaf sibling's column.
   * Returns a new plain-object tree; leaf objects themselves are reused,
   * not mutated.
   */
  function prepareTree(node) {
    var children = node.children || [];
    if (!children.length) return node;

    var leaves = [];
    var nonLeaves = [];
    children.forEach(function (c) {
      if (c.children && c.children.length) {
        nonLeaves.push(prepareTree(c));
      } else {
        leaves.push(c);
      }
    });

    var order = [];
    var buckets = {};
    leaves.forEach(function (c) {
      var key = c.level;
      if (!buckets[key]) {
        buckets[key] = [];
        order.push(key);
      }
      buckets[key].push(c);
    });
    var groupedLeaves = [];
    order.forEach(function (key) {
      groupedLeaves = groupedLeaves.concat(buckets[key]);
    });

    var copy = {};
    for (var k in node) {
      if (k !== "children") copy[k] = node[k];
    }
    copy.children = groupedLeaves.concat(nonLeaves);
    return copy;
  }

  /**
   * Ordered left-to-right slots for `dNode`'s children: a `"node"` slot per
   * non-leaf child, or per leaf child whose level is not groupable (see
   * GROUPABLE_LEAF_LEVELS -- it gets its own individual box exactly like a
   * non-leaf node), and one `"leaf"` slot per contiguous run of same-level
   * Component/Trait leaf children (rendered as a single leaf-group box).
   * `value` is each slot's leaf-count share, used to distribute any width
   * left over after minimums are met. Marks every leaf absorbed into a
   * `"leaf"` slot with `__grouped = true`, so the caller knows which nodes
   * do *not* get their own individual box.
   */
  function computeSlots(dNode) {
    var kids = dNode.children || [];
    var slots = [];
    var i = 0;
    while (i < kids.length) {
      var c = kids[i];
      var isLeaf = !(c.children && c.children.length);
      if (!isLeaf || !isGroupableLeafLevel(c.data.level)) {
        slots.push({ kind: "node", node: c, value: c.value });
        i += 1;
        continue;
      }
      var level = c.data.level;
      var runEnd = i;
      while (
        runEnd + 1 < kids.length &&
        !(kids[runEnd + 1].children && kids[runEnd + 1].children.length) &&
        kids[runEnd + 1].data.level === level &&
        isGroupableLeafLevel(kids[runEnd + 1].data.level)
      ) {
        runEnd += 1;
      }
      var members = kids.slice(i, runEnd + 1);
      members.forEach(function (m) {
        m.__grouped = true;
      });
      slots.push({
        kind: "leaf",
        level: level,
        rank: members[0].levelRank,
        members: members,
        value: members.length,
      });
      i = runEnd + 1;
    }
    return slots;
  }

  var measureSvg = null;
  var measureTextEl = null;
  function measureTextWidth(text, fontSize, fontWeight) {
    if (!measureSvg) {
      measureSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      measureSvg.setAttribute("width", "0");
      measureSvg.setAttribute("height", "0");
      measureSvg.style.position = "absolute";
      measureSvg.style.visibility = "hidden";
      measureTextEl = document.createElementNS("http://www.w3.org/2000/svg", "text");
      measureSvg.appendChild(measureTextEl);
      document.body.appendChild(measureSvg);
    }
    measureTextEl.setAttribute("font-size", fontSize);
    measureTextEl.setAttribute("font-weight", fontWeight || 400);
    measureTextEl.setAttribute(
      "font-family",
      '-apple-system, "Segoe UI", Roboto, Arial, sans-serif'
    );
    measureTextEl.textContent = text;
    return measureTextEl.getComputedTextLength();
  }

  /** Width of `label`'s single longest word -- what the label's box must be
   * at least as wide as, since the rest is free to wrap onto more lines. */
  function longestWordWidth(label, fontSize, fontWeight) {
    var words = String(label).split(/\s+/).filter(Boolean);
    if (!words.length) return measureTextWidth(label, fontSize, fontWeight);
    var max = 0;
    words.forEach(function (w) {
      max = Math.max(max, measureTextWidth(w, fontSize, fontWeight));
    });
    return max;
  }

  /**
   * Greedy word-wrap of `text` into lines no wider than `maxWidth`, measured
   * with the same `measureTextWidth` the interactive layout uses. Used only
   * by the static export renderer (see buildExportSvg): wrapping there is
   * computed once, up front, into fixed line positions, rather than left to
   * the viewer's own text engine -- see that function's docstring for why.
   */
  function wrapWords(text, maxWidth, fontSize, fontWeight) {
    var words = String(text).split(/\s+/).filter(Boolean);
    if (!words.length) return [""];
    var lines = [];
    var current = "";
    words.forEach(function (w) {
      var candidate = current ? current + " " + w : w;
      if (current && measureTextWidth(candidate, fontSize, fontWeight) > maxWidth) {
        lines.push(current);
        current = w;
      } else {
        current = candidate;
      }
    });
    if (current) lines.push(current);
    return lines;
  }

  /**
   * Pack `members` (leaf-group chip data) into rows no wider than
   * `maxWidth`, mirroring the on-screen flex-wrap chip list's `gap: 3px 5px`
   * -- used only by the static export renderer (see buildExportSvg).
   */
  function packChips(members, maxWidth) {
    var COL_GAP = 5;
    var rows = [];
    var row = [];
    var rowWidth = 0;
    members.forEach(function (m) {
      var chipWidth = measureTextWidth(m.data.label, CHIP_FONT_SIZE, 400) + CHIP_WIDTH_PADDING;
      var addWidth = row.length ? chipWidth + COL_GAP : chipWidth;
      if (row.length && rowWidth + addWidth > maxWidth) {
        rows.push(row);
        row = [];
        rowWidth = 0;
        addWidth = chipWidth;
      }
      row.push({ member: m, width: chipWidth });
      rowWidth += addWidth;
    });
    if (row.length) rows.push(row);
    return rows;
  }

  /**
   * Bottom-up: every node's minimum pixel width, and the ordered slot list
   * each internal node lays its children out with (see computeSlots). A
   * structural node's minimum is its own longest word's width (its full
   * label is free to wrap across lines, see module docstring) or the sum
   * of its slots' minimums, whichever is larger -- so a parent is by
   * construction always at least as wide as what its children need, which
   * is what lets layoutWidths (below) guarantee every descendant its
   * minimum without anything ever overflowing or being cut off.
   */
  function computeMinWidths(root) {
    root.eachAfter(function (d) {
      var ownWidth =
        Math.max(longestWordWidth(d.data.label, LABEL_FONT, 700) + LABEL_WIDTH_PADDING, GROUP_MIN_WIDTH);
      if (d.children && d.children.length) {
        d.__slots = computeSlots(d);
        d.__leafGroups = d.__slots.filter(function (s) {
          return s.kind === "leaf";
        });
        var childrenMin = 0;
        d.__slots.forEach(function (slot) {
          if (slot.kind === "node") {
            slot.minWidth = slot.node.__minWidth;
          } else {
            var longest = 0;
            slot.members.forEach(function (m) {
              longest = Math.max(longest, measureTextWidth(m.data.label, CHIP_FONT_SIZE, 400));
            });
            slot.minWidth = Math.max(longest + CHIP_WIDTH_PADDING, GROUP_MIN_WIDTH);
          }
          childrenMin += slot.minWidth;
        });
        d.__minWidth = Math.max(ownWidth, childrenMin);
      } else {
        d.__minWidth = ownWidth;
        d.__leafGroups = [];
      }
    });
  }

  /**
   * Distribute `totalWidthPx` across `slots`: every slot gets at least its
   * own `minWidth`, and whatever remains is split among the rest
   * proportionally to `value` (leaf count) -- the same fixed-point
   * "water-filling" resolution CSS flexbox uses for min-basis tracks. Sets
   * `slot.__widthPx` on each slot. layoutWidths never calls this with less
   * than the sum of the slots' minimums, by construction of
   * computeMinWidths above.
   */
  function allocateSlotWidths(slots, totalWidthPx) {
    var n = slots.length;
    var assigned = new Array(n).fill(false);
    var remaining = totalWidthPx;
    var remainingValue = 0;
    slots.forEach(function (s) {
      remainingValue += s.value;
    });

    var changed = true;
    var guard = 0;
    while (changed && guard < n + 2) {
      changed = false;
      guard += 1;
      for (var i = 0; i < n; i++) {
        if (assigned[i]) continue;
        var share = remainingValue > 0 ? (remaining * slots[i].value) / remainingValue : 0;
        if (share < slots[i].minWidth) {
          slots[i].__widthPx = slots[i].minWidth;
          assigned[i] = true;
          remaining = Math.max(remaining - slots[i].minWidth, 0);
          remainingValue -= slots[i].value;
          changed = true;
        }
      }
    }

    var unassignedCount = 0;
    for (var k = 0; k < n; k++) {
      if (!assigned[k]) unassignedCount += 1;
    }
    for (var j = 0; j < n; j++) {
      if (!assigned[j]) {
        slots[j].__widthPx =
          remainingValue > 0
            ? (remaining * slots[j].value) / remainingValue
            : remaining / unassignedCount;
      }
    }
  }

  /**
   * Top-down: walk from `node` (given its own allocated `x0px`/`widthPx`)
   * and allocate pixel positions/widths to every descendant, recursing
   * into "node" slots and just positioning "leaf" slots (they are
   * terminal, rendered as one leaf-group box).
   */
  function layoutWidths(node, x0px, widthPx) {
    node.__x0px = x0px;
    node.__widthPx = widthPx;
    if (!node.__slots) return;

    allocateSlotWidths(node.__slots, widthPx);
    var cursor = x0px;
    node.__slots.forEach(function (slot) {
      if (slot.kind === "node") {
        layoutWidths(slot.node, cursor, slot.__widthPx);
      } else {
        slot.__x0px = cursor;
      }
      cursor += slot.__widthPx;
    });
  }

  /**
   * Measure the rendered height of an HTML block at a fixed pixel width,
   * via a hidden, off-screen probe built with `buildFn` -- used for both
   * structural labels and leaf-group tag lists so every box's row can be
   * sized to fit its actual wrapped content exactly once, with no
   * scrolling or clipping.
   */
  function measureHtmlHeight(boxWidthPx, buildFn) {
    var probe = document.createElement("div");
    probe.className = "hitop-icicle-box-content";
    probe.style.position = "absolute";
    probe.style.visibility = "hidden";
    probe.style.left = "-9999px";
    probe.style.top = "0";
    probe.style.width = Math.max(boxWidthPx, 0) + "px";
    probe.style.height = "auto";
    buildFn(probe);
    document.body.appendChild(probe);
    var height = probe.scrollHeight;
    document.body.removeChild(probe);
    return height;
  }

  function appendLabelBlock(parent, label, sublabel) {
    var l = document.createElement("div");
    l.className = "hitop-icicle-label-html";
    l.lang = "en";
    l.textContent = label;
    parent.appendChild(l);
    if (sublabel) {
      var s = document.createElement("div");
      s.className = "hitop-icicle-sublabel-html";
      s.textContent = sublabel;
      parent.appendChild(s);
    }
  }

  function appendChipList(parent) {
    var list = document.createElement("div");
    list.className = "hitop-icicle-chip-list";
    parent.appendChild(list);
    return list;
  }

  /** Vertically-centered, pre-wrapped label (+ optional level caption) as
   * fixed <tspan> lines -- see buildExportSvg's docstring. Module-level:
   * takes only plain values, no per-instance state. */
  function appendExportLabel(g, boxWidth, boxHeight, label, sublabel, color) {
    var maxWidth = Math.max(boxWidth - EXPORT_LABEL_PAD_X * 2, 4);
    var lines = wrapWords(label, maxWidth, LABEL_FONT, 700);
    var lineHeight = LABEL_FONT * 1.25;
    var subLineHeight = sublabel ? EXPORT_SUBLABEL_FONT * 1.2 : 0;
    var blockHeight = lines.length * lineHeight + (sublabel ? EXPORT_SUBLABEL_GAP + subLineHeight : 0);
    var blockTop = Math.max((boxHeight - blockHeight) / 2, EXPORT_LABEL_PAD_Y);

    var text = document.createElementNS(SVG_NS, "text");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-size", LABEL_FONT);
    text.setAttribute("font-weight", "700");
    text.setAttribute("fill", color);
    lines.forEach(function (line, i) {
      var tspan = document.createElementNS(SVG_NS, "tspan");
      tspan.setAttribute("x", boxWidth / 2);
      tspan.setAttribute("y", blockTop + lineHeight * (i + 0.82));
      tspan.textContent = line;
      text.appendChild(tspan);
    });
    g.appendChild(text);

    if (!sublabel) return;
    var sub = document.createElementNS(SVG_NS, "text");
    sub.setAttribute("x", boxWidth / 2);
    sub.setAttribute(
      "y",
      blockTop + lines.length * lineHeight + EXPORT_SUBLABEL_GAP + subLineHeight * 0.78
    );
    sub.setAttribute("text-anchor", "middle");
    sub.setAttribute("font-size", EXPORT_SUBLABEL_FONT);
    sub.setAttribute("font-weight", "500");
    sub.setAttribute("fill", color);
    sub.setAttribute("opacity", "0.85");
    sub.textContent = sublabel;
    g.appendChild(sub);
  }

  /**
   * A shrink-only scale factor (never > 1: fitting a diagram to A4 should
   * shrink an oversized one, not blow up a small one past its natural
   * size) so `contentWpx`x`contentHpx` -- read as ordinary CSS pixels, i.e.
   * 96px/inch, matching how every other size in this renderer is already
   * interpreted -- would still fit inside an A4 page's printable area
   * (page size minus a margin on all sides) in *some* orientation. Tries
   * both orientations and keeps the larger resulting scale (landscape, in
   * practice, for this diagram's wide aspect ratio).
   *
   * This only decides how large the diagram becomes -- the exported
   * PNG/PDF is then sized exactly to that scaled diagram (see
   * exportPngBlob/exportPdfBytes below), not padded out to A4's full
   * physical size, so the file's own dimensions are exactly the diagram's,
   * flush in the top-left corner rather than centered in leftover page
   * space.
   */
  function computeA4Scale(contentWpx, contentHpx) {
    function fitFor(pageWmm, pageHmm) {
      var availWmm = pageWmm - A4_MARGIN_MM * 2;
      var availHmm = pageHmm - A4_MARGIN_MM * 2;
      var contentWmm = (contentWpx / CSS_PX_PER_INCH) * MM_PER_INCH;
      var contentHmm = (contentHpx / CSS_PX_PER_INCH) * MM_PER_INCH;
      return Math.min(availWmm / contentWmm, availHmm / contentHmm, 1);
    }
    return Math.max(fitFor(A4_WIDTH_MM, A4_HEIGHT_MM), fitFor(A4_HEIGHT_MM, A4_WIDTH_MM));
  }

  /** Rasterize `svgMarkup` onto a canvas sized `targetWpx`x`targetHpx`,
   * filled with `bgColor` first (SVG has no inherent background). Safe from
   * the canvas-tainting restriction only because the export SVG has no
   * <foreignObject> -- see buildExportSvg's docstring. */
  function rasterizeSvgToCanvas(svgMarkup, targetWpx, targetHpx, bgColor) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(
        new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" })
      );
      var img = new Image();
      img.onload = function () {
        var canvas = document.createElement("canvas");
        canvas.width = Math.max(Math.round(targetWpx), 1);
        canvas.height = Math.max(Math.round(targetHpx), 1);
        var ctx = canvas.getContext("2d");
        if (bgColor) {
          ctx.fillStyle = bgColor;
          ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        URL.revokeObjectURL(url);
        resolve(canvas);
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error("The diagram could not be rasterized."));
      };
      img.src = url;
    });
  }

  function canvasToBlob(canvas, type, quality) {
    return new Promise(function (resolve, reject) {
      canvas.toBlob(
        function (blob) {
          blob ? resolve(blob) : reject(new Error("Export failed."));
        },
        type,
        quality
      );
    });
  }

  /**
   * A minimal, hand-written single-page PDF wrapping one JPEG image --
   * intentionally not a real vector PDF (the export SVG this is built from
   * *is* vector, but re-deriving a compliant vector content stream from it
   * is a disproportionate amount of extra machinery here). PDF's
   * `/Filter /DCTDecode` accepts a standard JPEG byte stream directly, so
   * `canvas.toBlob("image/jpeg")`'s output can be embedded as-is.
   * Structure follows the PDF 1.4 spec's minimal single-image-page layout:
   * Catalog -> Pages -> Page -> (XObject image, content stream).
   */
  function buildSinglePageImagePdf(jpegBytes, imgWpx, imgHpx, pageWpt, pageHpt, x, y, w, h) {
    var enc = new TextEncoder();
    var chunks = [];
    var offsets = [];
    var pos = 0;

    function push(bytes) {
      chunks.push(bytes);
      pos += bytes.length;
    }
    function pushText(str) {
      push(enc.encode(str));
    }
    function beginObj(num) {
      offsets[num] = pos;
      pushText(num + " 0 obj\n");
    }
    function pad10(n) {
      var s = String(Math.round(n));
      while (s.length < 10) s = "0" + s;
      return s;
    }

    pushText("%PDF-1.4\n");
    push(new Uint8Array([0x25, 0xe2, 0xe3, 0xcf, 0xd3, 0x0a])); // binary-content marker comment

    beginObj(1);
    pushText("<< /Type /Catalog /Pages 2 0 R >>\nendobj\n");

    beginObj(2);
    pushText("<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n");

    beginObj(3);
    pushText(
      "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 " +
        pageWpt +
        " " +
        pageHpt +
        "] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    );

    beginObj(4);
    pushText(
      "<< /Type /XObject /Subtype /Image /Width " +
        imgWpx +
        " /Height " +
        imgHpx +
        " /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length " +
        jpegBytes.byteLength +
        " >>\nstream\n"
    );
    push(new Uint8Array(jpegBytes));
    pushText("\nendstream\nendobj\n");

    var content = "q\n" + w + " 0 0 " + h + " " + x + " " + y + " cm\n/Im0 Do\nQ";
    beginObj(5);
    pushText("<< /Length " + content.length + " >>\nstream\n" + content + "\nendstream\nendobj\n");

    var xrefStart = pos;
    var count = 6;
    pushText("xref\n0 " + count + "\n");
    pushText("0000000000 65535 f \n");
    for (var i = 1; i < count; i++) {
      pushText(pad10(offsets[i]) + " 00000 n \n");
    }
    pushText("trailer\n<< /Size " + count + " /Root 1 0 R >>\nstartxref\n" + xrefStart + "\n%%EOF");

    var total = 0;
    chunks.forEach(function (c) {
      total += c.length;
    });
    var out = new Uint8Array(total);
    var o = 0;
    chunks.forEach(function (c) {
      out.set(c, o);
      o += c.length;
    });
    return out;
  }

  var toastEl = null;
  function showToast(message) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "hitop-icicle-toast";
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = message;
    requestAnimationFrame(function () {
      toastEl.classList.add("is-visible");
    });
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(function () {
      toastEl.classList.remove("is-visible");
    }, 2600);
  }

  function triggerDownload(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 4000);
  }

  function copyLinkFallback(url) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard
        .writeText(url)
        .then(function () {
          showToast("Link copied to clipboard.");
        })
        .catch(function () {
          window.prompt("Copy link:", url);
        });
    }
    window.prompt("Copy link:", url);
    return Promise.resolve();
  }

  /**
   * Render one factorization's icicle diagram into `container`.
   *
   * @param {Element|string} container DOM node or CSS selector to render into.
   * @param {Object} data Parsed diagram JSON ({meta, hierarchy}).
   */
  function renderFactorizationIcicle(container, data) {
    var el = typeof container === "string" ? document.querySelector(container) : container;
    if (!el) return;

    if (!data || !data.hierarchy) {
      renderPlaceholder(el, data && data.meta);
      return;
    }

    el.innerHTML = "";
    var wrapper = document.createElement("div");
    wrapper.className = "hitop-icicle-wrapper";

    var toolbar = document.createElement("div");
    toolbar.className = "hitop-icicle-toolbar";
    toolbar.innerHTML =
      '<button type="button" class="hitop-icicle-btn" data-role="share" title="Share diagram" aria-label="Share diagram">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M12 15V4" /><path d="M7.5 8.5 12 4l4.5 4.5" /><path d="M5 13v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" />' +
      "</svg><span>Share</span></button>" +
      '<div class="hitop-icicle-menu">' +
      '<button type="button" class="hitop-icicle-btn hitop-icicle-btn-primary" data-role="download-trigger" aria-haspopup="true" aria-expanded="false" title="Download diagram" aria-label="Download diagram">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M12 4v11" /><path d="M7.5 11.5 12 16l4.5-4.5" /><path d="M5 19h14" />' +
      "</svg><span>Download</span>" +
      '<svg class="hitop-icicle-menu-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6" /></svg>' +
      "</button>" +
      '<div class="hitop-icicle-menu-list" role="menu" hidden>' +
      '<button type="button" class="hitop-icicle-menu-item" role="menuitem" data-format="svg"><span>SVG</span><span class="hitop-icicle-menu-item-hint">Vector, lossless</span></button>' +
      '<button type="button" class="hitop-icicle-menu-item" role="menuitem" data-format="png"><span>PNG</span><span class="hitop-icicle-menu-item-hint">Scaled to fit A4</span></button>' +
      '<button type="button" class="hitop-icicle-menu-item" role="menuitem" data-format="pdf"><span>PDF</span><span class="hitop-icicle-menu-item-hint">Print-ready, A4</span></button>' +
      "</div></div>";

    var svgHost = document.createElement("div");
    svgHost.className = "hitop-icicle-svg-host";
    var legend = document.createElement("div");
    legend.className = "hitop-icicle-legend";
    var detail = document.createElement("div");
    detail.className = "hitop-icicle-detail";
    detail.innerHTML =
      "<em>Click a node or focus it with the mouse or keyboard " +
      "to see its level, code, and provenance.</em>";
    wrapper.appendChild(toolbar);
    wrapper.appendChild(svgHost);
    wrapper.appendChild(legend);
    wrapper.appendChild(detail);
    el.appendChild(wrapper);

    var root = d3.hierarchy(prepareTree(data.hierarchy), function (d) {
      return d.children;
    });
    root.sum(function (d) {
      return d.children && d.children.length ? 0 : 1;
    });

    // Row = semantic level (docs/codesystem.md order, Component/Trait
    // merged), never raw tree depth.
    root.eachBefore(function (d) {
      var known = canonicalRank(d.data.level);
      d.levelRank = known >= 0 ? known : d.parent ? d.parent.levelRank + 1 : 0;
    });

    // Minimum widths (bottom-up, container-size independent) -- computed
    // once; only the top-down pixel allocation re-runs on resize.
    computeMinWidths(root);

    var nodes = root.descendants();
    // Every node gets its own individual box, except a Component/Trait leaf
    // absorbed into a leaf-group (computeSlots marks those __grouped) --
    // this includes non-Component/Trait leaves like a leaf Subfactor (e.g.
    // "Sexual Problems"), which must stay their own box, never merged with
    // a sibling that happens to share the same level (see module docstring).
    var internalNodes = nodes.filter(function (d) {
      return !d.__grouped;
    });

    // Compact away any canonical row with nothing in it for this specific
    // tree (e.g. a factorization that never uses "Superspectrum").
    var usedRanks = {};
    nodes.forEach(function (d) {
      usedRanks[d.levelRank] = true;
    });
    var sortedRanks = Object.keys(usedRanks)
      .map(Number)
      .sort(function (a, b) {
        return a - b;
      });
    var rowOfRank = {};
    sortedRanks.forEach(function (r, i) {
      rowOfRank[r] = i;
    });
    var maxRow = sortedRanks.length - 1;

    // The node the legend currently reflects. Defaults to the root (the
    // factor itself), so the legend starts out showing its top-level
    // branches; a click on any node re-points it there, and a
    // resize-triggered redraw re-renders the legend from this same node so
    // the user's selection survives.
    var activeNode = root;

    // The most recent draw()'s row geometry and connector data, kept around
    // so buildExportSvg (see below) can lay out a static export without
    // recomputing layout -- refreshed on every draw(), including a
    // resize-triggered one, so an export always reflects the current size.
    var lastDraw = null;

    /** Legend: one swatch per child of `node`, using that child's own
     * palette color -- the factor's top-level branches by default, or
     * whatever node was last clicked. A leaf with no children renders a
     * short explanatory placeholder instead of an empty bar. */
    function renderLegend(node) {
      var children = (node && node.children) || [];
      legend.innerHTML = "";
      if (!children.length) {
        var empty = document.createElement("span");
        empty.className = "hitop-icicle-legend-empty";
        empty.textContent =
          node && node !== root
            ? "No further sublevels below “" + node.data.label + "”."
            : "No top-level branches.";
        legend.appendChild(empty);
        return;
      }
      children.forEach(function (child) {
        var swatch = document.createElement("span");
        swatch.className = "hitop-icicle-legend-item";
        var dot = document.createElement("span");
        dot.className = "hitop-icicle-legend-swatch";
        dot.style.background = child.data.color;
        var label = document.createElement("span");
        label.textContent = child.data.label;
        swatch.appendChild(dot);
        swatch.appendChild(label);
        legend.appendChild(swatch);
      });
    }

    /** Hover preview: updates the detail text only, leaving the legend and
     * the persistent selection untouched so passing the mouse over sibling
     * nodes doesn't make the legend flicker. */
    function previewNode(dNode) {
      detail.innerHTML = describeNode(dNode.data);
    }

    /** Click/keyboard selection: updates the detail text, re-points the
     * legend at `dNode`'s own children (see renderLegend), and -- for a
     * node with its own box -- marks that box active. */
    function selectNode(dNode, cellSelection) {
      activeNode = dNode;
      detail.innerHTML = describeNode(dNode.data);
      renderLegend(dNode);
      if (cellSelection) {
        cellSelection.classed("is-active", function (n) {
          return n === dNode;
        });
      }
    }

    function draw() {
      svgHost.innerHTML = "";
      var containerWidth = Math.max(svgHost.clientWidth || el.clientWidth || 960, 320);
      // Every node gets at least its own minimum width (see module
      // docstring): the diagram grows past the viewport and scrolls
      // horizontally, rather than shrinking any label narrower than one
      // word, if the tree's combined minimums exceed the available space.
      var width = Math.max(containerWidth, root.__minWidth);
      layoutWidths(root, 0, width);

      var rowHeight = [];
      for (var i = 0; i <= maxRow; i++) rowHeight[i] = MIN_ROW_HEIGHT;

      internalNodes.forEach(function (d) {
        var boxWidthPx = Math.max(d.__widthPx - SIB_GAP, 0);
        d.__contentHeight = measureHtmlHeight(boxWidthPx, function (probe) {
          appendLabelBlock(probe, d.data.label, d.data.level);
        });
        var row = rowOfRank[d.levelRank];
        rowHeight[row] = Math.max(rowHeight[row], d.__contentHeight + SIB_GAP);

        d.__leafGroups.forEach(function (g) {
          var groupWidthPx = Math.max(g.__widthPx - SIB_GAP, 0);
          g.__contentHeight = measureHtmlHeight(groupWidthPx, function (probe) {
            var s = document.createElement("div");
            s.className = "hitop-icicle-sublabel-html";
            s.textContent = g.level;
            probe.appendChild(s);
            var list = appendChipList(probe);
            g.members.forEach(function (c) {
              var span = document.createElement("span");
              span.className = c.data.provisional
                ? "hitop-icicle-chip is-provisional"
                : "hitop-icicle-chip";
              span.textContent = c.data.label;
              list.appendChild(span);
            });
          });
          var gRow = rowOfRank[g.rank];
          rowHeight[gRow] = Math.max(rowHeight[gRow], g.__contentHeight + SIB_GAP);
        });
      });

      var rowTop = [0];
      for (var r = 1; r <= maxRow; r++) {
        rowTop[r] = rowTop[r - 1] + rowHeight[r - 1] + ROW_GAP;
      }
      var totalHeight = rowTop[maxRow] + rowHeight[maxRow];

      var svg = d3
        .select(svgHost)
        .append("svg")
        .attr("viewBox", "0 0 " + width + " " + totalHeight)
        .attr("width", width)
        .attr("height", totalHeight)
        .attr("role", "img")
        .attr("aria-label", "Factorization tree " + (data.meta ? data.meta.label : ""));

      var connectorData = internalNodes
        .filter(function (d) {
          return d.parent;
        })
        .map(function (d) {
          return {
            x: d.__x0px + d.__widthPx / 2,
            fromRow: rowOfRank[d.parent.levelRank],
            toRow: rowOfRank[d.levelRank],
            provisional: !!d.data.provisional,
          };
        })
        .concat(
          internalNodes.reduce(function (acc, p) {
            p.__leafGroups.forEach(function (g) {
              acc.push({
                x: g.__x0px + g.__widthPx / 2,
                fromRow: rowOfRank[p.levelRank],
                toRow: rowOfRank[g.rank],
                provisional: false,
              });
            });
            return acc;
          }, [])
        );

      svg
        .append("g")
        .attr("class", "hitop-icicle-connectors")
        .selectAll("line")
        .data(connectorData)
        .join("line")
        .attr("class", function (d) {
          return d.provisional
            ? "hitop-icicle-connector is-provisional"
            : "hitop-icicle-connector";
        })
        .attr("x1", function (d) { return d.x; })
        .attr("x2", function (d) { return d.x; })
        .attr("y1", function (d) { return rowTop[d.fromRow] + rowHeight[d.fromRow]; })
        .attr("y2", function (d) { return rowTop[d.toRow]; });

      var cell = svg
        .selectAll("g.hitop-icicle-node")
        .data(internalNodes)
        .join("g")
        .attr("class", "hitop-icicle-node")
        .attr("tabindex", 0)
        .attr("transform", function (d) {
          return "translate(" + d.__x0px + "," + rowTop[rowOfRank[d.levelRank]] + ")";
        });

      cell.each(function (d) {
        var g = d3.select(this);
        var row = rowOfRank[d.levelRank];
        var boxWidth = Math.max(d.__widthPx - SIB_GAP, 0);
        var boxHeight = rowHeight[row] - SIB_GAP;
        var fill = d.data.color;
        var textColor = textColorFor(fill);

        g.append("rect")
          .attr("width", boxWidth)
          .attr("height", boxHeight)
          .attr("fill", fill)
          .attr("opacity", d.data.kind === "collection" ? 0.85 : 1)
          .attr("class", "hitop-icicle-box")
          .append("title")
          .text(d.data.label + " (" + d.data.level + ", " + d.data.code + ")");

        var fo = g
          .append("foreignObject")
          .attr("x", 0)
          .attr("y", 0)
          .attr("width", boxWidth)
          .attr("height", boxHeight);
        var content = fo
          .append("xhtml:div")
          .attr("class", "hitop-icicle-box-content")
          .style("color", textColor)
          .node();
        appendLabelBlock(content, d.data.label, d.data.level);
      });

      cell.on("click", function (event, d) {
        selectNode(d, cell);
      });
      cell.on("keydown", function (event, d) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectNode(d, cell);
        }
      });
      cell.on("mouseenter", function (event, d) {
        previewNode(d);
      });

      // Leaf groups: one box per contiguous run of same-level leaf
      // children, spanning only the width that run was allocated (not the
      // whole parent) -- see module docstring. Members render as a
      // wrapped group of small pill tags, the flex-wrap "chip group"
      // pattern common to Material Design/Carbon/etc. for a dense set of
      // short labels.
      var leafGroupLayer = svg.append("g").attr("class", "hitop-icicle-leafgroups");
      internalNodes.forEach(function (p) {
        p.__leafGroups.forEach(function (group) {
          var row = rowOfRank[group.rank];
          var boxWidth = Math.max(group.__widthPx - SIB_GAP, 0);
          var boxHeight = rowHeight[row] - SIB_GAP;
          var fill = group.members[0].data.color;
          var textColor = textColorFor(fill);
          var luminance = d3.hsl(fill).l;
          var chipBg = luminance > 0.6 ? "rgba(0,0,0,0.08)" : "rgba(255,255,255,0.22)";
          var chipBgHover = luminance > 0.6 ? "rgba(0,0,0,0.16)" : "rgba(255,255,255,0.34)";

          var g = leafGroupLayer
            .append("g")
            .attr("transform", "translate(" + group.__x0px + "," + rowTop[row] + ")");

          g.append("rect")
            .attr("width", boxWidth)
            .attr("height", boxHeight)
            .attr("fill", fill)
            .attr("class", "hitop-icicle-box");

          var fo = g
            .append("foreignObject")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", boxWidth)
            .attr("height", boxHeight);
          var content = fo
            .append("xhtml:div")
            .attr("class", "hitop-icicle-box-content")
            .style("color", textColor)
            .style("--hitop-chip-bg", chipBg)
            .style("--hitop-chip-bg-hover", chipBgHover)
            .node();

          var sublabel = document.createElement("div");
          sublabel.className = "hitop-icicle-sublabel-html";
          sublabel.textContent = group.level;
          content.appendChild(sublabel);

          var list = document.createElement("div");
          list.className = "hitop-icicle-chip-list";
          content.appendChild(list);

          group.members.forEach(function (c) {
            var chip = d3
              .select(list)
              .append("xhtml:span")
              .attr("class", function () {
                return c.data.provisional ? "hitop-icicle-chip is-provisional" : "hitop-icicle-chip";
              })
              .attr("tabindex", 0)
              .attr("title", c.data.label + " (" + c.data.level + ", " + c.data.code + ")")
              .text(c.data.label);

            chip.on("click", function () {
              selectNode(c, null);
            });
            chip.on("keydown", function (event) {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                selectNode(c, null);
              }
            });
            chip.on("mouseenter", function () {
              previewNode(c);
            });
          });
        });
      });

      // Legend: children of the currently selected node (default: the
      // factor's own top-level branches) -- see renderLegend/selectNode.
      // Re-rendered from `activeNode` on every draw so a resize-triggered
      // redraw preserves whatever the user last clicked.
      renderLegend(activeNode);

      lastDraw = {
        rowHeight: rowHeight,
        rowTop: rowTop,
        width: width,
        totalHeight: totalHeight,
        connectorData: connectorData,
      };
    }

    draw();

    // Node fill now comes straight from the JSON's own `color` field
    // (theme-independent), so only layout -- not color -- ever needs a
    // redraw; a resize is the only thing that still requires one.
    var resizeTimer = null;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(draw, 150);
    });

    /**
     * Build the diagram as a standalone, dependency-free SVG: plain
     * <rect>/<line>/<text>, no <foreignObject>. Two things this buys over
     * serializing the live (foreignObject-based) interactive SVG directly:
     *
     *  - Portability: <foreignObject> HTML reflow is the least-supported
     *    part of the SVG spec outside of actual browsers (patchy or absent
     *    in most image viewers, Office, and PDF tooling), and where it does
     *    render, its line-wrapping depends on whatever font *that* renderer
     *    substitutes when the original isn't installed -- both of which
     *    made a downloaded diagram's line breaks unpredictable from one
     *    viewer to the next (e.g. a label that fit on one line here
     *    wrapping to two elsewhere). Wrapping is instead computed once,
     *    right here, with the same `measureTextWidth` the interactive
     *    layout itself uses, and baked in as fixed <tspan> positions -- so
     *    every viewer paints the exact same lines, full stop.
     *  - Rasterizability: browsers taint a canvas the moment an SVG image
     *    containing <foreignObject> is drawn onto it (a deliberate, blanket
     *    security restriction that applies regardless of same-origin blob
     *    URLs), which made a canvas-based PNG/PDF export of the interactive
     *    SVG impossible. A <foreignObject>-free SVG carries no such
     *    restriction, which is what lets the PNG/PDF export functions below
     *    rasterize this output directly.
     *
     * Returns `{ markup, width, height }`, or null before the first draw().
     */
    function buildExportSvg() {
      if (!lastDraw) return null;
      var width = lastDraw.width;
      var height = lastDraw.totalHeight;

      var svg = document.createElementNS(SVG_NS, "svg");
      svg.setAttribute("xmlns", SVG_NS);
      svg.setAttribute("viewBox", "0 0 " + width + " " + height);
      svg.setAttribute("width", width);
      svg.setAttribute("height", height);
      svg.setAttribute("role", "img");
      svg.setAttribute(
        "aria-label",
        "Factorization tree " + (data.meta && data.meta.label ? data.meta.label : "")
      );
      svg.setAttribute("font-family", '-apple-system, "Segoe UI", Roboto, Arial, sans-serif');

      var bg = document.createElementNS(SVG_NS, "rect");
      bg.setAttribute("width", width);
      bg.setAttribute("height", height);
      bg.setAttribute("fill", "#ffffff");
      svg.appendChild(bg);

      var connectorGroup = document.createElementNS(SVG_NS, "g");
      lastDraw.connectorData.forEach(function (c) {
        var line = document.createElementNS(SVG_NS, "line");
        line.setAttribute("x1", c.x);
        line.setAttribute("x2", c.x);
        line.setAttribute("y1", lastDraw.rowTop[c.fromRow] + lastDraw.rowHeight[c.fromRow]);
        line.setAttribute("y2", lastDraw.rowTop[c.toRow]);
        line.setAttribute("stroke", "rgba(11, 11, 11, 0.38)");
        line.setAttribute("stroke-width", "1.5");
        if (c.provisional) line.setAttribute("stroke-dasharray", "4 3");
        connectorGroup.appendChild(line);
      });
      svg.appendChild(connectorGroup);

      internalNodes.forEach(function (d) {
        var row = rowOfRank[d.levelRank];
        var boxWidth = Math.max(d.__widthPx - SIB_GAP, 0);
        var boxHeight = lastDraw.rowHeight[row] - SIB_GAP;
        var fill = d.data.color;
        var textColor = textColorFor(fill);

        var g = document.createElementNS(SVG_NS, "g");
        g.setAttribute("transform", "translate(" + d.__x0px + "," + lastDraw.rowTop[row] + ")");

        var rect = document.createElementNS(SVG_NS, "rect");
        rect.setAttribute("width", boxWidth);
        rect.setAttribute("height", boxHeight);
        rect.setAttribute("fill", fill);
        rect.setAttribute("opacity", d.data.kind === "collection" ? 0.85 : 1);
        rect.setAttribute("stroke", "#ffffff");
        rect.setAttribute("stroke-width", "1.5");
        var title = document.createElementNS(SVG_NS, "title");
        title.textContent = d.data.label + " (" + d.data.level + ", " + d.data.code + ")";
        rect.appendChild(title);
        g.appendChild(rect);

        appendExportLabel(g, boxWidth, boxHeight, d.data.label, d.data.level, textColor);
        svg.appendChild(g);
      });

      internalNodes.forEach(function (p) {
        p.__leafGroups.forEach(function (group) {
          var row = rowOfRank[group.rank];
          var boxWidth = Math.max(group.__widthPx - SIB_GAP, 0);
          var boxHeight = lastDraw.rowHeight[row] - SIB_GAP;
          var fill = group.members[0].data.color;
          var textColor = textColorFor(fill);
          var luminance = d3.hsl(fill).l;
          var chipFill = luminance > 0.6 ? "rgba(0,0,0,0.08)" : "rgba(255,255,255,0.22)";

          var g = document.createElementNS(SVG_NS, "g");
          g.setAttribute(
            "transform",
            "translate(" + group.__x0px + "," + lastDraw.rowTop[row] + ")"
          );

          var rect = document.createElementNS(SVG_NS, "rect");
          rect.setAttribute("width", boxWidth);
          rect.setAttribute("height", boxHeight);
          rect.setAttribute("fill", fill);
          rect.setAttribute("stroke", "#ffffff");
          rect.setAttribute("stroke-width", "1.5");
          g.appendChild(rect);

          var subLineHeight = EXPORT_SUBLABEL_FONT * 1.2;
          var sub = document.createElementNS(SVG_NS, "text");
          sub.setAttribute("x", boxWidth / 2);
          sub.setAttribute("y", EXPORT_LABEL_PAD_Y + subLineHeight * 0.78);
          sub.setAttribute("text-anchor", "middle");
          sub.setAttribute("font-size", EXPORT_SUBLABEL_FONT);
          sub.setAttribute("font-weight", "500");
          sub.setAttribute("fill", textColor);
          sub.setAttribute("opacity", "0.85");
          sub.textContent = group.level;
          g.appendChild(sub);

          var innerWidth = Math.max(boxWidth - EXPORT_LABEL_PAD_X * 2, 4);
          var chipRows = packChips(group.members, innerWidth);
          var chipHeight = CHIP_FONT_SIZE * 1.3 + 4;
          var chipsTop = EXPORT_LABEL_PAD_Y + subLineHeight + 4;

          chipRows.forEach(function (rowChips, ri) {
            var rowY = chipsTop + ri * (chipHeight + EXPORT_CHIP_ROW_GAP);
            var rowWidth =
              rowChips.reduce(function (sum, c) {
                return sum + c.width;
              }, 0) +
              (rowChips.length - 1) * EXPORT_CHIP_COL_GAP;
            var cursorX = boxWidth / 2 - rowWidth / 2;
            rowChips.forEach(function (c) {
              var chipG = document.createElementNS(SVG_NS, "g");
              chipG.setAttribute("transform", "translate(" + cursorX + "," + rowY + ")");

              var pill = document.createElementNS(SVG_NS, "rect");
              pill.setAttribute("width", c.width);
              pill.setAttribute("height", chipHeight);
              pill.setAttribute("rx", chipHeight / 2);
              if (c.member.data.provisional) {
                pill.setAttribute("fill", "none");
                pill.setAttribute("stroke", textColor);
                pill.setAttribute("stroke-width", "1");
                pill.setAttribute("stroke-dasharray", "3 2");
              } else {
                pill.setAttribute("fill", chipFill);
              }
              chipG.appendChild(pill);

              var chipText = document.createElementNS(SVG_NS, "text");
              chipText.setAttribute("x", c.width / 2);
              chipText.setAttribute("y", chipHeight / 2 + CHIP_FONT_SIZE * 0.36);
              chipText.setAttribute("text-anchor", "middle");
              chipText.setAttribute("font-size", CHIP_FONT_SIZE);
              chipText.setAttribute("fill", textColor);
              chipText.textContent = c.member.data.label;
              chipG.appendChild(chipText);

              g.appendChild(chipG);
              cursorX += c.width + EXPORT_CHIP_COL_GAP;
            });
          });

          svg.appendChild(g);
        });
      });

      return {
        markup: new XMLSerializer().serializeToString(svg),
        width: width,
        height: height,
      };
    }

    function buildExportFilename(ext) {
      var meta = data.meta || {};
      var base =
        [meta.factorization_id, meta.version].filter(Boolean).join("-") || "hitop-factorization";
      return base + "-diagram." + ext;
    }

    /** The diagram alone, scaled (if needed) to what would still fit a DIN A4
     * page -- see computeA4Scale -- rasterized at exactly that size. No page
     * padding, no centering: the PNG's own dimensions are the diagram's. */
    function exportPngBlob() {
      var built = buildExportSvg();
      if (!built) return Promise.reject(new Error("The diagram has not rendered yet."));
      var scale = computeA4Scale(built.width, built.height);
      var wPx = (built.width / CSS_PX_PER_INCH) * PNG_DPI * scale;
      var hPx = (built.height / CSS_PX_PER_INCH) * PNG_DPI * scale;
      return rasterizeSvgToCanvas(built.markup, wPx, hPx, "#ffffff").then(function (canvas) {
        return canvasToBlob(canvas, "image/png");
      });
    }

    /** The diagram alone, scaled (if needed) to what would still fit a DIN A4
     * page -- see computeA4Scale -- wrapped into a single-page PDF whose page
     * size *is* that scaled diagram, filling it completely. No A4-sized page
     * padding and no centering: a PDF page has no inherent margin to begin
     * with, so "top-left" here just means the image fills the page exactly
     * as authored, with nothing added around it. */
    function exportPdfBytes() {
      var built = buildExportSvg();
      if (!built) return Promise.reject(new Error("The diagram has not rendered yet."));
      var scale = computeA4Scale(built.width, built.height);
      var contentWpt = (built.width / CSS_PX_PER_INCH) * PT_PER_INCH * scale;
      var contentHpt = (built.height / CSS_PX_PER_INCH) * PT_PER_INCH * scale;
      var imgWpx = Math.round((contentWpt / PT_PER_INCH) * PDF_DPI);
      var imgHpx = Math.round((contentHpt / PT_PER_INCH) * PDF_DPI);

      return rasterizeSvgToCanvas(built.markup, imgWpx, imgHpx, "#ffffff")
        .then(function (canvas) {
          return canvasToBlob(canvas, "image/jpeg", 0.92);
        })
        .then(function (jpegBlob) {
          return jpegBlob.arrayBuffer();
        })
        .then(function (jpegBytes) {
          return buildSinglePageImagePdf(
            jpegBytes,
            imgWpx,
            imgHpx,
            contentWpt,
            contentHpt,
            0,
            0,
            contentWpt,
            contentHpt
          );
        });
    }

    function handleDownload(format) {
      if (format === "svg") {
        var built = buildExportSvg();
        if (!built) {
          showToast("The diagram has not rendered yet.");
          return;
        }
        triggerDownload(
          new Blob([built.markup], { type: "image/svg+xml;charset=utf-8" }),
          buildExportFilename("svg")
        );
        showToast("Diagram downloaded as SVG.");
        return;
      }
      if (format === "png") {
        exportPngBlob()
          .then(function (blob) {
            triggerDownload(blob, buildExportFilename("png"));
            showToast("Diagram downloaded as PNG.");
          })
          .catch(function (err) {
            console.error(err);
            showToast("PNG export failed.");
          });
        return;
      }
      if (format === "pdf") {
        exportPdfBytes()
          .then(function (bytes) {
            triggerDownload(
              new Blob([bytes], { type: "application/pdf" }),
              buildExportFilename("pdf")
            );
            showToast("Diagram downloaded as PDF.");
          })
          .catch(function (err) {
            console.error(err);
            showToast("PDF export failed.");
          });
      }
    }

    // Share/download toolbar wiring. Every export pulls a fresh
    // buildExportSvg() (rather than caching one), so it always reflects the
    // diagram's current size even after a resize-triggered redraw.
    var shareBtn = toolbar.querySelector('[data-role="share"]');
    var menuEl = toolbar.querySelector(".hitop-icicle-menu");
    var menuTrigger = toolbar.querySelector('[data-role="download-trigger"]');
    var menuList = toolbar.querySelector(".hitop-icicle-menu-list");

    function onDocClick(event) {
      if (!menuEl.contains(event.target)) closeMenu();
    }
    function onDocKeydown(event) {
      if (event.key === "Escape") closeMenu();
    }
    function openMenu() {
      menuList.hidden = false;
      menuTrigger.setAttribute("aria-expanded", "true");
      document.addEventListener("click", onDocClick, true);
      document.addEventListener("keydown", onDocKeydown, true);
    }
    function closeMenu() {
      menuList.hidden = true;
      menuTrigger.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", onDocClick, true);
      document.removeEventListener("keydown", onDocKeydown, true);
    }

    menuTrigger.addEventListener("click", function (event) {
      event.stopPropagation();
      if (menuList.hidden) openMenu();
      else closeMenu();
    });
    Array.prototype.forEach.call(menuList.querySelectorAll(".hitop-icicle-menu-item"), function (
      item
    ) {
      item.addEventListener("click", function () {
        closeMenu();
        handleDownload(item.getAttribute("data-format"));
      });
    });

    shareBtn.addEventListener("click", function () {
      var meta = data.meta || {};
      var shareTitle = meta.label || document.title;
      var shareUrl = window.location.href;

      exportPngBlob()
        .then(function (blob) {
          var file = new File([blob], buildExportFilename("png"), { type: "image/png" });
          if (navigator.canShare && navigator.canShare({ files: [file] })) {
            return navigator.share({ files: [file], title: shareTitle, text: shareTitle });
          }
          if (navigator.share) return navigator.share({ title: shareTitle, url: shareUrl });
          return copyLinkFallback(shareUrl);
        })
        .catch(function (err) {
          if (err && err.name === "AbortError") return; // user cancelled the native share sheet
          copyLinkFallback(shareUrl);
        });
    });
  }

  global.renderFactorizationIcicle = renderFactorizationIcicle;
})(window);
