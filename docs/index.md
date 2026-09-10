---
hide:
  - toc
  - path
  - footer
---

<div class="hitop-home">
  <section class="hitop-hero">
    <div class="hitop-eyebrow"><span></span> Open ontology · Version {{ hitop_ontology_version }}</div>
    <h1>One system.<br><em>Clear concepts.</em></h1>
    <p class="hitop-lead">A machine-readable representation of the Hierarchical Taxonomy of Psychopathology — with stable concept identity, decentralized manifestation suffixes, and versioned factorizations.</p>
    <div class="hitop-actions">
      <a class="hitop-button hitop-button--primary" href="about/">Explore documentation <b>→</b></a>
      <a class="hitop-button" href="create-a-factorization/">Create a factorization</a>
      <a class="hitop-button" href="https://github.com/HiTOP-Ontologies/hitop-ontology">GitHub ↗</a>
    </div>
    <div class="hitop-metrics">
      <div><strong>{{ hitop_ontology_version }}</strong><span>Current ontology</span></div>
      <div><strong>{{ hitop_project_status }}</strong><span>Project status</span></div>
      <div><strong>MIT</strong><span>Open-source license</span></div>
    </div>
  </section>

  <section class="hitop-section">
    <div class="hitop-section-head"><div><small>01 / Foundation</small><h2>Structure. Compare.<br>Harmonize.</h2></div><p>Three building blocks make heterogeneous mental-health data comparable while preserving local operational detail.</p></div>
    <div class="hitop-card-grid">
      <a class="hitop-card" href="core-vocabulary/"><i>01</i><b>↗</b><h3>Structure</h3><p>Stable HiTOP base codes for shared concepts that can be referenced across systems and versions.</p></a>
      <a class="hitop-card" href="factorizations/"><i>02</i><b>↗</b><h3>Compare</h3><p>Versioned factorizations compose the same core concepts into explicit, auditable models.</p></a>
      <a class="hitop-card" href="mapping-harmonization/"><i>03</i><b>↗</b><h3>Harmonize</h3><p>Namespaced suffixes and curated mappings connect local instruments to a common semantic base.</p></a>
    </div>
  </section>

  <section class="hitop-section">
    <div class="hitop-section-head"><div><small>02 / Code system</small><h2>Identity, clearly decomposed.</h2></div><p>One code, two responsibilities: stable concept identity plus an optional decentralized manifestation suffix.</p></div>
    <div class="hitop-code-model" aria-label="Identifier model">
      <span>SS<small>Segment</small></span><span>cc<small>Concept</small></span><span>XX<small>Checksum</small></span><span>.M<small>Manifest.</small></span><span>TT<small>Type</small></span><span>NS<small>Namespace</small></span><span>SLUG<small>Local name</small></span>
    </div>
    <p class="hitop-example">Example · <code>U0aB2X.M-AF-ROR3J2WQSVQFFIKK-CHRONIC_WORRY</code></p>
  </section>

  <section class="hitop-section hitop-learning-teaser">
    <div><small>03 / Guided learning</small><div class="hitop-big-number">04</div><h2>Four steps.<br>One valid result.</h2><p>Build the structure, write metadata, compose the hierarchy, then validate against the repository schema.</p><a class="hitop-button hitop-button--primary" href="create-a-factorization/">Start the module →</a></div>
    <ol><li><b>01</b><span><strong>Create the scaffold</strong>Directory and required files</span></li><li><b>02</b><span><strong>Write the meta block</strong>Identity, status, provenance</span></li><li><b>03</b><span><strong>Compose the hierarchy</strong>Concept and collection nodes</span></li><li><b>04</b><span><strong>Validate & compile</strong>Schema, tests, exports</span></li></ol>
  </section>
</div>
