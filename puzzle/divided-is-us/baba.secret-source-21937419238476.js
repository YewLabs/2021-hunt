IMG_WIDTH = 48;
IMG_HEIGHT = 48;
MINI_SCALE = 0.5;
JUKE_THRESHOLD = 5;

function sendReset() {
    socket.send(JSON.stringify({'type': 'reset', 'board': currentLevel[1]}))
}
function sendUndo() {
    if (!winning) {
    socket.send(JSON.stringify({'type': 'undo', 'board': currentLevel[1]}))
    }
}
function sendMove(direction) {
    socket.send(JSON.stringify({'type': 'move', 'board': currentLevel[1], 'direction': direction}))
}
function sendStart() {
    socket.send(JSON.stringify({'type': 'start', 'board': currentLevel[1]}));
}
function sendRewind() {
    const board = parseInt(currentLevel[1]);
    const state = stored_states[board][currentIndex];
    const hash  = stored_hashes[board][currentIndex];
    socket.send(JSON.stringify({'type': 'rewind', 'board': board, 'state' : state, 'hash' : hash}));
}

function clearActive(l) {
    l.forEach(id => $("#"+id).removeClass("active"))
}

levels = ['l1','l2','l3','l4','l5','l6','l7','l8','l9'];
rewind_is_active = false;

stored_states = {};
stored_hashes = {};
for (var i=1; i<=9; i++) {
  stored_states[i] = [];
  stored_hashes[i] = [];
}


function setUpClicks(l, f) {
    l.forEach(lid => {
        $("#"+lid).click( (e) => {
            clearActive(l);
            $(e.target).addClass("active");
            f(lid)
        })
    })
}
currentIndex = 0;
currentLevel = "l1";
currentPlayer = "p0";
tx = 0;
ty = 0;
maxLevel = 1;
setUpClicks(levels, l => {
    if (rewind_is_active) { return; }
    const level = parseInt(l[1]);
    currentLevel = l;
    sendStart()
});
$("#reset").click(function() {
    if (!rewind_is_active) {
        sendReset();
    }
});
$("#reload-button").click(function() { location.reload(); });

$(document).keydown(function (e) {
  if (winning) { return; }
  var arrow = { A: 65, S: 83, W: 87, D: 68, left: 37, up: 38, right: 39, down: 40, Z: 90, backspace: 8 };

  if (rewind_is_active) {
    switch (e.which) {
      case arrow.left:
      case arrow.A:
        do_rewind(-1);
        return;
      case arrow.right:
      case arrow.D:
        do_rewind(+1);
        return;
    }
  }

  switch (e.which) {
    case arrow.left:
    case arrow.A:
      sendMove('W');
      e.preventDefault();
      break;
    case arrow.up:
    case arrow.W:
      sendMove('N');
      e.preventDefault();
      break;
    case arrow.right:
    case arrow.D:
      sendMove('E');
      e.preventDefault();
      break;
    case arrow.down:
    case arrow.S:
      sendMove('S');
      e.preventDefault();
      break;
    case arrow.backspace:
    case arrow.Z:
      sendUndo();
      e.preventDefault();
      break;
  }
});


$("#minus-one-button").click(function() {
  do_rewind(-1);
});
$("#plus-one-button").click(function() {
  do_rewind(+1);
});

function do_rewind(delta) {
    if (!rewind_is_active) {
        rewind_is_active = true;
        $(".viewport").css({"filter" : "grayscale(1)"});
        $("#cancel").removeClass("hidden");
        $("#revert").removeClass("hidden");
    }
    board = parseInt(currentLevel[1]);
    currentIndex += delta;
    if (currentIndex >= stored_states[board].length) {
        currentIndex = stored_states[board].length-1;
    }
    else if (currentIndex < 0) {
        currentIndex = 0;
    }
    $("#turn-numerator").html(currentIndex+1);
    render_state(stored_states[board][currentIndex]);
}

function stopRewind() {
    currentIndex = stored_states[board].length - 1;
    $("#cancel").addClass("hidden");
    $("#revert").addClass("hidden");
    $(".viewport").css({"filter" : "grayscale(0)"});
    currentIndex = stored_states[board].length-1;
    rewind_is_active = false;
}

$("#cancel").click(function () {
    stopRewind();
    $("#turn-numerator").html(currentIndex+1);
    render_state(stored_states[board][currentIndex]);
});
$("#revert").click(function () {
    sendRewind(); // send the message
    $("#turn-numerator").html(currentIndex+1);
    stopRewind();
});



