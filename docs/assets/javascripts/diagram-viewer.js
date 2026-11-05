// Wires up the factorization dropdown on the diagram viewer page
// (docs/models/diagrams.md). Loaded site-wide via mkdocs.yml's
// extra_javascript, like factorization-icicle.js and d3 themselves, so it
// is a no-op everywhere except that one page.
//
// This does its own init/re-init instead of relying on the inline
// <script src="..."> and <script>...</script> tags that used to live
// directly in diagrams.md's content: MkDocs Material's
// navigation.instant swaps page content into the DOM via innerHTML on an
// in-app navigation (no full reload), and a <script> element inserted that
// way never executes -- only a real full-page load parses and runs it.
// That is why the diagram used to render on a hard reload but not when the
// page was reached by clicking an in-app link. document$ is Material's
// observable that fires after the initial load *and* after every
// instant-navigation swap, so subscribing to it (with the fallback below
// for a page that never defines document$) makes this reliable either way.
//
// That fixed the common case, but nothing guarantees the render still
// can't fail for some other reason on a given visit (the renderer script
// genuinely not loaded yet on a cold connection, a malformed/unexpected
// diagram payload, a thrown error inside the third-party d3 render path).
// A first-time visitor has no way to tell "still loading" apart from "this
// is just blank here" -- so every attempt below is verified, and any
// failure replaces the empty container with an explicit message and a
// Retry button instead of leaving it silently empty.
function initializeDiagramViewer() {
  var select = document.getElementById("factorization-select");
  var container = document.getElementById("diagram-container");
  if (!select || !container || container.dataset.initialized === "true") return;
  container.dataset.initialized = "true";

  var customDiagram = null;
  try {
    customDiagram = JSON.parse(sessionStorage.getItem("hitop-custom-diagram") || "null");
  } catch (_error) {
    sessionStorage.removeItem("hitop-custom-diagram");
  }
  if (customDiagram && customDiagram.hierarchy) {
    var customKey = "browser-preview";
    var option = document.createElement("option");
    option.value = customKey;
    option.textContent = (customDiagram.meta && customDiagram.meta.label) || "Browser preview";
    select.prepend(option);
    var payload = document.createElement("div");
    payload.hidden = true;
    payload.id = "data-" + customKey;
    payload.textContent = JSON.stringify(customDiagram);
    select.parentNode.insertBefore(payload, select.nextSibling);
    select.value = customKey;
  }

  // HiTOP Working Model is the default view regardless of the dropdown's
  // own option order, so a future catalog reorder can't silently change it.
  if (!customDiagram && select.querySelector('option[value="working-model"]')) {
    select.value = "working-model";
  }

  function renderSucceeded() {
    // renderFactorizationIcicle builds one of these two roots depending on
    // whether the factorization's tree is populated yet -- either is a
    // real, intentional result, not a silent failure.
    return !!container.querySelector(".hitop-icicle-wrapper, .hitop-icicle-placeholder");
  }

  function showFallback(reason) {
    container.innerHTML = "";
    var box = document.createElement("div");
    box.className = "hitop-diagram-fallback";
    var message = document.createElement("p");
    message.textContent = "The diagram did not load" + (reason ? " (" + reason + ")" : "") + ".";
    var button = document.createElement("button");
    button.type = "button";
    button.className = "hitop-button";
    button.textContent = "Retry";
    button.addEventListener("click", function () {
      attemptRender(select.value, 5);
    });
    box.appendChild(message);
    box.appendChild(button);
    container.appendChild(box);
  }

  function attemptRender(key, retriesLeft) {
    var el = document.getElementById("data-" + key);
    if (!el) {
      showFallback('no data for "' + key + '"');
      return;
    }
    if (typeof renderFactorizationIcicle !== "function") {
      // d3 and factorization-icicle.js load as plain, synchronous scripts
      // ahead of this file, so this should never be reached in practice --
      // but a first, cold navigation is exactly the case a visitor cannot
      // tell apart from "nothing renders here", so back off briefly and
      // retry a few times before giving up and showing the button.
      if (retriesLeft > 0) {
        setTimeout(function () {
          attemptRender(key, retriesLeft - 1);
        }, 200);
      } else {
        showFallback("the diagram renderer did not load");
      }
      return;
    }
    try {
      var data = JSON.parse(el.textContent);
      renderFactorizationIcicle(container, data);
    } catch (err) {
      console.error(err);
      showFallback("a rendering error occurred");
      return;
    }
    if (!renderSucceeded()) {
      showFallback("an unknown error occurred");
    }
  }

  select.addEventListener("change", function () {
    attemptRender(select.value, 5);
  });
  attemptRender(select.value, 5);
}

if (typeof document$ !== "undefined") {
  document$.subscribe(initializeDiagramViewer);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeDiagramViewer);
} else {
  initializeDiagramViewer();
}
