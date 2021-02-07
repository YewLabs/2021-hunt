const connectedPorts = [];
var socket = null;
self.addEventListener('connect', ({ ports }) => {
  const port = ports[0];
  connectedPorts.push(port);
  port.addEventListener('message', ({ data }) => {
    const { action, value } = data;

    if (action == 'auth') {
      if (socket == null || socket.readyState != WebSocket.OPEN) {
        var url = value.url;
        var auth = value.auth;
        socket = new WebSocket(url);
        socket.onopen = function() {
          socket.send(JSON.stringify({type: 'AUTH', data: auth}));
        };

        socket.onmessage = function(e) {
          connectedPorts.forEach(port => port.postMessage(e.data));
        }
      }
    } else if (action == 'unload') {
      connectedPorts.splice(connectedPorts.indexOf(port), 1);
    }
  });

  port.start();
});
