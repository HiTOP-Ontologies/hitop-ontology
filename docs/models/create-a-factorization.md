# Create a factorization

<div class="hitop-page-intro">
  <p>Build, validate, and download a hierarchy file, then prepare the repository commands needed to compile it.</p>
  <span class="hitop-source">Guided module · based on <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/docs/factorizations.md">docs/factorizations.md</a> and <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/schema/factorization-hierarchy.schema.json">schema/factorization-hierarchy.schema.json</a></span>
</div>

<div class="hitop-learning" data-learning-root data-ontology-version="{{ hitop_ontology_version }}">
  <nav class="hitop-learning-nav" aria-label="Learning steps" role="tablist">
    <button id="learning-tab-1" type="button" role="tab" aria-controls="learning-panel-1" aria-selected="true" class="is-active" data-step-button="1"><b>01</b><span>Scaffold<small>Directory and files</small></span></button>
    <button id="learning-tab-2" type="button" role="tab" aria-controls="learning-panel-2" aria-selected="false" tabindex="-1" data-step-button="2"><b>02</b><span>Metadata<small>Identity and provenance</small></span></button>
    <button id="learning-tab-3" type="button" role="tab" aria-controls="learning-panel-3" aria-selected="false" tabindex="-1" data-step-button="3"><b>03</b><span>Hierarchy<small>Concept or collection</small></span></button>
    <button id="learning-tab-4" type="button" role="tab" aria-controls="learning-panel-4" aria-selected="false" tabindex="-1" data-step-button="4"><b>04</b><span>Export<small>Validate and download</small></span></button>
  </nav>

  <section id="learning-panel-1" class="hitop-lesson is-active" role="tabpanel" aria-labelledby="learning-tab-1" data-step="1">
    <p class="hitop-lesson-kicker">Step 01 · Scaffold</p>
    <h2>Create the required files</h2>
    <div class="hitop-form-grid"><label>Factorization ID<input data-factor-id value="my-factorization" pattern="[a-z][a-z0-9-]*"></label><label>Version directory<input data-version-dir value="v1" pattern="v[1-9][0-9]*"></label><label>Stable version code<input data-version-code value="V10abc" pattern="[A-Za-z0-9]+"></label></div>
    <div class="hitop-live-output" aria-live="polite"><span>Generated path</span><code data-scaffold-output>factorizations/my-factorization/v1/V10abc_hierarchy.yaml</code></div>
    <p>The same directory also requires a `README.md` describing scope, source, version, and status.</p>
    <button type="button" class="hitop-next" data-next="2">Continue to metadata →</button>
  </section>

  <section id="learning-panel-2" class="hitop-lesson" role="tabpanel" aria-labelledby="learning-tab-2" data-step="2">
    <p class="hitop-lesson-kicker">Step 02 · Metadata</p><h2>Write a complete meta block</h2>
    <div class="hitop-form-grid"><label>Human-readable label<input data-meta-label value="My HiTOP factorization"></label><label>Status<select data-meta-status><option>draft</option><option>active</option><option>deprecated</option></select></label><label>Created by<input data-created-by value="Your name or role"></label><label>Created at<input data-created-at type="date"></label></div>
    <pre class="hitop-yaml" aria-live="polite"><code data-meta-output></code></pre><button type="button" class="hitop-next" data-next="3">Continue to hierarchy →</button>
  </section>

  <section id="learning-panel-3" class="hitop-lesson" role="tabpanel" aria-labelledby="learning-tab-3" data-step="3">
    <p class="hitop-lesson-kicker">Step 03 · Hierarchy</p><h2>Compose the complete hierarchy</h2>
    <p>Select a node to edit it. Add children at any depth to build the complete tree; siblings are created by selecting their parent and adding another child.</p>
    <div class="hitop-tree-editor">
      <div class="hitop-tree-outline">
        <span>Hierarchy</span>
        <div data-tree-outline role="tree" aria-label="Factorization hierarchy"></div>
      </div>
      <div class="hitop-node-editor">
        <span data-selected-node-label>Selected node</span>
    <div class="hitop-form-grid">
      <label>Node kind<select data-node-kind><option value="concept">concept</option><option value="partial">partial</option><option value="collection">collection</option></select></label>
      <label>Partial node ID<input data-node-local-id disabled pattern="[A-Za-z0-9]+"><small>Required for partial: stable local identity, independent of the core code.</small></label>
      <label>Partial mapping note<textarea data-node-mapping-note disabled></textarea><small>Optional: describe the overlap and differences.</small></label>
      <label>Level<input data-node-level value="Factor" required></label>
      <label>Label<input data-node-label value="General Factor of Psychopathology" required></label>
      <label>Ontology code · search by code or label
        <span class="hitop-code-combobox">
          <input data-node-code-search role="combobox" aria-expanded="false" aria-controls="hitop-code-options" aria-autocomplete="list" autocomplete="off" placeholder="Type a code or label…" value="F001Hw — General Factor of Psychopathology">
          <input data-node-code type="hidden" value="F001Hw">
          <span id="hitop-code-options" class="hitop-code-options" data-code-options role="listbox" hidden></span>
        </span>
        <small class="hitop-field-help">Concept or partial: select an ontology code. Partial also requires a unique local ID. Collection: enter a unique local code.</small>
      </label>
      <label class="hitop-checkbox-field"><input data-node-provisional type="checkbox"><span>Provisional placement</span><small>Optional for any node kind; marks this placement as tentative.</small></label>
      <label class="hitop-bridge-field">Bridge · search by label
        <span class="hitop-code-combobox">
          <input data-bridge-search role="combobox" aria-expanded="false" aria-controls="hitop-bridge-options" aria-autocomplete="list" aria-describedby="hitop-bridge-help" autocomplete="off" placeholder="Type a label from this hierarchy…">
          <span id="hitop-bridge-options" class="hitop-code-options" data-bridge-options role="listbox" hidden></span>
        </span>
        <span class="hitop-bridge-selection" data-bridge-selection aria-label="Selected bridge labels"></span>
        <small id="hitop-bridge-help">Select unique labels of other nodes in this hierarchy, including partial and collection nodes. Each selection appears below as a removable chip; bridges document cross-loading and do not create hierarchy edges.</small>
      </label>
    </div>
    <div class="hitop-validation" data-node-message aria-live="polite">A concept code must reference an existing code from the core ontology.</div>
        <div class="hitop-tree-actions">
          <button type="button" data-add-child>Add child</button>
          <button type="button" data-remove-node>Remove selected</button>
        </div>
      </div>
    </div>
    <pre class="hitop-yaml" aria-label="Current hierarchy YAML"><code data-node-output></code></pre>
    <button type="button" class="hitop-next" data-next="4">Continue to validation →</button>
  </section>

  <section id="learning-panel-4" class="hitop-lesson" role="tabpanel" aria-labelledby="learning-tab-4" data-step="4">
    <p class="hitop-lesson-kicker">Step 04 · Validate and download</p><h2>Validate the complete hierarchy file</h2>
    <pre class="hitop-yaml" aria-label="Generated hierarchy YAML"><code data-document-output></code></pre>
    <div class="hitop-validation" data-document-message aria-live="polite">Validation has not been run.</div>
    <div class="hitop-export-actions">
      <button type="button" class="hitop-next" data-validate-document>Validate file</button>
      <button type="button" class="hitop-next" data-download-document disabled>Download YAML</button>
      <button type="button" class="hitop-next" data-download-ontology disabled>Download RDF</button>
      <button type="button" class="hitop-next" data-download-diagram disabled>Download diagram JSON</button>
      <button type="button" class="hitop-next" data-open-diagram disabled>Open diagram in viewer</button>
    </div>
    <p class="hitop-copy-status" data-download-status aria-live="polite"></p>
    <div class="hitop-boundary"><strong>Validation boundary</strong>The browser validates the generated hierarchy and derived artifacts against the rules available in this website build. Domain review is still required before changing `status` from `draft` to `active`.</div>
  </section>
</div>

<script type="application/json" data-hitop-core-concepts>{{ hitop_core_concepts_json }}</script>

### Node meaning

Choose `concept` for the same core concept, including equivalent local wording.
Choose `partial` for partial overlap with an existing core code; it does not
assert equivalence, narrower/broader direction, or a reversed pole. Choose
`collection` to group concepts using a local code. The label is the wording
shown in this factorization; the core ontology remains unchanged.

For `partial`, supply a stable alphanumeric `id`. It identifies the local
node independently of its core `code`. Multiple partial nodes may reference
the same core code using different IDs. An optional `mapping_note` explains
which contents overlap and how they differ. IDs must not collide with
collection codes. Labels and bridges do not determine identity.
