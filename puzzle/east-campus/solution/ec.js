function getPos(path) {
  let width = 400;
  const height = 60;
  let x = 800,
    y = 750;
  let i = 0;
  for (const l of path) {
    i += 1;
    x += l === "R" ? width : -width;
    y -= height;
    width *= 0.5;
  }
  const oldX = x;
  x = horizLocMap[x] || x;
  // if (horizLocMap[oldX] === undefined) {
  //   console.log("missing", x);
  // }
  return [x, y];
}
function drawLine(ctx, path, letter) {
  const pos1 = getPos(path.substr(0, path.length - 1));
  const pos2 = getPos(path);
  const left = path.substr(path.length - 1) === "R";
  ctx.beginPath();
  ctx.moveTo(pos1[0], pos1[1] - 4);
  ctx.lineTo(pos2[0], pos2[1]);
  ctx.strokeStyle = left ? "black" : "#964b00";
  ctx.stroke();
  ctx.fillStyle = "black";

  ctx.fillRect(pos2[0] - 3, pos2[1] - 4, 7, 9);

  if (letter) {
    ctx.fillStyle = "white";
    ctx.fillText(letter, pos2[0] - 2.5, pos2[1] + 3.7);
  }
}
const paths = [
  ["LLL", "B"],
  ["LLLLRRRLRR", " "],
  ["LLLRL", "Q"],
  ["LLLRLL", "E"],
  ["LLLRLLRRRRL", " "],
  ["LLLRLRL", "D"],
  ["LLLRLRLL", "I"],
  ["LLLRLRLLL", "U"],
  ["LLLRLRLLRL", "C"],
  ["LLLRLRLLRR", "K"],
  ["LLLRLRLR", " "],
  ["LLLRLRRRRLLLR", " "],
  ["LLLRRLLR", "O"],
  ["LLR", "H"],
  ["LLRL", "T"],
  ["LLRLLLLLLLLL", " "],
  ["LLRLRLLLLRR", " "],
  ["LLRLRLRLRLL", " "],
  ["LLRR", "O"],
  ["LLRRL", "I"],
  ["LLRRLR", "S"],
  ["LLRRLRRR", "G"],
  ["LLRRRLL", "S"],
  ["LLRRRLLRLLRRR", " "],
  ["LLRRRLLRRRLRL", " "],
  ["LLRRRLLRRRLRR", " "],
  ["LLRRRLLRRRRRR", " "],
  ["LLRRRLLRRRRRR", " "],
  ["LLRRRRRR", "E"],
  ["LRLL", "T"],
  ["LRLLL", "E"],
  ["LRLLR", "E"],
  ["LRLLRLLR", "H"],
  ["LRLLRLRLLR", " "],
  ["LRLRLRLLRRR", " "],
  ["LRLRRL", "W"],
  ["LRRL", "E"],
  ["LRRLRLL", "S"],
  ["LRRLRLLR", "T"],
  ["LRRLRLR", "P"],
  ["LRRLRLRR", "L"],
  ["LRRLRLRRLL", "A"],
  ["LRRLRLRRLRL", "R"],
  ["LRRLRLRRLRRL", "A"],
  ["LRRLRLRRR", " "],
  ["LRRLRR", "L"],
  ["LRRLRRRR", "E"],
  ["LRRLRRRRRLR", " "],
  ["LRRR", "K"],
  ["LRRRLL", "C"],
  ["LRRRLLLR", "L"],
  ["LRRRLR", "E"],
  ["LRRRLRLL", "H"],
  ["LRRRLRRL", "C"],
  ["LRRRR", "I"],
  ["LRRRRLL", "U"],
  ["LRRRRLLL", " "],
  ["LRRRRLLLL", "O"],
  ["LRRRRLR", "T"],
  ["LRRRRRRL", "T"],
  ["LRRRRRRLLR", " "],
  ["RLL", "T"],
  ["RLLL", "O"],
  ["RLLLLLLR", "S"],
  ["RLLLLRLL", "N"],
  ["RLLLRLR", "R"],
  ["RLLRLLRL", "H"],
  ["RLLRLRLR", "E"],
  ["RLLRR", "N"],
  ["RLLRRLLL", "R"],
  ["RLLRRLRRLRR", " "],
  ["RLR", "T"],
  ["RLRLLLRRRLRL", " "],
  ["RLRLLR", "C"],
  ["RLRLLRL", " "],
  ["RLRLLRL", "M"],
  ["RLRLLRLR", "T"],
  ["RLRLLRLRL", "S"],
  ["RLRLLRLRLLL", "O"],
  ["RLRLLRLRR", "E"],
  ["RLRLLRLRRLL", "S"],
  ["RLRRLRL", "I"],
  ["RLRRLRLLRRRRL", " "],
  ["RLRRRLLR", "O"],
  ["RLRRRRRR", "N"],
  ["RRL", "G"],
  ["RRLL", "R"],
  ["RRLLLLRLRRLLL", " "],
  ["RRLLLLRLRRRRR", " "],
  ["RRLLRLLLLR", "E"],
  ["RRLLRLLLLRL", " "],
  ["RRLLRLLLR", "A"],
  ["RRLLRLLR", " "],
  ["RRLLRLLR", "N"],
  ["RRLLRLLRL", "D"],
  ["RRLLRLR", "A"],
  ["RRLLRRL", "M"],
  ["RRLLRRLR", "E"],
  ["RRLLRRRLRLLR", " "],
  ["RRLR", "O"],
  ["RRLRLLLLLRR", " "],
  ["RRLRRLRR", "O"],
  ["RRRL", "J"],
  ["RRRLLLLRRLLLL", " "],
  ["RRRLLRLR", "D"],
  ["RRRLR", "A"],
  ["RRRLRLLL", " "],
  ["RRRLRLLL", "F"],
  ["RRRLRLLLL", "G"],
  ["RRRLRLLLLL", "B"],
  ["RRRLRLLLLLL", "O"],
  ["RRRLRLLLLR", "O"],
  ["RRRLRLLLLRR", "O"],
  ["RRRLRLLR", "B"],
  ["RRRLRLLRL", "F"],
  ["RRRLRLR", "K"],
  ["RRRLRLRL", "C"],
  ["RRRLRLRLL", "A"],
  ["RRRLRLRR", "T"],
  ["RRRLRLRRR", "O"],
  ["RRRLRRLR", "N"],
  ["RRRRL", "W"],
  ["RRRRLLLR", "S"],
  ["RRRRLLRRLRLRRL", " "],
  ["RRRRLRLR", "E"],
  ["RRRRLRRLLRRR", " "],
  ["RRRRRL", "R"],
  ["RRRRRRL", "S"],
];
const allParentPaths = new Set();
for (const p of paths) {
  for (let i = 0; i < p[0].length; i++) {
    allParentPaths.add(p[0].substr(0, i));
  }
}
const horizLocMap = {};
const xmax = 1600;
const allX = [...allParentPaths, ...paths.map((x) => x[0])].map(
  (path) => getPos(path)[0]
);
allX.sort((a, b) => a - b);
allX.forEach((x, index) => {
  horizLocMap[x] = (index * xmax) / allX.length - 350;
});
var puzzleOnLoad = function () {
  var canvas = document.getElementsByTagName("canvas")[0];
  canvas.height = 600;
  canvas.width =900;
  var ctx = canvas.getContext("2d");
  trackTransforms(ctx);
  ctx.font = "10px monospace";

  function redraw() {
    // Clear the entire canvas
    var p1 = ctx.transformedPoint(0, 0);
    var p2 = ctx.transformedPoint(canvas.width, canvas.height);
    ctx.clearRect(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y);

    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();

    for (const path of allParentPaths) {
      drawLine(ctx, path);
    }
    for (const path of paths) {
      drawLine(ctx, path[0], path[1]);
    }
  }
  redraw();

  var lastX = canvas.width / 2,
    lastY = canvas.height / 2 + 120;

  var dragStart, dragged;

  canvas.addEventListener(
    "mousedown",
    function (evt) {
      document.body.style.mozUserSelect = document.body.style.webkitUserSelect = document.body.style.userSelect =
        "none";
      lastX = evt.offsetX || evt.pageX - canvas.offsetLeft;
      lastY = evt.offsetY || evt.pageY - canvas.offsetTop;
      dragStart = ctx.transformedPoint(lastX, lastY);
      dragged = false;
    },
    false
  );

  canvas.addEventListener(
    "mousemove",
    function (evt) {
      lastX = evt.offsetX || evt.pageX - canvas.offsetLeft;
      lastY = evt.offsetY || evt.pageY - canvas.offsetTop;
      dragged = true;
      if (dragStart) {
        var pt = ctx.transformedPoint(lastX, lastY);
        ctx.translate(pt.x - dragStart.x, pt.y - dragStart.y);
        redraw();
      }
    },
    false
  );

  canvas.addEventListener(
    "mouseup",
    function (evt) {
      dragStart = null;
      if (!dragged) zoom(evt.shiftKey ? -2 : 2);
    },
    false
  );

  var scaleFactor = 1.1;
  let currScale = 1;
  const maxScale = 3;

  var zoom = function (clicks) {
    var pt = ctx.transformedPoint(lastX, lastY);
    ctx.translate(pt.x, pt.y);
    var factor = Math.pow(scaleFactor, clicks);
    if (currScale / factor > maxScale) {
      factor = 1;
    }
    ctx.scale(factor, factor);
    currScale /= factor;
    ctx.translate(-pt.x, -pt.y);
    redraw();
  };

  var handleScroll = function (evt) {
    var delta = evt.wheelDelta
      ? evt.wheelDelta / 40
      : evt.detail
      ? -evt.detail
      : 0;
    var isChrome = !!window.chrome;
    if (isChrome) {
      delta /= 10;
    }
    if (delta) zoom(delta);
    return evt.preventDefault() && false;
  };

  canvas.addEventListener("DOMMouseScroll", handleScroll, false);
  canvas.addEventListener("mousewheel", handleScroll, false);
  zoom(-6.4);
};

