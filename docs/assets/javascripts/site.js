document.addEventListener("DOMContentLoaded",()=>{
  const sidebar=document.querySelector(".md-sidebar--primary");
  if(!sidebar||window.matchMedia("(max-width: 1219px)").matches)return;
  const button=document.createElement("button");
  button.className="hitop-sidebar-toggle";
  button.type="button";
  button.textContent="‹";
  button.setAttribute("aria-label","Collapse documentation navigation");
  button.setAttribute("aria-expanded","true");
  button.addEventListener("click",()=>{
    const collapsed=document.body.classList.toggle("hitop-nav-collapsed");
    button.setAttribute("aria-expanded",String(!collapsed));
    localStorage.setItem("hitop-nav",collapsed?"collapsed":"open");
  });
  document.body.append(button);
  if(localStorage.getItem("hitop-nav")==="collapsed"){
    document.body.classList.add("hitop-nav-collapsed");
    button.setAttribute("aria-expanded","false");
  }
});

function initializeMetadataFilters(root = document) {
  root.querySelectorAll(".hitop-metadata-reference").forEach((reference) => {
    if (reference.dataset.filterInitialized === "true") return;

    const select = reference.querySelector("[data-metadata-filter]");
    const rows = [...reference.querySelectorAll("tbody tr")];
    const count = reference.querySelector("[data-metadata-count]");
    if (!select || !rows.length) return;

    const applyFilter = () => {
      const selected = select.value;
      let visible = 0;

      rows.forEach((row) => {
        const requirement = row.cells[2]?.textContent.trim().toLowerCase() || "";
        const show = selected === "all" || requirement.startsWith(selected);
        row.hidden = !show;
        if (show) visible += 1;
      });

      if (count) count.textContent = `${visible} of ${rows.length} fields shown`;
    };

    reference.dataset.filterInitialized = "true";
    select.addEventListener("change", applyFilter);
    applyFilter();
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(() => initializeMetadataFilters());
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => initializeMetadataFilters());
} else {
  initializeMetadataFilters();
}