function setTitle() {
    titles = [undefined, "YOU", "TWO", "THREE", "FOUR"]
    title = titles[parseInt(currentPlayer[1])]

    if(title) $(".puzzle-title-header").html("Divided is <img src='sprites/text/"+title+".gif' width='48' height='48'>")
}

function set_max_level(n) {
    if (maxLevel < n) {
        $("#"+levels[maxLevel-1]).removeClass("last");
        maxLevel = n;
        $("#"+levels[n-1]).addClass("last");
    }
    for (i = 0;i < n; i++) {
        $("#"+levels[i]).removeClass("hidden");
    }
}
stuff = {};
function getID(x,y,t,player) {
    return x+"-"+y+"-"+t+"-"+player;
}

function check(x,y,player) {
  if (player == 'p1') {
    return (x <= tx && y <= ty);
  }
  else if (player == 'p2') {
    return (x >= tx && y <= ty);
  }
  else if (player == 'p3') {
    return (x <= tx && y >= ty);
  }
  else if (player == 'p4') {
    return (x >= tx && y >= ty);
  }
}
function shift(x,y,player) {
  if (player == 'p1') {
    return [x,y];
  }
  else if (player == 'p2') {
    return [x-tx,y];
  }
  else if (player == 'p3') {
    return [x,y-ty];
  }
  else if (player == 'p4') {
    return [x-tx,y-ty];
  }
}

function addLabelForPlayer(player) {
    if (player == currentPlayer) {
      target = $("#baba");
      var w = IMG_WIDTH;
      var h = IMG_HEIGHT;
      var fontsize = 30;
    }
    else {
      target = $("#baba-" + player);
      var w = IMG_WIDTH * MINI_SCALE;
      var h = IMG_HEIGHT * MINI_SCALE;
      var fontsize = 16;
    }
    if (player == 'p1') icon = 'sprites/text/YOU.gif';
    else if (player == 'p2') icon = 'sprites/text/TWO.gif';
    else if (player == 'p3') icon = 'sprites/text/THREE.gif';
    else if (player == 'p4') icon = 'sprites/text/FOUR.gif';

    var label = $('<div />', {
        id: "label-" + player,
        width: (tx+1)*w,
    });
    label.css("text-align", "center");
    label.css("font-size", fontsize);
    label.css({"left": parseInt(target.css('padding-left')),
      "top": 2*parseInt(target.css('padding-bottom'))+(ty+1.2)*h,"position":"absolute"});
    label.html("Player " + player[1]);
    label.appendTo(target);
}


function addElementForPlayer(x,y,t,player) {
    if (!check(x,y,player)) return;
    if (player == currentPlayer) {
      target = $("#baba");
      var w = IMG_WIDTH;
      var h = IMG_HEIGHT;
    }
    else {
      target = $("#baba-" + player);
      var w = IMG_WIDTH * MINI_SCALE;
      var h = IMG_HEIGHT * MINI_SCALE;
    }

    const [sx, sy] = shift(x,y,player);
    var img = $('<div />', {
        id: getID(x,y,t,player),
        class: "sprite"+t,
    });
    img.css({
      "left": parseInt(target.css('padding-left'))+sx*w,
      "top": parseInt(target.css('padding-top'))+sy*h,
      "position":"absolute",
      "width": w,
      "height": h,
      "background-size": "cover",
    });
    img.appendTo(target);
}

function addElement(x,y,t) {
  if (maxLevel >= JUKE_THRESHOLD) {
    addElementForPlayer(x,y,t,"p1");
    addElementForPlayer(x,y,t,"p2");
    addElementForPlayer(x,y,t,"p3");
    addElementForPlayer(x,y,t,"p4");
  }
  else {
    addElementForPlayer(x,y,t,currentPlayer);
  }
}

function removeElementForPlayer(x,y,t,player) {
    if (!check(x,y,player)) return;
    $("#"+getID(x,y,t,player)).remove();
}
function removeElement(x,y,t) {
  if (maxLevel >= JUKE_THRESHOLD) {
    removeElementForPlayer(x,y,t,"p1");
    removeElementForPlayer(x,y,t,"p2");
    removeElementForPlayer(x,y,t,"p3");
    removeElementForPlayer(x,y,t,"p4");
  }
  else {
    removeElementForPlayer(x,y,t,currentPlayer);
  }
}

