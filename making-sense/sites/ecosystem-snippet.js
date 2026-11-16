/* Making Sense ecosystem grid. Marks the data-current site as You are here
   and points that card to / in the same tab. The other cards stay new-tab links. */
(function () {
  function apply(root) {
    var current = root.getAttribute("data-current");
    if (!current) return;
    var cards = root.querySelectorAll(".ms-eco-card");
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      if (card.getAttribute("data-site") === current) {
        card.removeAttribute("target");
        card.removeAttribute("rel");
        card.setAttribute("href", "/");
      } else {
        card.setAttribute("target", "_blank");
        card.setAttribute("rel", "noopener");
      }
    }
  }
  function run() {
    var roots = document.querySelectorAll(".ms-eco");
    for (var i = 0; i < roots.length; i++) apply(roots[i]);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
