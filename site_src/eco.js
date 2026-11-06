(function () {
  var svg = document.getElementById("eco"); if (!svg) return;
  var edges = Array.prototype.slice.call(svg.querySelectorAll(".edge"));
  function focus(id) {
    edges.forEach(function (e) { var on = !id || e.dataset.a === id || e.dataset.b === id; e.classList.toggle("dim", !on); e.classList.toggle("hl", !!id && on); });
  }
  Array.prototype.forEach.call(svg.querySelectorAll(".node"), function (n) {
    n.addEventListener("mouseenter", function () { focus(n.dataset.id); }); n.addEventListener("mouseleave", function () { focus(null); });
    n.addEventListener("focusin", function () { focus(n.dataset.id); }); n.addEventListener("focusout", function () { focus(null); });
  });
})();
