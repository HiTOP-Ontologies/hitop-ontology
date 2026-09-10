# Validation & quality

<div class="hitop-page-intro">
  <p>Automated gates check source code, schemas, factorizations, documentation examples, and generated ontology formats before publication.</p>
  <span class="hitop-source">Source · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/blob/main/.github/workflows/ci.yml">.github/workflows/ci.yml</a> · <a href="https://github.com/HiTOP-Ontologies/hitop-ontology/tree/main/validation">validation/</a></span>
</div>

## Validation pipeline

1. Install the package from locked constraints on Python 3.10, 3.11, and 3.12.
2. Compile Python sources and run the regression suite under `validation/`.
3. Validate documentation code examples and JSON Schema syntax.
4. Run Ruff lint and formatting checks.
5. Build the Python distribution and convert RDF to Turtle and OWL.
6. Run the ROBOT ontology quality report.
7. Build and publish this website only after all required jobs succeed.

## Local check

Run the local quality gate before committing changes to the tooling or its
documentation. It checks Python syntax, executes the regression suite, and
validates the published documentation examples in one reproducible sequence:

**Command**

```bash
scripts/validate_hitop_suffix_tooling.sh
```

**Output**

```text
Checking Python syntax and imports... PASS
Checking regression tests... PASS
Checking documentation code examples... PASS
Validation completed successfully.
```

Use Tox before a release to repeat the same checks with every supported Python
interpreter. This catches version-specific behavior that a check in the active
local environment alone cannot detect:

**Command**

```bash
.venv/bin/tox -e py310,py311,py312
```

**Output**

```text
py310: commands[0]> python -m compileall -q src scripts validation
py310: commands[1]> python -m unittest discover -s validation -v
py310: commands[2]> python scripts/validate_hitop_suffix_docs.py
py310: OK
py311: commands[0]> python -m compileall -q src scripts validation
py311: commands[1]> python -m unittest discover -s validation -v
py311: commands[2]> python scripts/validate_hitop_suffix_docs.py
py311: OK
py312: commands[0]> python -m compileall -q src scripts validation
py312: commands[1]> python -m unittest discover -s validation -v
py312: commands[2]> python scripts/validate_hitop_suffix_docs.py
py312: OK
congratulations :)
```
