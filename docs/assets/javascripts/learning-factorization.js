function initializeFactorizationLearning() {
  const root = document.querySelector("[data-learning-root]");
  if (!root || root.dataset.initialized === "true") return;
  root.dataset.initialized = "true";
  root.classList.add("is-enhanced");

  const $ = (selector) => root.querySelector(selector);
  const all = (selector) => [...root.querySelectorAll(selector)];
  const yamlString = (value) => JSON.stringify(String(value));
  const coreConceptsElement = document.querySelector("[data-hitop-core-concepts]");
  let coreConcepts = [];
  try {
    coreConcepts = JSON.parse(coreConceptsElement?.textContent || "[]");
  } catch (_error) {
    // The validation result explains when the build-time vocabulary is unavailable.
  }
  const conceptsByCode = new Map(coreConcepts.map((concept) => [concept.code, concept]));

  let nextNodeId = 2;
  let selectedNodeId = 1;
  let validatedDocument = "";
  const hierarchy = {
    id: 1,
    kind: "concept",
    level: "Factor",
    label: "General Factor of Psychopathology",
    code: "F001Hw",
    provisional: false,
    bridge: [],
    children: [],
  };

  const show = (step) => {
    all("[data-step]").forEach((element) => {
      const active = element.dataset.step === String(step);
      element.classList.toggle("is-active", active);
      element.hidden = !active;
    });
    all("[data-step-button]").forEach((element) => {
      const active = element.dataset.stepButton === String(step);
      element.classList.toggle("is-active", active);
      element.setAttribute("aria-current", active ? "step" : "false");
      element.setAttribute("aria-selected", String(active));
      element.tabIndex = active ? 0 : -1;
    });
  };

  const stepButtons = all("[data-step-button]");
  stepButtons.forEach((button, index) => {
    button.addEventListener("click", () => show(button.dataset.stepButton));
    button.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === "ArrowLeft") next = (index - 1 + stepButtons.length) % stepButtons.length;
      if (event.key === "ArrowRight") next = (index + 1) % stepButtons.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = stepButtons.length - 1;
      show(stepButtons[next].dataset.stepButton);
      stepButtons[next].focus();
    });
  });
  all("[data-next]").forEach((button) =>
    button.addEventListener("click", () => {
      show(button.dataset.next);
      $(`[data-step="${button.dataset.next}"] h2`).setAttribute("tabindex", "-1");
      $(`[data-step="${button.dataset.next}"] h2`).focus();
      root.scrollIntoView({ behavior: "smooth", block: "start" });
    }),
  );

  const values = () => ({
    factorId: $("[data-factor-id]").value.trim(),
    versionDir: $("[data-version-dir]").value.trim(),
    versionCode: $("[data-version-code]").value.trim(),
    metaLabel: $("[data-meta-label]").value.trim(),
    status: $("[data-meta-status]").value,
    createdBy: $("[data-created-by]").value.trim(),
    createdAt: $("[data-created-at]").value,
  });

  const repositoryPath = (data = values()) =>
    `factorizations/${data.factorId || "…"}/${data.versionDir || "…"}/${data.versionCode || "…"}_hierarchy.yaml`;

  const findNode = (id, node = hierarchy, parent = null) => {
    if (node.id === id) return { node, parent };
    for (const child of node.children) {
      const found = findNode(id, child, node);
      if (found) return found;
    }
    return null;
  };

  const selectedNode = () => findNode(selectedNodeId)?.node || hierarchy;

  const serializeNode = (node, indent, listItem = false) => {
    const firstIndent = " ".repeat(indent);
    const fieldIndent = " ".repeat(listItem ? indent + 2 : indent);
    const lines = [
      `${firstIndent}${listItem ? "- " : ""}label: ${yamlString(node.label)}`,
      `${fieldIndent}level: ${yamlString(node.level)}`,
      `${fieldIndent}kind: ${yamlString(node.kind)}`,
      `${fieldIndent}code: ${yamlString(node.code)}`,
    ];
    if (node.provisional) lines.push(`${fieldIndent}provisional: true`);
    if (node.bridge.length) {
      lines.push(`${fieldIndent}bridge:`);
      for (const label of node.bridge) lines.push(`${fieldIndent}  - ${yamlString(label)}`);
    }
    if (node.children.length) {
      lines.push(`${fieldIndent}children:`);
      for (const child of node.children) {
        lines.push(...serializeNode(child, (listItem ? indent + 2 : indent) + 2, true));
      }
    }
    return lines;
  };

  const buildHierarchy = () => `hierarchy:\n${serializeNode(hierarchy, 2).join("\n")}\n`;

  const buildDocument = (data = values()) => `meta:
  factorization_id: ${yamlString(data.factorId)}
  version: ${yamlString(data.versionCode)}
  label: ${yamlString(data.metaLabel)}
  status: ${yamlString(data.status)}
  based_on:
    ontology_iri: "http://purl.org/hitop"
    ontology_version: ${yamlString(root.dataset.ontologyVersion)}
  provenance:
    created_by: ${yamlString(data.createdBy)}
    created_at: ${yamlString(data.createdAt)}

${buildHierarchy()}`;

  const invalidateDocument = () => {
    validatedDocument = "";
    all(
      "[data-download-document],[data-download-ontology],[data-download-diagram],[data-open-diagram]",
    ).forEach((button) => {
      button.disabled = true;
    });
    const message = $("[data-document-message]");
    message.classList.remove("is-valid", "is-invalid");
    message.textContent = "Validation has not been run for the current hierarchy.";
    $("[data-download-status]").textContent = "";
  };

  const updateDocument = () => {
    $("[data-document-output]").textContent = buildDocument();
    $("[data-node-output]").textContent = buildHierarchy();
    invalidateDocument();
  };

  const updateScaffold = () => {
    const path = repositoryPath();
    $("[data-scaffold-output]").textContent = path;
    updateDocument();
  };

  const updateMeta = () => {
    const data = values();
    $("[data-meta-output]").textContent = `meta:
  factorization_id: ${yamlString(data.factorId)}
  version: ${yamlString(data.versionCode)}
  label: ${yamlString(data.metaLabel)}
  status: ${yamlString(data.status)}
  based_on:
    ontology_iri: "http://purl.org/hitop"
    ontology_version: ${yamlString(root.dataset.ontologyVersion)}
  provenance:
    created_by: ${yamlString(data.createdBy)}
    created_at: ${yamlString(data.createdAt)}`;
    updateDocument();
  };

  const nodeErrors = (node, path, seenCodes = null) => {
    const errors = [];
    if (!node.label) errors.push(`${path}: label is required.`);
    if (!node.level) errors.push(`${path}: level is required.`);
    if (!/^[A-Za-z0-9]+$/.test(node.code)) {
      errors.push(`${path}: code must contain only letters and numbers.`);
    } else if (seenCodes?.has(node.code)) {
      errors.push(`${path}: code ${node.code} occurs more than once in the hierarchy.`);
    } else {
      seenCodes?.add(node.code);
    }
    if (node.kind === "concept" && conceptsByCode.size > 0 && !conceptsByCode.has(node.code)) {
      errors.push(`${path}: concept code ${node.code || "(empty)"} is not in the core vocabulary.`);
    }
    if (!Array.isArray(node.bridge) || node.bridge.some((label) => !label)) {
      errors.push(`${path}: bridge must contain non-empty node labels.`);
    }
    return errors;
  };

  const updateNodeMessage = () => {
    const node = selectedNode();
    const message = $("[data-node-message]");
    const errors = nodeErrors(node, "Selected node");
    message.classList.toggle("is-invalid", errors.length > 0);
    message.classList.toggle("is-valid", errors.length === 0);
    if (errors.length) {
      message.textContent = errors.join(" ");
    } else if (node.kind === "collection") {
      message.textContent =
        "Valid collection node. Its code is local to this factorization; provisional and bridge remain optional.";
    } else {
      message.textContent = `${node.code} exists in the core ontology. Label and level are valid.`;
    }
  };

  const closeCodeOptions = () => {
    $("[data-code-options]").hidden = true;
    $("[data-node-code-search]").setAttribute("aria-expanded", "false");
  };

  const selectConcept = (concept) => {
    const node = selectedNode();
    node.code = concept.code;
    $("[data-node-code]").value = concept.code;
    $("[data-node-code-search]").value = `${concept.code} — ${concept.label}`;
    if (!node.label) {
      node.label = concept.label;
      $("[data-node-label]").value = concept.label;
    }
    closeCodeOptions();
    updateNodeMessage();
    renderTree();
    updateDocument();
  };

  const renderCodeOptions = (query = "") => {
    const options = $("[data-code-options]");
    options.replaceChildren();
    if (selectedNode().kind !== "concept") {
      closeCodeOptions();
      return;
    }
    const normalized = query.trim().toLocaleLowerCase();
    const matches = coreConcepts.filter(
      (concept) =>
        !normalized ||
        concept.code.toLocaleLowerCase().includes(normalized) ||
        concept.label.toLocaleLowerCase().includes(normalized),
    );
    for (const concept of matches) {
      const option = document.createElement("button");
      const code = document.createElement("code");
      option.type = "button";
      option.setAttribute("role", "option");
      code.textContent = concept.code;
      option.append(code, document.createTextNode(concept.label));
      option.addEventListener("mousedown", (event) => event.preventDefault());
      option.addEventListener("click", () => selectConcept(concept));
      options.append(option);
    }
    options.hidden = false;
    $("[data-node-code-search]").setAttribute("aria-expanded", "true");
  };

  const renderTree = () => {
    const container = $("[data-tree-outline]");
    container.replaceChildren();
    const renderBranch = (nodes) => {
      const list = document.createElement("ul");
      list.className = "hitop-tree-list";
      list.setAttribute("role", "group");
      for (const node of nodes) {
        const item = document.createElement("li");
        const button = document.createElement("button");
        const detail = document.createElement("small");
        button.type = "button";
        button.setAttribute("role", "treeitem");
        button.setAttribute("aria-selected", String(node.id === selectedNodeId));
        button.classList.toggle("is-selected", node.id === selectedNodeId);
        button.append(document.createTextNode(node.label || "Untitled node"));
        detail.textContent = `${node.level || "No level"} · ${node.code || "No code"}`;
        button.append(detail);
        button.addEventListener("click", () => {
          selectedNodeId = node.id;
          syncNodeEditor();
          renderTree();
        });
        item.append(button);
        if (node.children.length) item.append(renderBranch(node.children));
        list.append(item);
      }
      return list;
    };
    container.append(renderBranch([hierarchy]));
    $("[data-remove-node]").disabled = selectedNodeId === hierarchy.id;
  };

  const allNodes = (node = hierarchy, output = []) => {
    output.push(node);
    node.children.forEach((child) => allNodes(child, output));
    return output;
  };

  const closeBridgeOptions = () => {
    $("[data-bridge-options]").hidden = true;
    $("[data-bridge-search]").setAttribute("aria-expanded", "false");
  };

  const renderBridgeSelection = () => {
    const node = selectedNode();
    const selection = $("[data-bridge-selection]");
    selection.replaceChildren();
    for (const label of node.bridge) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.textContent = `${label} ×`;
      chip.setAttribute("aria-label", `Remove bridge to ${label}`);
      chip.addEventListener("click", () => {
        node.bridge = node.bridge.filter((item) => item !== label);
        renderBridgeSelection();
        updateNodeMessage();
        updateDocument();
      });
      selection.append(chip);
    }
  };

  const addBridge = (label) => {
    const node = selectedNode();
    if (!node.bridge.includes(label)) node.bridge.push(label);
    $("[data-bridge-search]").value = "";
    closeBridgeOptions();
    renderBridgeSelection();
    updateNodeMessage();
    updateDocument();
  };

  const renderBridgeOptions = (query = "") => {
    const node = selectedNode();
    const options = $("[data-bridge-options]");
    const normalized = query.trim().toLocaleLowerCase();
    const labels = [
      ...new Set(coreConcepts.map((concept) => concept.label).filter(Boolean)),
    ]
      .filter(
        (label) =>
          label !== node.label &&
          !node.bridge.includes(label) &&
          (!normalized || label.toLocaleLowerCase().includes(normalized)),
      )
      .sort((left, right) => left.localeCompare(right));
    options.replaceChildren();
    for (const label of labels) {
      const option = document.createElement("button");
      option.type = "button";
      option.setAttribute("role", "option");
      option.textContent = label;
      option.addEventListener("mousedown", (event) => event.preventDefault());
      option.addEventListener("click", () => addBridge(label));
      options.append(option);
    }
    if (!labels.length) {
      const empty = document.createElement("span");
      empty.className = "hitop-option-empty";
      empty.textContent = "No matching ontology labels";
      options.append(empty);
    }
    options.hidden = false;
    $("[data-bridge-search]").setAttribute("aria-expanded", "true");
  };

  const syncNodeEditor = () => {
    const node = selectedNode();
    const concept = conceptsByCode.get(node.code);
    $("[data-node-kind]").value = node.kind;
    $("[data-node-level]").value = node.level;
    $("[data-node-label]").value = node.label;
    $("[data-node-code]").value = node.code;
    $("[data-node-code-search]").value =
      node.kind === "concept" && concept ? `${concept.code} — ${concept.label}` : node.code;
    $("[data-node-provisional]").checked = node.provisional;
    $("[data-bridge-search]").value = "";
    renderBridgeSelection();
    closeBridgeOptions();
    $("[data-selected-node-label]").textContent =
      node.id === hierarchy.id ? "Selected node · Root" : "Selected node · Child";
    updateNodeMessage();
    $("[data-remove-node]").disabled = node.id === hierarchy.id;
  };

  const updateSelectedNode = () => {
    const node = selectedNode();
    node.kind = $("[data-node-kind]").value;
    node.level = $("[data-node-level]").value.trim();
    node.label = $("[data-node-label]").value.trim();
    node.code = $("[data-node-code]").value.trim();
    node.provisional = $("[data-node-provisional]").checked;
    if (node.kind === "collection") {
      $("[data-node-code-search]").value = node.code;
      closeCodeOptions();
    }
    updateNodeMessage();
    renderTree();
    updateDocument();
  };

  all("[data-factor-id],[data-version-dir],[data-version-code]").forEach((input) =>
    input.addEventListener("input", updateScaffold),
  );
  all("[data-meta-label],[data-meta-status],[data-created-by],[data-created-at]").forEach((input) =>
    input.addEventListener("input", updateMeta),
  );
  all(
    "[data-node-kind],[data-node-level],[data-node-label],[data-node-provisional]",
  ).forEach((input) => input.addEventListener("input", updateSelectedNode));

  const codeSearch = $("[data-node-code-search]");
  codeSearch.addEventListener("focus", () => renderCodeOptions(""));
  codeSearch.addEventListener("input", () => {
    const node = selectedNode();
    if (node.kind === "collection") {
      node.code = codeSearch.value.trim();
      $("[data-node-code]").value = node.code;
      updateNodeMessage();
      renderTree();
      updateDocument();
      return;
    }
    const exactCode = codeSearch.value.trim();
    const exactConcept = conceptsByCode.get(exactCode);
    node.code = exactConcept?.code || "";
    $("[data-node-code]").value = node.code;
    renderCodeOptions(codeSearch.value);
    updateNodeMessage();
    renderTree();
    updateDocument();
  });
  codeSearch.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeCodeOptions();
    if (event.key === "Enter") {
      const firstOption = $("[data-code-options] button");
      if (firstOption) {
        event.preventDefault();
        firstOption.click();
      }
    }
  });
  codeSearch.addEventListener("blur", () => setTimeout(closeCodeOptions, 0));

  const bridgeSearch = $("[data-bridge-search]");
  bridgeSearch.addEventListener("focus", () => renderBridgeOptions(""));
  bridgeSearch.addEventListener("input", () => renderBridgeOptions(bridgeSearch.value));
  bridgeSearch.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeBridgeOptions();
    if (event.key === "Enter") {
      const firstOption = $("[data-bridge-options] button");
      if (firstOption) {
        event.preventDefault();
        firstOption.click();
      }
    }
  });
  bridgeSearch.addEventListener("blur", () => setTimeout(closeBridgeOptions, 0));

  $("[data-add-child]").addEventListener("click", () => {
    const parentErrors = nodeErrors(selectedNode(), "Selected parent");
    if (parentErrors.length) {
      const message = $("[data-node-message]");
      message.classList.add("is-invalid");
      message.classList.remove("is-valid");
      message.textContent = `Cannot add a child: ${parentErrors.join(" ")}`;
      return;
    }
    const child = {
      id: nextNodeId++,
      kind: "concept",
      level: "",
      label: "",
      code: "",
      provisional: false,
      bridge: [],
      children: [],
    };
    selectedNode().children.push(child);
    selectedNodeId = child.id;
    syncNodeEditor();
    renderTree();
    updateDocument();
    $("[data-node-label]").focus();
  });

  $("[data-remove-node]").addEventListener("click", () => {
    const found = findNode(selectedNodeId);
    if (!found?.parent) return;
    found.parent.children = found.parent.children.filter((node) => node.id !== selectedNodeId);
    selectedNodeId = found.parent.id;
    syncNodeEditor();
    renderTree();
    updateDocument();
  });

  const validateDocument = () => {
    const data = values();
    const errors = [];
    if (!/^[a-z][a-z0-9]*(-[a-z0-9]+)*$/.test(data.factorId)) {
      errors.push("Factorization ID must be a kebab-case identifier.");
    }
    if (!/^v[1-9][0-9]*$/.test(data.versionDir)) {
      errors.push("Version directory must match v<N>, for example v1.");
    }
    if (!/^[A-Za-z0-9]+$/.test(data.versionCode)) {
      errors.push("Stable version code must contain only letters and numbers.");
    }
    if (!data.metaLabel) errors.push("Human-readable label is required.");
    if (!data.createdBy) errors.push("Created by is required.");
    const parsedDate = new Date(`${data.createdAt}T00:00:00Z`);
    if (
      !/^\d{4}-\d{2}-\d{2}$/.test(data.createdAt) ||
      Number.isNaN(parsedDate.getTime()) ||
      parsedDate.toISOString().slice(0, 10) !== data.createdAt
    ) {
      errors.push("Created at must be a valid ISO date in YYYY-MM-DD format.");
    }
    if (conceptsByCode.size === 0) {
      errors.push("The core vocabulary is unavailable in this build.");
    }

    const seenCodes = new Set();
    let nodeCount = 0;
    const validateNode = (node, path) => {
      nodeCount += 1;
      errors.push(...nodeErrors(node, path, seenCodes));
      node.children.forEach((child, index) =>
        validateNode(child, `${path} > child ${index + 1}`),
      );
    };
    validateNode(hierarchy, "Root");
    const hierarchyNodes = allNodes(hierarchy, []);
    const ontologyLabels = new Set(coreConcepts.map((concept) => concept.label));
    for (const node of hierarchyNodes) {
      for (const bridge of node.bridge) {
        if (!ontologyLabels.has(bridge) || bridge === node.label) {
          errors.push(`${node.label || "Unlabeled node"}: bridge target ${bridge} is not another concept from the core ontology.`);
        }
      }
    }
    if (!errors.length) {
      const parsedOntology = new DOMParser().parseFromString(buildOntology(), "application/xml");
      if (parsedOntology.querySelector("parsererror")) {
        errors.push("The generated factorization ontology is not valid XML.");
      }
      try {
        JSON.parse(JSON.stringify(buildDiagram()));
      } catch (_error) {
        errors.push("The generated diagram data is not valid JSON.");
      }
    }

    const message = $("[data-document-message]");
    message.classList.toggle("is-valid", errors.length === 0);
    message.classList.toggle("is-invalid", errors.length > 0);
    if (errors.length) {
      validatedDocument = "";
      all(
        "[data-download-document],[data-download-ontology],[data-download-diagram],[data-open-diagram]",
      ).forEach((button) => {
        button.disabled = true;
      });
      message.textContent = `Validation failed: ${errors.join(" ")}`;
      return false;
    }

    validatedDocument = buildDocument(data);
    all(
      "[data-download-document],[data-download-ontology],[data-download-diagram],[data-open-diagram]",
    ).forEach((button) => {
      button.disabled = false;
    });
    message.textContent = `Validation passed for ${nodeCount} hierarchy node${nodeCount === 1 ? "" : "s"}. The YAML file is ready for download.`;
    return true;
  };

  const palette = [
    "#1E3A5F", "#264B7D", "#2F5FA3", "#3F7EB8", "#4D98C7", "#4B8CC7",
    "#5A9ED4", "#6AAFE0", "#7ABEE1", "#8ACCE6", "#9EDAED", "#B1E0F0",
    "#9FC0E9", "#AEB8E3", "#BCA2DF", "#CA92DA", "#DDA5DD", "#E7B9DF",
    "#EECAE1", "#F8B7C5", "#FF8FA4", "#FFB3BA", "#FFBCC4", "#FFCCD6",
  ];
  const paletteLevels = new Set(["Factor", "Superspectrum", "Spectrum", "Subfactor"]);
  const roundHalfEven = (value) => {
    const lower = Math.floor(value);
    const fraction = value - lower;
    if (Math.abs(fraction - 0.5) < Number.EPSILON * 4) return lower % 2 === 0 ? lower : lower + 1;
    return Math.round(value);
  };
  const lighten = (hex, steps) => {
    if (!hex || steps <= 0) return hex;
    let [r, g, b] = [1, 3, 5].map((offset) => parseInt(hex.slice(offset, offset + 2), 16) / 255);
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h = 0;
    let s = 0;
    let l = (max + min) / 2;
    if (max !== min) {
      const delta = max - min;
      s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);
      if (max === r) h = (g - b) / delta + (g < b ? 6 : 0);
      else if (max === g) h = (b - r) / delta + 2;
      else h = (r - g) / delta + 4;
      h /= 6;
    }
    l = Math.min(0.93, l + steps * 0.09);
    s *= 0.94 ** steps;
    const hue = (p, q, t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };
    if (s === 0) r = g = b = l;
    else {
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue(p, q, h + 1 / 3);
      g = hue(p, q, h);
      b = hue(p, q, h - 1 / 3);
    }
    return `#${[r, g, b].map((channel) => roundHalfEven(channel * 255).toString(16).padStart(2, "0")).join("").toUpperCase()}`;
  };

  const buildDiagram = () => {
    const eligible = allNodes(hierarchy, []).filter((node) => paletteLevels.has(node.level));
    const directColors = new Map(
      eligible.map((node, index) => [
        node.id,
        palette[eligible.length > 1 ? roundHalfEven((index * (palette.length - 1)) / (eligible.length - 1)) : 0],
      ]),
    );
    const convert = (node, branch, parentColor = null, derivedDepth = 0) => {
      const isPaletteNode = paletteLevels.has(node.level);
      const color = isPaletteNode ? directColors.get(node.id) : lighten(parentColor, derivedDepth + 1);
      const nextDepth = isPaletteNode ? 0 : derivedDepth + 1;
      const output = { label: node.label, level: node.level, code: node.code, kind: node.kind, branch, color };
      if (node.bridge.length) output.bridge = [...node.bridge];
      if (node.provisional) output.provisional = true;
      if (node.children.length) {
        output.children = node.children.map((child, index) =>
          convert(child, branch === null ? index : branch, color, nextDepth),
        );
      }
      return output;
    };
    const data = values();
    return {
      meta: {
        factorization_id: data.factorId,
        version: data.versionCode,
        label: data.metaLabel,
        status: data.status,
      },
      hierarchy: convert(hierarchy, null),
    };
  };

  const xmlEscape = (value) =>
    String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  const buildOntology = () => {
    const data = values();
    const base = `http://purl.org/hitop/factorizations/${data.factorId}/v${data.versionCode}`;
    const subjectIri = (node) => node.kind === "collection" ? `${base}#${node.code}` : `http://purl.org/hitop#${node.code}`;
    const descriptions = [];
    descriptions.push(`  <rdf:Description rdf:about="${xmlEscape(base)}">
    <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Ontology"/>
    <rdfs:label xml:lang="en">${xmlEscape(data.metaLabel)}</rdfs:label>
    <owl:versionInfo>${xmlEscape(data.versionCode)}</owl:versionInfo>
    <owl:imports rdf:resource="http://purl.org/hitop"/>
    <dcterms:isVersionOf>${xmlEscape(root.dataset.ontologyVersion)}</dcterms:isVersionOf>
    <dcterms:creator>${xmlEscape(data.createdBy)}</dcterms:creator>
    <dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date">${xmlEscape(data.createdAt)}</dcterms:created>
    <skos:changeNote xml:lang="en">status: ${xmlEscape(data.status)}</skos:changeNote>
  </rdf:Description>`);
    const visit = (node) => {
      const lines = [`  <rdf:Description rdf:about="${xmlEscape(subjectIri(node))}">`];
      lines.push(`    <hitop:hasLevel>${xmlEscape(node.level)}</hitop:hasLevel>`);
      if (node.kind === "collection") {
        lines.push('    <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Collection"/>');
        lines.push(`    <rdfs:label xml:lang="en">${xmlEscape(node.label)}</rdfs:label>`);
      } else {
        const concept = conceptsByCode.get(node.code);
        lines.push(`    <rdfs:label>${xmlEscape(concept?.label || node.label)}</rdfs:label>`);
        if (concept?.comment) lines.push(`    <rdfs:comment>${xmlEscape(concept.comment)}</rdfs:comment>`);
      }
      if (node.provisional) lines.push('    <skos:changeNote xml:lang="en">provisional: true</skos:changeNote>');
      if (node.bridge.length) lines.push(`    <skos:changeNote xml:lang="en">Bridges: ${xmlEscape(node.bridge.join(", "))}</skos:changeNote>`);
      node.children.forEach((child) => lines.push(`    <hitop:hasTier rdf:resource="${xmlEscape(subjectIri(child))}"/>`));
      lines.push("  </rdf:Description>");
      descriptions.push(lines.join("\n"));
      node.children.forEach(visit);
    };
    visit(hierarchy);
    return `<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:hitop="http://purl.org/hitop#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:dcterms="http://purl.org/dc/terms/">
${descriptions.join("\n")}
</rdf:RDF>
`;
  };

  const download = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
    $("[data-download-status]").textContent = `${filename} was generated, validated, and downloaded.`;
  };

  $("[data-validate-document]").addEventListener("click", validateDocument);
  $("[data-download-document]").addEventListener("click", () => {
    if (!validateDocument() || validatedDocument !== buildDocument()) return;
    const data = values();
    download(validatedDocument, `${data.versionCode}_hierarchy.yaml`, "application/yaml;charset=utf-8");
  });
  $("[data-download-ontology]").addEventListener("click", () => {
    if (!validateDocument()) return;
    download(
      buildOntology(),
      `${values().versionCode}_factorization.rdf`,
      "application/rdf+xml;charset=utf-8",
    );
  });
  $("[data-download-diagram]").addEventListener("click", () => {
    if (!validateDocument()) return;
    download(
      `${JSON.stringify(buildDiagram(), null, 2)}\n`,
      `${values().versionCode}_diagram.json`,
      "application/json;charset=utf-8",
    );
  });
  $("[data-open-diagram]").addEventListener("click", () => {
    if (!validateDocument()) return;
    sessionStorage.setItem("hitop-custom-diagram", JSON.stringify(buildDiagram()));
    window.location.href = "../diagrams/?source=browser";
  });

  $("[data-created-at]").value ||= new Date().toISOString().slice(0, 10);
  updateScaffold();
  updateMeta();
  syncNodeEditor();
  renderTree();
  updateDocument();
  show(1);
}

// Material emits document$ after the initial load and every instant-navigation swap.
if (typeof document$ !== "undefined") {
  document$.subscribe(initializeFactorizationLearning);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeFactorizationLearning);
} else {
  initializeFactorizationLearning();
}