function render_state(state) {
    mainbaba = $("#baba");
    width = state[0];
    height = state[1];
    mainbaba.empty();
    tx = (width-1)/2;
    ty = (height-1)/2;
    if (maxLevel > 1) {
      $("#rewind-controls").removeClass("hidden");
    }

    mainbaba.width((tx+1)*IMG_WIDTH);
    mainbaba.height((ty+1)*IMG_HEIGHT);
    if (maxLevel >= JUKE_THRESHOLD) {
      for (var i=1;i<=4;i++) {
        var player = "p" + i;
        if (currentPlayer == player) {
          $("#baba-"+player).remove();
        }
        else {
          $("#baba-"+player).empty();
          $("#baba-"+player).show();
          $("#baba-"+player).width((tx+1)*IMG_WIDTH*MINI_SCALE);
          $("#baba-"+player).height((ty+1)*IMG_HEIGHT*MINI_SCALE);
        }
        addLabelForPlayer(player);
      }
    } else {
      for (var i=1;i<=4;i++) {
        var player = "p" + i;
        $("#baba-"+player).hide();
      }
    }

    if(state.length%3 != 2) {
        throw "Invalid state";
    }
    for(var i=2;i<state.length;i+=3) {
        x = state[i];
        y = state[i+1];
        t = state[i+2];
        addElement(x,y,t);
    }
}

function process_full_state_message(board, state, won, hash) {
    var i;
    if (stored_hashes[board][0] == hash) {
        i = 0;
    }
    else {
        i = stored_hashes[board].lastIndexOf(hash);
        if (i==-1) {
            i = 0;
        }
    }

    stored_states[board] = stored_states[board].slice(0,i);
    stored_hashes[board] = stored_hashes[board].slice(0,i);
    stored_states[board].push(state);
    stored_hashes[board].push(hash);

    if (board != parseInt(currentLevel[1])) {
        return;
    }
    winning = won;

    if (rewind_is_active) {
        stopRewind();
    }
    render_state(state);
    currentIndex = stored_states[board].length - 1;
    $("#turn-numerator").html(currentIndex+1);
    $("#turn-denominator").html(currentIndex+1);
}

function process_update(board, diff, won, hash) {
    // Create a new state
    const old_state = stored_states[board][stored_states[board].length-1];
    var new_state = old_state.slice(0); // deep copy
    diff.forEach(value => {
        if(value[2]) {
            new_state.push(value[0]);
            new_state.push(value[1]);
            new_state.push(value[3]);
        } else {
            for (var i=2; i < new_state.length; ++i) {
                if ((new_state[i] == value[0]) && (new_state[i+1] == value[1]) && (new_state[i+2] == value[3])) {
                    // delete the object
                    new_state = new_state.slice(0,i).concat(new_state.slice(i+3));
                    break;
                }
            }
        }
    });
    stored_states[board].push(new_state);
    stored_hashes[board].push(hash);

    if(board != parseInt(currentLevel[1])) {
        return;
    }

    if (rewind_is_active) {
      if (won) {
        stopRewind();
      }
      else {
        $("#turn-denominator").html(stored_states[board].length);
        return;
      }
    }
    currentIndex = stored_states[board].length - 1;
    $("#turn-numerator").html(currentIndex+1);
    $("#turn-denominator").html(currentIndex+1);

    // render update
    diff.forEach(value => {
        if(value[2]) {
            addElement(value[0],value[1],value[3]);
        } else {
            removeElement(value[0],value[1],value[3]);
        }
    });

    if (won) {
        alert("Congratulations!");
        if (currentLevel == maxLevel) {
          currentLevel++;
          maxLevel++;
          sendStart();
        }
        else {
          winning = true;
        }
    }
}

if (location.protocol === "https:") {
    socket = new WebSocket(
        `wss://${window.location.host}/ws/puzzle/divided-is-us`);
} else {
    socket = new WebSocket(
        `ws://${window.location.host}/ws/puzzle/divided-is-us`);
}
socket.onopen = function (e) {
    console.log('socket opened!');
    socket.send(JSON.stringify({'type': 'AUTH', 'data': auth_token}));
};

socket.onmessage = function (e) {
    data = JSON.parse(e.data);
    if (data['type'] == 'fullstate') {
        process_full_state_message(data['board'], data['state'], data['won'], data['hash'])
    }
    else if (data['type'] == 'init' ) {
        set_max_level(data['level'])
        if (typeof data['player'] !== 'undefined') {
          currentPlayer = 'p'+data['player']
        }
        setTitle();
    }
    else if (data['type'] == 'update' ) {
        process_update(data['board'], data['diff'], data['won'], data['hash'])
    } else {
        console.log('Received unexpected server message:', data['type']);
    }
};

socket.onclose = function (e) {
    alert('Disconnected. Refresh to reconnect.');
    $(".viewport").css({"opacity": "50%"});
    $("#reload").removeClass("hidden");
}
