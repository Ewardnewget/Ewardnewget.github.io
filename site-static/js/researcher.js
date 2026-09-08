/* Progressive enhancement: both language pages are complete static documents. */
(() => {
  "use strict";
  const controls = document.getElementById("publication-controls");
  const rows = Array.from(document.querySelectorAll("#paper-list > li"));
  const search = document.getElementById("paper-search");
  const year = document.getElementById("paper-year");
  const count = document.getElementById("paper-count");
  const empty = document.getElementById("no-papers");
  const clear = document.getElementById("clear-filters");
  const normalize = (text) => text.normalize("NFKC").toLowerCase().trim();

  if (controls && rows.length && search && year && count && empty && clear) {
    const text = new Map(rows.map((row) => [row, normalize(row.textContent)]));
    const years = [...new Set(rows.map((row) => row.dataset.year))]
      .filter((value) => value !== "undated")
      .sort((a, b) => Number(b) - Number(a));
    if (rows.some((row) => row.dataset.year === "undated")) years.push("undated");
    for (const value of years) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value === "undated" ? controls.dataset.undatedLabel : value;
      year.append(option);
    }
    const apply = () => {
      const terms = normalize(search.value).split(/\s+/).filter(Boolean);
      let visible = 0;
      for (const row of rows) {
        const match = (year.value === "all" || row.dataset.year === year.value) &&
          terms.every((term) => text.get(row).includes(term));
        row.hidden = !match;
        if (match) visible += 1;
      }
      count.textContent = controls.dataset.countPattern
        .replace("{visible}", visible).replace("{total}", rows.length);
      empty.hidden = visible !== 0;
    };
    search.addEventListener("input", apply);
    year.addEventListener("change", apply);
    clear.addEventListener("click", () => {
      search.value = "";
      year.value = "all";
      apply();
      search.focus();
    });
    controls.hidden = false;
    apply();
  }

  // A language change is ordinary navigation; no browser-language auto-redirect.
  for (const link of document.querySelectorAll(".language-switch a")) {
    link.addEventListener("click", () => { link.hash = window.location.hash; });
  }

  const nav = Array.from(document.querySelectorAll('.site-nav a[href^="#"]'));
  const sections = nav.map((link) => document.querySelector(link.getAttribute("href"))).filter(Boolean);
  const activate = (id) => {
    for (const link of nav) {
      if (link.getAttribute("href") === `#${id}`) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
  };
  for (const link of nav) link.addEventListener("click", () => activate(link.hash.slice(1)));
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) if (entry.isIntersecting) activate(entry.target.id);
    }, { rootMargin: "-12% 0px -65% 0px", threshold: 0 });
    sections.forEach((section) => observer.observe(section));
  }
})();
