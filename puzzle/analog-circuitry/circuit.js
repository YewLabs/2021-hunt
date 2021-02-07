var editable = [1, 11, 12, 19, 33, 34, 43, 44, 51, 57, 70, 79, 83, 84, 91, 98, 104, 110, 116, 137, 141, 142, 149, 158, 162, 163, 169, 199, 206, 215, 219, 228, 229, 238, 239, 257, 261, 265, 270, 271, 278, 284, 290, 310, 314, 318, 322, 326, 349, 350, 356, 365, 367, 376, 377, 384, 409, 410, 417, 427, 432, 436, 440, 441, 448, 461, 470, 474, 478, 494, 498, 502, 503, 509]

var boxes = [25 ,63 ,97 ,123,148,176,220,246,266,296,327,366,390,428,454,479,516];
var depends = {};
depends[25] = [19, 1, 11, 12]
depends[63] = [33, 34, 43, 44, 51, 57]
depends[97] = [70, 79, 83, 84, 91]
depends[123] = [104, 98, 116, 110]
depends[148] = [137, 141, 142]
depends[176] = [162, 163, 169, 141, 149, 158]
depends[220] = [215, 219, 206, 199]
depends[246] = [228, 229, 238, 239]
depends[266] = [257, 261, 265]
depends[296] = [290, 270, 271, 278, 284]
depends[327] = [322, 326, 310, 314, 318]
depends[366] = [365, 356, 349, 350]
depends[390] = [376, 377, 384, 367]
depends[428] = [409, 410, 417, 427]
depends[454] = [448, 432, 436, 440, 441]
depends[479] = [474, 478, 461, 470]
depends[516] = [494, 498, 502, 503, 509]

var texts = {};
var outerTexts = {};
var svgNS = "http://www.w3.org/2000/svg";

function setText(n, value) {
    texts[n].textContent = value[0];
    outerTexts[n].setAttributeNS(null,"font-size","10");
    var eltBB = getElement(n).children[0].getBBox();
    var textBB = outerTexts[n].getBBox();
    var widthTransform = textBB.width / eltBB.width;
    var heightTransform = textBB.height / eltBB.height;
    var ratio = widthTransform > heightTransform ? widthTransform : heightTransform;
    currSize = 10;

    while (value > 0.8) {
            var textBB = outerTexts[n].getBBox();
    var widthTransform = textBB.width / eltBB.width;
    var heightTransform = textBB.height / eltBB.height;
    var ratio = widthTransform > heightTransform ? widthTransform : heightTransform;
        outerTexts[n].setAttributeNS(null,"font-size",currSize*.8/value);
        currSize = currSize*.8/ratio;
    }
    if(value[1] == 'yes') {
        setColor(n, '#39FF14');
    } else {
        setColor(n, 'rgba(0,0,0,0');
    }

}
function setColor(n, value, animate) {
    getElement(n).children[0].style.transition = "fill "+(animate || 0) + "ms";
    getElement(n).children[0].style.fill = value;
}
function getColor(n, value) {
    return getElement(n).children[0].style.fill;
}
loaded = false;
function onLoad() {
    loaded = true;
    setCursors("pointer");
}

nextColor = {
    "red": "green",
    "green": "blue",
    "blue": "red",
}
// recentCount = 0;
function doClick(n) {
    if (!loaded) {
        alert("Disconnected. Refresh to reconnect.");
        return;
    }
    if (locked) {
        return;
    }
    Object.keys(depends).forEach(key => {
        if(depends[key].includes(n)) {
            setText(key, "");
            setColor(key, "gray");
        }
    });
    color = getColor(n);
    new_color = nextColor[color]|| "red";
    // setColor(n, "gray", 0);
    setColor(n, new_color, 1300);

    setTimeout(() => {
        socket.send(JSON.stringify({'type': 'colortoggle', 'box': n, 'color': new_color}));
        unlock();
    }, 1000);
    // setTimeout(() => {recentCount -= 1;setLimits();}, 60*1000);
    // recentCount += 1;
    lock();
    // setLimits();
}
// function setLimits() {

// }
locked = false;
function lock() {
    if(!loaded) {
        return;
    }
    setCursors("wait");
    locked = true;
}
function unlock() {
    if(!loaded) {
        return;
    }
    setCursors("pointer");
    locked = false;
}
let socket = null;

function setCursors(cursor) {
    editable.forEach(n => {
        getElement(n).children[0].style.cursor = cursor;
    });
    document.getElementsByTagName("body")[0].style.cursor = (cursor == 'wait') ? cursor : 'default';
}
  if (location.protocol === "https:") {
    socket = new WebSocket(
      `wss://${window.location.host}/ws/puzzle/analog-circuitry`);
  } else {
    socket = new WebSocket(
      `ws://${window.location.host}/ws/puzzle/analog-circuitry`);
  }
  socket.onopen = function (e) {
    console.log('socket opened!');
    socket.send(JSON.stringify({'type': 'AUTH', 'data': auth_token}));
  };

  socket.onmessage = function (e) {
    data = JSON.parse(e.data);
    if (data['type'] == 'initialState') {
      onLoad();
    }
    if (data['type'] == 'statusUpdate' || data['type'] == 'initialState') {
      Object.entries(data['words']).forEach(entry => setText(entry[0],entry[1]));
      Object.entries(data['colors']).forEach(entry =>setColor(entry[0],entry[1]));
    } else {
      console.log('Received unexpected server message');
      console.log(data);
    }
  };

  socket.onclose = function (e) {
    alert('Disconnected. Refresh to reconnect.');
    setCursors("pointer");
    editable.forEach(n => {
        getElement(n).onclick = (event) => alert("Disconnected. Refresh to reconnect.");
    });
  }
function getElement(n) {
    return document.getElementById("line2d_"+n)
}


editable.forEach(n => {
    setColor(n, "#333");
    getElement(n).onclick = () => doClick(n);
});

boxes.forEach(n => {
    n = n + "";
    e = getElement(n);
    var newText = document.createElementNS(svgNS,"text");
    newText.setAttributeNS(null,"x",e.getBBox().x+e.getBBox().width*0.05);
    newText.setAttributeNS(null,"y",e.getBBox().y+e.getBBox().height*.7);
    newText.setAttributeNS(null,"font-size","10");
    newText.setAttributeNS(null,"font-family","monospace");
    outerTexts[n] = newText;

    var textNode = document.createTextNode("")
    newText.appendChild(textNode);
    texts[n] = textNode;
    e.appendChild(newText);

})
