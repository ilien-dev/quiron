// The language switch wins over the browser's language: remember what was picked.
document.querySelectorAll("[data-lang]").forEach(function (link) {
  link.addEventListener("click", function () {
    try { localStorage.setItem("quiron-lang", link.dataset.lang); } catch (e) {}
  });
});
