// hi! this puzzle is not intended to be reverse engineered. thanks

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
        socketSend(n, new_color);
        unlock();
    }, 1000);
    // setTimeout(() => {recentCount -= 1;setLimits();}, 60*1000);
    // recentCount += 1;
    lock();
    // setLimits();
}

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

function setCursors(cursor) {
    editable.forEach(n => {
        getElement(n).children[0].style.cursor = cursor;
    });
    document.getElementsByTagName("body")[0].style.cursor = (cursor == 'wait') ? cursor : 'default';
}

function getElement(n) {
    return document.getElementById("line2d_"+n)
}

// NEW CODE STARTS HERE

var node_colors = Array(74).fill("red");

function ziplongest(w1, w2) {
    var result = [];
    for (var i = 0; i < Math.max(w1.length, w2.length); i++) {
        result.push([w1[i], w2[i]]);
    }
    return result;
}

function computeGate(color, number, firstWord, secondWord) {
    if (color === "red" && number === 1) {
        return Array.from(firstWord).reverse().join("");
    } else if (color === "red" && number === 2) {
        return caesar(firstWord, 13);
    } else if (color === "red" && number === 3) {
        return Array.from(firstWord).sort().join("");
    } else if (color === "blue" && number === 1) {
        if (firstWord === "") {
            return "";
        }
        return firstWord.slice(-1).concat(firstWord.slice(0, -1));
    } else if (color === "blue" && number === 2) {
        if (firstWord === "") {
            return "";
        }
        var lastLetter = caesar(firstWord.slice(-1), 4);
        return firstWord.slice(0, -1).concat(lastLetter);
    } else if (color === "blue" && number === 3) {
        if (firstWord === "") {
            return "AY";
        }
        return firstWord.slice(1).concat(firstWord[0]).concat("AY");
    } else if (color === "green" && number === 1) {
        return Array.from(firstWord).map((c, i) => x[2*i + 1]).join("");
    } else if (color === "green" && number === 2) {
        return firstWord.slice(1, -1);
    } else if (color === "green" && number === 3) {
        return Array.from(firstWord).filter(c => !"AEIOU".includes(c)).join("");
    }
    if (!secondWord) {
        return "Invalid parameters";
    }
    if (color === "blue" && number === 4) {
        return ziplongest(firstWord, secondWord).map(x => x.join("")).join("");
    } else if (color === "blue" && number === 5) {
        return ziplongest(firstWord, secondWord).filter(([a, b]) => a === b).map(([a, b]) => a).join("");
    } else if (color === "blue" && number === 6) {
        return firstWord.concat(secondWord);
    } else if (color === "red" && number === 4) {
        return redfunc(firstWord, secondWord, (a, b) => a^b);
    } else if (color === "red" && number === 5) {
        return redfunc(firstWord, secondWord, (a, b) => a&b);
    } else if (color === "red" && number === 6) {
        return redfunc(firstWord, secondWord, (a, b) => a|b);
    } else if (color === "green" && number === 4) {
        var arr = Array.from(secondWord).map((c, i) => [c, i]).sort();
        return arr.map(([c, i]) => firstWord[i]).join("").concat(firstWord.slice(secondWord.length));
    } else if (color === "green" && number === 5) {
        if (secondWord === "") {
            return "";
        }
        return caesar(firstWord, secondWord.charCodeAt() - 64);
    } else if (color === "green" && number === 6) {
        return Array.from(firstWord).map((c, i) => {
            var v = c.charCodeAt() - 65;
            return secondWord[v] || c;
        }).join("");
    }
    return "NOT A GATE :(";
}

function caesar(plaintext, shift) {
    return Array.from(plaintext).map(
        (c, i) => String.fromCharCode(
            ((plaintext.charCodeAt(i) - 65 + shift) % 26) + 65
            )
        ).join("");
}

function letterfn(fn, a, b) {
    if (!(a && b)) {
        return a || b;
    }
    var x = a.charCodeAt() - 64;
    var y = b.charCodeAt() - 64;
    var z = fn(x, y);
    if (z > 0 && z < 27) {
        return String.fromCharCode(z + 64);
    } else {
        return "X"
    }
}

function redfunc(w1, w2, fn) {
    return ziplongest(w1, w2).map(([a, b]) => letterfn(fn, a, b)).join("");
}

var answers = ["CREATIONIST", "WATERFALL", "QUINCE", "ANTENNA", "PHASE", "SEAWATER", "NANA", "POEM", "ICE", "THEOLOGIZE", "RIA", "STORAGE", "LOVED", "RIBOSOME", "SUBPRIME", "LOBE", "BOLT", ];
function getWord(v, colors) {
    var word = getWordInternal(v, colors);
    var boxIndex = boxes.findIndex(x => x === Number(v));
    var answerIndex = answers.findIndex(x => x === word);
    if (boxIndex !== -1 && answerIndex !== -1 && boxIndex === answerIndex) {
        return [word, "yes"];
    }
    return [word, "no"];
}