// Adds ctx.getTransform() - returns an SVGMatrix
// Adds ctx.transformedPoint(x,y) - returns an SVGPoint
function trackTransforms(ctx) {
  var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  var xform = svg.createSVGMatrix();
  ctx.getTransform = function () {
    return xform;
  };

  var savedTransforms = [];
  var save = ctx.save;
  ctx.save = function () {
    savedTransforms.push(xform.translate(0, 0));
    return save.call(ctx);
  };

  var restore = ctx.restore;
  ctx.restore = function () {
    xform = savedTransforms.pop();
    return restore.call(ctx);
  };

  var scale = ctx.scale;
  ctx.scale = function (sx, sy) {
    xform = xform.scaleNonUniform(sx, sy);
    return scale.call(ctx, sx, sy);
  };

  var rotate = ctx.rotate;
  ctx.rotate = function (radians) {
    xform = xform.rotate((radians * 180) / Math.PI);
    return rotate.call(ctx, radians);
  };

  var translate = ctx.translate;
  ctx.translate = function (dx, dy) {
    xform = xform.translate(dx, dy);
    return translate.call(ctx, dx, dy);
  };

  var transform = ctx.transform;
  ctx.transform = function (a, b, c, d, e, f) {
    var m2 = svg.createSVGMatrix();
    m2.a = a;
    m2.b = b;
    m2.c = c;
    m2.d = d;
    m2.e = e;
    m2.f = f;
    xform = xform.multiply(m2);
    return transform.call(ctx, a, b, c, d, e, f);
  };

  var setTransform = ctx.setTransform;
  ctx.setTransform = function (a, b, c, d, e, f) {
    xform.a = a;
    xform.b = b;
    xform.c = c;
    xform.d = d;
    xform.e = e;
    xform.f = f;
    return setTransform.call(ctx, a, b, c, d, e, f);
  };

  var pt = svg.createSVGPoint();
  ctx.transformedPoint = function (x, y) {
    pt.x = x;
    pt.y = y;
    return pt.matrixTransform(xform.inverse());
  };
}
