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
 * `provisional: true` in the source hierarchy.yaml gets a dashed box
 * outline (or, inside a leaf list, a dashed-outline pill instead of a
 * solid-fill one) and, for an individually-boxed node, a dashed incoming
 * connector line.
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
      (meta && meta.label ? meta.label : "Diese Faktorisierung") +
      ": der Baum ist noch nicht kuratiert (meta.status: " +
      (meta && meta.status ? meta.status : "draft") +
      "). Diagramm erscheint, sobald hierarchy in der YAML-Datei befuellt ist.";
    container.appendChild(box);
  }

  function describeNode(dData) {
    var parts = [];
    parts.push("<strong>" + dData.label + "</strong>");
    parts.push("Level: " + dData.level);
    parts.push("Code: " + dData.code);
    if (dData.kind === "collection") {
      parts.push("Art: faktorisierungslokale Zusammenfuehrung (skos:Collection)");
    }
    if (dData.bridge && dData.bridge.length) {
      parts.push("Bridge: " + dData.bridge.join(", "));
    }
    if (dData.provisional) {
      parts.push("Status: provisional (gestrichelt dargestellt)");
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
    var svgHost = document.createElement("div");
    svgHost.className = "hitop-icicle-svg-host";
    var legend = document.createElement("div");
    legend.className = "hitop-icicle-legend";
    var detail = document.createElement("div");
    detail.className = "hitop-icicle-detail";
    detail.innerHTML =
      "<em>Knoten anklicken oder mit der Maus/Tastatur fokussieren, " +
      "um Level, Code und Herkunft zu sehen.</em>";
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

    function focusData(dData, cellSelection, matchFn) {
      detail.innerHTML = describeNode(dData);
      if (cellSelection) {
        cellSelection.classed("is-active", matchFn);
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
        .attr("aria-label", "Faktorisierungsbaum " + (data.meta ? data.meta.label : ""));

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
          .attr(
            "class",
            d.data.provisional ? "hitop-icicle-box is-provisional" : "hitop-icicle-box"
          )
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
        focusData(d.data, cell, function (n) { return n === d; });
      });
      cell.on("keydown", function (event, d) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          focusData(d.data, cell, function (n) { return n === d; });
        }
      });
      cell.on("mouseenter", function (event, d) {
        focusData(d.data, null, null);
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
              focusData(c.data, null, null);
            });
            chip.on("keydown", function (event) {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                focusData(c.data, null, null);
              }
            });
            chip.on("mouseenter", function () {
              focusData(c.data, null, null);
            });
          });
        });
      });

      // Legend: one swatch per top-level branch, using its own palette color.
      legend.innerHTML = "";
      (root.children || []).forEach(function (child) {
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

    draw();

    // Node fill now comes straight from the JSON's own `color` field
    // (theme-independent), so only layout -- not color -- ever needs a
    // redraw; a resize is the only thing that still requires one.
    var resizeTimer = null;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(draw, 150);
    });
  }

  global.renderFactorizationIcicle = renderFactorizationIcicle;
})(window);
