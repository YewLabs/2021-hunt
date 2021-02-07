(function() {
let leftChrome = 'leftChrome' in localStorage ?
    +localStorage.leftChrome : outerWidth - innerWidth;
let topChrome = 'topChrome' in localStorage ?
    +localStorage.topChrome : outerHeight - innerHeight;
document.body.addEventListener('mousemove', e => {
  if (!localStorage.devicePixelRatio) {
    localStorage.devicePixelRatio = devicePixelRatio;
  } else if (localStorage.devicePixelRatio != devicePixelRatio) {
    return;
  }
  localStorage.leftChrome = leftChrome = e.screenX - e.clientX - screenLeft - scrollX;
  localStorage.topChrome = topChrome = e.screenY - e.clientY - screenTop - scrollY;
}, {passive: true});

const count = document.getElementById('coop-count');
const canvas = document.getElementById('coop-canvas');
const context = canvas.getContext('2d');

function getSize() {
  let size = [screen.width, screen.height];
  if (outerHeight == screen.width && outerWidth == screen.height) {
    size.reverse();
  }
  if (topChrome == 0 && innerHeight < screen.height) {
    size = [innerWidth, innerHeight];
  }
  return size;
}

var lastX = 0;
var lastY = 0;
var lastTick = Date.now();

function broadcastPosition() {
  const [width, height] = getSize();
  const x = (screenLeft + leftChrome + innerWidth * motion.px) / width;
  const y = (screenTop + topChrome + innerHeight * motion.py) / height;
  const hasMoved = (x - lastX) ** 2 + (y - lastY) ** 2 > 0.001 ** 2;
  if (Date.now() > lastTick + (hasMoved ? 1000 / 60 * Object.keys(clients).length : 1000)) {
    viewerSocket.emit('updatePosition', {'x': x, 'y': y, 'active': !document.hidden});
    lastX = x;
    lastY = y;
    lastTick = Date.now();
  }
}

function redraw() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  context.save();
  context.translate(-screenLeft - leftChrome, -screenTop - topChrome);
  let active = 0;
  let inactive = 0;

  for (const key in clients) {
    clients[key].active ? active++ : inactive++;
    context.strokeStyle = clients[key].active ? 'black' : 'gray';
    context.beginPath();
    drawCircle(clients[key], 1);
    context.stroke();
  }
  count.textContent = 'Collaborators: ' + active;
  if (inactive) {
    count.textContent += ' (+' + inactive + ' inactive)';
  }
  const items = Object.entries(clients);
  for (let i = 0; i < items.length; ++i) {
    const [key1, val1] = items[i];
    if (!val1.active) continue;
    for (let j = i + 1; j < items.length; ++j) {
      const [key2, val2] = items[j];
      if (!val2.active || !circlesOverlap(val1, val2)) continue;
      context.save();
      context.beginPath();
      drawCircle(val1, 0);
      context.clip();
      context.beginPath();
      drawCircle(val2, 0);
      context.clip();
      context.beginPath();
      for (let k = j + 1; k < items.length; ++k) {
        const [key3, val3] = items[k];
        if (!val3.active || !circlesOverlap(val1, val3) || !circlesOverlap(val2, val3)) continue;
        drawCircle(val3, 0);
      }
      context.clip();
      context.drawImage(image, 0, 0, ...getSize());
      context.restore();
    }
  }
  context.restore();
}

function circlesOverlap({r: r1, x: x1, y: y1}, {r: r2, x: x2, y: y2}) {
  const [width, height] = getSize();
  r1 *= Math.sqrt(width * height);
  x1 *= width;
  y1 *= height;
  r2 *= Math.sqrt(width * height);
  x2 *= width;
  y2 *= height;
  const dr = r1 + r2;
  const dx = x2 - x1;
  const dy = y2 - y1;
  return dx * dx + dy * dy < dr * dr;
}

function drawCircle({r, x, y}, dr) {
  const [width, height] = getSize();
  r = r * Math.sqrt(width * height) + dr;
  x *= width;
  y *= height;
  context.moveTo(x + r, y);
  context.arc(x, y, r, 0, 10);
}

const container = document.getElementById('coop-container');
const start = document.getElementById('coop-start');
const image = new Image();
let clients = {};
let motion = {px: 0.5, py: 0.5, vx: 0, vy: 0};
let viewerSocket = null;

start.addEventListener('click', e => {
  container.style.display = '';
  start.style.display = 'none';

  if (window.DeviceMotionEvent && DeviceMotionEvent.requestPermission) {
    DeviceMotionEvent.requestPermission();
  }
  window.addEventListener('devicemotion', e => {
    const {x, y} = e.accelerationIncludingGravity;
    if (x == null || y == null) {
      return;
    }
    const theta = (window.orientation || 0) * Math.PI / 180;
    motion.vx += +x * Math.cos(theta) - y * Math.sin(theta);
    motion.vy += -x * Math.sin(theta) - y * Math.cos(theta);
    const v = Math.sqrt(motion.vx * motion.vx + motion.vy * motion.vy);
    if (v != 0) {
      const w = Math.max(0, v - 1);
      motion.vx *= w / v;
      motion.vy *= w / v;
    }
    motion.px += motion.vx / 10000;
    motion.py += motion.vy / 10000;
    if (motion.px < 0) { motion.px = 0; motion.vx = 0; }
    if (motion.px > 1) { motion.px = 1; motion.vx = 0; }
    if (motion.py < 0) { motion.py = 0; motion.vy = 0; }
    if (motion.py > 1) { motion.py = 1; motion.vy = 0; }
  });
  document.addEventListener('visibilitychange', broadcastPosition);
  window.addEventListener('resize', redraw);

  viewerSocket = io('wss://cooperation.perpendicular.institute', {query: {auth: '{{ puzzle.auth }}'}});
  viewerSocket.on('answerImage', data => {
    image.src = data;
    go();
  });
  viewerSocket.on('updatePositions', data => {
    clients = data;
    requestAnimationFrame(redraw);
  });
  viewerSocket.on('disconnect', () => {
    count.textContent = 'Disconnected. Refresh to reconnect.';
  });
  function go() { broadcastPosition(); requestAnimationFrame(go); }
  document.querySelector('meta[name=viewport]').content = 'width=device-width,user-scalable=no';
});
})();
