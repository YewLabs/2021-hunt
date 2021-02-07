// TODO: make sure this is set to the correct endpoint eventually
// change this to the local endpoint to work with the testing server
// this is necessary because the local server runs the websockets server
// on a different port from the static server
const protocol = (location.protocol === 'https:') ? 'wss' : 'ws';
const WEBSOCKETS_ENDPOINT =
	(window.location.host == 'localhost:8000') ?
	'ws://localhost:8001' :
	`${protocol}://${window.location.host}/ws/puzzle/yweiyst`;

class WebSocketManager {
	constructor() {
		this.ws = null;
		this.isOpen = false;
	}
	init(onopen, onmessage, onclose, onbadauth) {
		this.ws = new WebSocket(WEBSOCKETS_ENDPOINT);
		this.ws.onopen = (e) => {
			const urlParams = new URLSearchParams(window.location.search);
			if (!urlParams.has('token')) {
				onbadauth();
			}
			this.ws.send(JSON.stringify({
				'type': 'AUTH',
				'data': urlParams.get('token')
			}));
			this.isOpen = true;
			onopen();
		};
		this.ws.onmessage = (e) => {
			const data = JSON.parse(e.data);
			onmessage(data);
		};
		this.ws.onclose = (e) => {
			this.isOpen = false;
			onclose();
		}
	}
	send(msg) {
		if (this.isOpen) {
			this.ws.send(JSON.stringify(msg));
		}
	}
};

export { WebSocketManager };