function getWordInternal(v, colors) {
    if (v == 25) {
        return computeGate(colors[19], 6, computeGate(colors[1], 4, "SWING", "PELOSI"), computeGate(colors[12], 4, "BOAST", computeGate(colors[11], 1, "HAM")))
    }
    if (v == 63) {
        return computeGate(colors[57], 6, computeGate(colors[44], 4, computeGate(colors[34], 5, computeGate(colors[33], 2, "PROMO"), "EAVES"), computeGate(colors[43], 1, "EAVES")), computeGate(colors[51], 6, "HAJJ", "ATLANTAFALCONS"))
    }
    if (v == 97) {
        return computeGate(colors[91], 6, computeGate(colors[84], 4, "HAPPEN", "LOCCUM"), computeGate(colors[83], 1, computeGate(colors[79], 2, computeGate(colors[70], 6, "IN", "TRANSALPINE"))))
    }
    if (v == 123) {
        return computeGate(colors[116], 4, computeGate(colors[104], 5, computeGate(colors[98], 6, "SAFETY", "NAMES"), "MAINTENANCE"), computeGate(colors[110], 6, "HEN", "FAD"))
    }
    if (v == 148) {
        return computeGate(colors[142], 5, computeGate(colors[137], 3, "WAXMUSEUM"), computeGate(colors[141], 2, "OPOSSUM"))
    }
    if (v == 176) {
        return computeGate(colors[169], 4, computeGate(colors[162], 1, computeGate(colors[158], 1, computeGate(colors[149], 5, computeGate(colors[141], 2, "OPOSSUM"), "RAVENERS"))), computeGate(colors[163], 6, "AWED", "EXERTION"))
    }
    if (v == 220) {
        return computeGate(colors[219], 2, computeGate(colors[215], 3, computeGate(colors[206], 5, computeGate(colors[199], 4, "ENSNARE", "WHERE"), "ORNAMENTAL")))
    }
    if (v == 246) {
        return computeGate(colors[239], 4, computeGate(colors[238], 2, computeGate(colors[229], 6, "REOPEN", computeGate(colors[228], 1, "REPAIR"))), "SHAKESPEARE")
    }
    if (v == 266) {
        return computeGate(colors[265], 1, computeGate(colors[261], 2, computeGate(colors[257], 3, "ALICE")))
    }
    if (v == 296) {
        return computeGate(colors[290], 6, computeGate(colors[284], 6, "THE", computeGate(colors[271], 4, "LOGO", "FARM")), computeGate(colors[278], 5, computeGate(colors[270], 3, "CITY"), "FARM"))
    }
    if (v == 327) {
        return computeGate(colors[326], 2, computeGate(colors[322], 2, computeGate(colors[318], 2, computeGate(colors[314], 2, computeGate(colors[310], 2, "PARATRIATHLON")))))
    }
    if (v == 366) {
        return computeGate(colors[365], 1, computeGate(colors[356], 6, computeGate(colors[349], 2, "STOP"), computeGate(colors[350], 6, "BEACH", "GRENADES")))
    }
    if (v == 390) {
        return computeGate(colors[384], 6, computeGate(colors[376], 1, computeGate(colors[367], 6, "OHIO", "SPREAD")), computeGate(colors[377], 4, "CLUNK", "GECKO"))
    }
    if (v == 428) {
        return computeGate(colors[427], 1, computeGate(colors[417], 4, computeGate(colors[409], 1, "SEROTONIN"), computeGate(colors[410], 4, "IAMB", "DROP")))
    }
    if (v == 454) {
        return computeGate(colors[448], 6, computeGate(colors[440], 1, "BUS"), computeGate(colors[441], 4, computeGate(colors[436], 3, computeGate(colors[432], 2, "KVETCHY")), "SWAYS"))
    }
    if (v == 479) {
        return computeGate(colors[478], 2, computeGate(colors[474], 2, computeGate(colors[470], 3, computeGate(colors[461], 6, "DICE", "MELBOURNE"))))
    }
    if (v == 516) {
        return computeGate(colors[509], 4, computeGate(colors[502], 2, computeGate(colors[494], 2, "MAUL")), computeGate(colors[503], 6, computeGate(colors[498], 1, "HOTFIXES"), "CLAY"))
    }
}

function socketSend(box, newColor) {
    var val = editable.findIndex(v => v === box);
    node_colors[val] = newColor;
    setColor(box, newColor);

    var allColors = {};
    editable.forEach((boxid, i) => {
        allColors[boxid] = node_colors[i];
    });

    Object.keys(depends).forEach(key => {
        if (depends[key].includes(box)) {
            setText(key, getWord(key, allColors));
        }
    });
}

function init() {
    var allColors = {};
    editable.forEach((boxid, i) => {
        allColors[boxid] = node_colors[i];
        setColor(boxid, node_colors[i]);
    });
    boxes.forEach((word) => {
        setText(word, getWord(word, allColors));
    });
    setCursors("pointer");
}

// NEW CODE ENDS HERE

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

init();
