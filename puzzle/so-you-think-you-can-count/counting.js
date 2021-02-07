const debug = true;
function dlog(msg) {
  if (debug) { console.log(msg); }
};

const authToken = JSON.parse(document.getElementById('auth-token').textContent);

const chatSocket = new WebSocket(
  (location.protocol === "https:" ? "wss://" : "ws://") +
    `${window.location.host}/ws/puzzle/counting`);

chatSocket.onopen = function(e) {
  dlog('boop!');
  chatSocket.send(JSON.stringify({'type': 'AUTH', 'data': authToken}));
};

chatSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  if (data.type == 'info') {
    console.log('I: ' + data.message);
  } else if (data.type == 'best') {
    score = document.querySelector('#best-score');
    score.className = (data.score >= data.goal ? 'complete' : 'incomplete')
    score.innerText = data.score.toString();
    document.querySelector('#best-goal').innerHTML = data.goal.toString();
  } else if (data.type == 'debug') {
    console.log('D: ' + data.message);
  } else if (data.type == 'status') {
    document.querySelector('#chat-status').innerHTML = data.message;
  } else if (data.type == 'mark') {
    document.querySelector(`#msg-${data['message_id']}`).className += " " + data.css_class;
  } else if (data.type == 'big-enough') {
    message = data.message.replace(/^\s+|\s+$/g, '');
    document.querySelector(`#msg-${data['message_id']}`).innerHTML =
      `<span class="chat-name">Singing Creodont:</span> ${message}`;
  } else if (data.type == 'leader') {
    document.querySelector('#chat-status').className = 'leader';
  } else if (data.type == 'non-leader') {
    document.querySelector('#chat-status').className = '';
  } else {
    sender = ('sender' in data) ?
      `<span class="chat-name">${data.sender}:</span> ` : '';
    message = data.message.replace(/^\s+|\s+$/g, '');
    if (message) {
      game_display = document.querySelector('#chat-log');
      game_display.innerHTML +=
        `<div id="msg-${data.id}" class="chat-text">${sender}${message}</div>`;
      game_display.scrollTop = game_display.scrollHeight;
    }
  }
};

chatSocket.onclose = function(e) {
  console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
  if (e.keyCode === 13) {  // enter, return
    document.querySelector('#chat-message-submit').click();
  }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
  if (this.disabled) { return; }
  const messageInputDom = document.querySelector('#chat-message-input');
  const message = messageInputDom.value;
  chatSocket.send(JSON.stringify({
    'type': 'chat',
    'message': message,
  }));
  messageInputDom.value = '';

  document.querySelector('#chat-message-submit').disabled = true;
  enforce_cooldown(5);
};

enforce_cooldown = function (n) {
  if (n > 0) {
    document.querySelector('#chat-cooldown').innerText = `0:0${n}`;
    setTimeout(enforce_cooldown, 1000, n - 1);
  } else {
    document.querySelector('#chat-cooldown').innerText = '';
    document.querySelector('#chat-message-submit').disabled = false;
  }
};
