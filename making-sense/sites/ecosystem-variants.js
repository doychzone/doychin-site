/* Where Making Sense lives: preview variants.
   Draws SVG connections and points the data-current card to / in the same tab. */
(function () {
  var SITES = {
    doychin: "/",
    doychzone: "https://www.doychzone.com/",
    moytu: "https://www.moytu.com/",
    theagegames: "https://theagegames.com"
  };

  function applyCurrent(root) {
    var current = root.getAttribute("data-current");
    var cards = root.querySelectorAll(".ms-eco-card");
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var site = card.getAttribute("data-site");
      if (site === current) {
        card.removeAttribute("target");
        card.removeAttribute("rel");
        card.setAttribute("href", "/");
      } else {
        card.setAttribute("target", "_blank");
        card.setAttribute("rel", "noopener");
        if (SITES[site]) card.setAttribute("href", SITES[site]);
      }
    }
  }

  function rectIn(el, root) {
    var a = el.getBoundingClientRect();
    var b = root.getBoundingClientRect();
    return {
      left: a.left - b.left,
      top: a.top - b.top,
      width: a.width,
      height: a.height,
      cx: a.left - b.left + a.width / 2,
      cy: a.top - b.top + a.height / 2
    };
  }

  function edgeToward(box, tx, ty) {
    var dx = tx - box.cx;
    var dy = ty - box.cy;
    if (dx === 0 && dy === 0) return { x: box.cx, y: box.cy };
    var hx = box.width / 2;
    var hy = box.height / 2;
    var sx = Math.abs(dx) < 0.001 ? Infinity : hx / Math.abs(dx);
    var sy = Math.abs(dy) < 0.001 ? Infinity : hy / Math.abs(dy);
    var t = Math.min(sx, sy);
    return { x: box.cx + dx * t, y: box.cy + dy * t };
  }

  function quad(x1, y1, x2, y2, bow) {
    var dx = x2 - x1;
    var dy = y2 - y1;
    var cx = (x1 + x2) / 2 - dy * bow;
    var cy = (y1 + y2) / 2 + dx * bow;
    return "M " + x1.toFixed(1) + " " + y1.toFixed(1) +
      " Q " + cx.toFixed(1) + " " + cy.toFixed(1) +
      " " + x2.toFixed(1) + " " + y2.toFixed(1);
  }

  function cubic(x1, y1, c1x, c1y, c2x, c2y, x2, y2) {
    return "M " + x1.toFixed(1) + " " + y1.toFixed(1) +
      " C " + c1x.toFixed(1) + " " + c1y.toFixed(1) +
      ", " + c2x.toFixed(1) + " " + c2y.toFixed(1) +
      ", " + x2.toFixed(1) + " " + y2.toFixed(1);
  }

  function clearGroup(g) {
    while (g.firstChild) g.removeChild(g.firstChild);
  }

  function el(name, attrs) {
    var node = document.createElementNS("http://www.w3.org/2000/svg", name);
    for (var k in attrs) node.setAttribute(k, attrs[k]);
    return node;
  }

  function isStacked(stage) {
    return window.matchMedia("(max-width: 700px)").matches;
  }

  function drawMap(stage, svg) {
    var origin = stage.querySelector(".ms-eco-origin");
    var mark = stage.querySelector(".ms-eco-origin-mark") || origin;
    var cards = stage.querySelectorAll(".ms-eco-card");
    var o = rectIn(mark, stage);
    var paths = svg.querySelector(".ms-eco-connections");
    var dots = svg.querySelector(".ms-eco-nodes");
    clearGroup(paths);
    clearGroup(dots);
    var stroke = {
      fill: "none",
      stroke: "rgba(239,237,228,0.55)",
      "stroke-width": "1.5",
      "stroke-dasharray": "6 7",
      "stroke-linecap": "round"
    };
    if (isStacked(stage)) {
      var full = rectIn(origin, stage);
      var railX = 14;
      var startY = full.top + full.height + 6;
      var last = rectIn(cards[cards.length - 1], stage);
      paths.appendChild(el("path", Object.assign({
        d: quad(full.cx, full.top + full.height + 2, railX, startY + 18, 0.2)
      }, stroke)));
      paths.appendChild(el("path", Object.assign({
        d: "M " + railX.toFixed(1) + " " + (startY + 18).toFixed(1) +
          " L " + railX.toFixed(1) + " " + last.cy.toFixed(1)
      }, stroke)));
      for (var i = 0; i < cards.length; i++) {
        var c = rectIn(cards[i], stage);
        paths.appendChild(el("path", Object.assign({
          d: "M " + railX.toFixed(1) + " " + c.cy.toFixed(1) +
            " L " + (c.left - 2).toFixed(1) + " " + c.cy.toFixed(1)
        }, stroke)));
        dots.appendChild(el("circle", {
          cx: (c.left - 2).toFixed(1),
          cy: c.cy.toFixed(1),
          r: "2.5",
          fill: "#efede4"
        }));
      }
    } else {
      var bows = { doychin: 0.14, doychzone: -0.1, moytu: -0.12, theagegames: 0.16 };
      for (var j = 0; j < cards.length; j++) {
        var card = cards[j];
        var c = rectIn(card, stage);
        var start = edgeToward(o, c.cx, c.cy);
        var end = edgeToward(c, o.cx, o.cy);
        var site = card.getAttribute("data-site");
        var bow = bows[site] != null ? bows[site] : 0.12;
        paths.appendChild(el("path", Object.assign({
          d: quad(start.x, start.y, end.x, end.y, bow)
        }, stroke)));
        dots.appendChild(el("circle", {
          cx: end.x.toFixed(1),
          cy: end.y.toFixed(1),
          r: "2.5",
          fill: "#efede4"
        }));
      }
    }
    if (!isStacked(stage)) {
      dots.appendChild(el("circle", {
        cx: o.cx.toFixed(1),
        cy: o.cy.toFixed(1),
        r: "3",
        fill: "#b0551f"
      }));
    }
  }

  function drawTree(stage, svg) {
    var origin = stage.querySelector(".ms-eco-origin");
    var cards = stage.querySelectorAll(".ms-eco-card");
    var o = rectIn(origin, stage);
    var paths = svg.querySelector(".ms-eco-connections");
    var dots = svg.querySelector(".ms-eco-nodes");
    clearGroup(paths);
    clearGroup(dots);
    var mobile = isStacked(stage);
    var trunkX = mobile ? 14 : o.cx;
    var trunkTop = o.top + o.height + 2;
    var last = rectIn(cards[cards.length - 1], stage);
    var forkY;
    if (mobile) {
      forkY = trunkTop + 24;
    } else {
      var firstCard = rectIn(cards[0], stage);
      forkY = (trunkTop + firstCard.top) / 2 - 8;
    }
    if (mobile) {
      paths.appendChild(el("path", {
        d: cubic(o.cx, trunkTop, o.cx, trunkTop + 10, trunkX, forkY - 16, trunkX, forkY),
        fill: "none",
        stroke: "#b0551f",
        "stroke-width": "3",
        "stroke-linecap": "round"
      }));
      paths.appendChild(el("path", {
        d: "M " + trunkX.toFixed(1) + " " + forkY.toFixed(1) +
          " L " + trunkX.toFixed(1) + " " + last.cy.toFixed(1),
        fill: "none",
        stroke: "#b0551f",
        "stroke-width": "3",
        "stroke-linecap": "round"
      }));
    } else {
      paths.appendChild(el("path", {
        d: "M " + trunkX.toFixed(1) + " " + trunkTop.toFixed(1) +
          " L " + trunkX.toFixed(1) + " " + forkY.toFixed(1),
        fill: "none",
        stroke: "#b0551f",
        "stroke-width": "3.5",
        "stroke-linecap": "round"
      }));
    }
    dots.appendChild(el("circle", {
      cx: trunkX.toFixed(1),
      cy: forkY.toFixed(1),
      r: "3.5",
      fill: "#b0551f"
    }));
    for (var i = 0; i < cards.length; i++) {
      var c = rectIn(cards[i], stage);
      var endX, endY, c1x, c1y, c2x, c2y, startX, startY;
      if (mobile) {
        startX = trunkX;
        startY = c.cy;
        endX = c.left - 2;
        endY = c.cy;
        c1x = startX + 8;
        c1y = startY;
        c2x = endX - 8;
        c2y = endY;
      } else {
        startX = trunkX;
        startY = forkY;
        endX = c.cx;
        endY = c.top - 2;
        var mid = (endY - startY);
        c1x = startX + (endX - startX) * 0.06;
        c1y = startY + mid * 0.62;
        c2x = endX;
        c2y = startY + mid * 0.72;
      }
      paths.appendChild(el("path", {
        d: cubic(startX, startY, c1x, c1y, c2x, c2y, endX, endY),
        fill: "none",
        stroke: "#efede4",
        "stroke-width": "1.7",
        "stroke-linecap": "round",
        "stroke-linejoin": "round"
      }));
      dots.appendChild(el("circle", {
        cx: endX.toFixed(1),
        cy: endY.toFixed(1),
        r: "2.6",
        fill: "#b0551f"
      }));
    }
  }

  function sizeSvg(stage, svg) {
    var w = stage.clientWidth;
    var h = stage.clientHeight;
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);
  }

  function draw(root) {
    var stage = root.querySelector(".ms-eco-stage");
    var svg = root.querySelector(".ms-eco-paths");
    if (!stage || !svg) return;
    sizeSvg(stage, svg);
    if (stage.classList.contains("ms-eco-stage--map")) drawMap(stage, svg);
    else if (stage.classList.contains("ms-eco-stage--tree")) drawTree(stage, svg);
  }

  function setup(root) {
    applyCurrent(root);
    var drawNow = function () { draw(root); };
    drawNow();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawNow);
    var imgs = root.querySelectorAll("img");
    for (var i = 0; i < imgs.length; i++) {
      if (!imgs[i].complete) imgs[i].addEventListener("load", drawNow);
    }
    if (typeof ResizeObserver !== "undefined") {
      var ro = new ResizeObserver(drawNow);
      var stage = root.querySelector(".ms-eco-stage");
      if (stage) ro.observe(stage);
    } else {
      window.addEventListener("resize", drawNow);
    }
  }

  function run() {
    var roots = document.querySelectorAll(".ms-eco");
    for (var i = 0; i < roots.length; i++) setup(roots[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
