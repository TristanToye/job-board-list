(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll("#boards tbody tr"));
  var q = document.getElementById("q"), ids = { region: "f-region", type: "f-type", api: "f-api", partner: "f-partner", lang: "f-lang", tier: "f-tier", function: "f-function", focus: "f-focus" };
  var sels = {}; Object.keys(ids).forEach(function (k) { sels[k] = document.getElementById(ids[k]); });
  var count = document.getElementById("count"), empty = document.getElementById("empty");
  if (!q) return;
  var sortSel = document.getElementById("sort"), tbody = document.querySelector("#boards tbody");
  function resort() {
    if (!sortSel || !tbody) return;
    var byName = sortSel.value === "name";
    rows.sort(function (a, b) { return byName ? (a.dataset.name < b.dataset.name ? -1 : 1) : (Number(a.dataset.rank) - Number(b.dataset.rank)) || (a.dataset.name < b.dataset.name ? -1 : 1); });
    rows.forEach(function (r) { tbody.appendChild(r); });
  }
  function apply() {
    resort();
    var term = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
    rows.forEach(function (r) {
      var ok = term.every(function (t) { return r.dataset.search.indexOf(t) > -1; });
      Object.keys(sels).forEach(function (k) { var v = sels[k].value; if (!v) return; if (k === "lang") { if ((" " + r.dataset.lang + " ").indexOf(" " + v + " ") < 0) ok = false; } else if (k === "function" || k === "focus") { if ((" " + r.dataset.tags + " ").indexOf(" " + v + " ") < 0) ok = false; } else if (r.dataset[k] !== v) ok = false; });
      r.hidden = !ok; if (ok) shown++;
    });
    count.textContent = "Showing " + shown + " of " + rows.length + " boards";
    empty.hidden = shown !== 0;
    try {
      var p = new URLSearchParams();
      if (q.value) p.set("q", q.value);
      if (sortSel && sortSel.value !== "prom") p.set("sort", sortSel.value);
      Object.keys(sels).forEach(function (k) { if (sels[k].value) p.set(k, sels[k].value); });
      history.replaceState(null, "", p.toString() ? "?" + p : location.pathname);
    } catch (e) {}
  }
  try {
    var p = new URLSearchParams(location.search);
    if (p.get("q")) q.value = p.get("q");
    if (sortSel && p.get("sort")) sortSel.value = p.get("sort");
    Object.keys(sels).forEach(function (k) { if (p.get(k)) sels[k].value = p.get(k); });
  } catch (e) {}
  q.addEventListener("input", apply);
  if (sortSel) sortSel.addEventListener("change", apply);
  Object.keys(sels).forEach(function (k) { sels[k].addEventListener("change", apply); });
  apply();
})();
