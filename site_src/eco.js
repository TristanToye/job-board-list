(function () {
  var table = document.querySelector("table.matrix"); if (!table) return;
  var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr")), filter = document.getElementById("ecofilter");
  if (filter) filter.addEventListener("input", function () { var t = filter.value.trim().toLowerCase(); rows.forEach(function (r) { r.hidden = !!t && r.dataset.name.indexOf(t) < 0; }); });
  var heads = table.querySelectorAll("thead th");
  table.addEventListener("mouseover", function (ev) {
    var td = ev.target.closest("td"); rows.forEach(function (r) { r.classList.remove("hot"); }); Array.prototype.forEach.call(table.querySelectorAll(".hotcol"), function (c) { c.classList.remove("hotcol"); });
    if (!td) return; var tr = td.parentNode; tr.classList.add("hot"); var idx = Array.prototype.indexOf.call(tr.children, td);
    if (heads[idx]) heads[idx].classList.add("hotcol"); rows.forEach(function (r) { if (r.children[idx]) r.children[idx].classList.add("hotcol"); });
  });
  table.addEventListener("mouseleave", function () { rows.forEach(function (r) { r.classList.remove("hot"); }); Array.prototype.forEach.call(table.querySelectorAll(".hotcol"), function (c) { c.classList.remove("hotcol"); }); });
})();
