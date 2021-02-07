import { WebSocketManager } from './ws.js';
import { KtaneGame } from './game.js';
import { KtaneGraphics } from './graphics.js';
import { Matrix3x3 } from './geom.js';

const CANVAS_WIDTH = 1000;
const CANVAS_HEIGHT = 600;

class KtaneClient {
	constructor(canvasCtx) {
		this.game = new KtaneGame(this.wsSend.bind(this));
		this.graphics = new KtaneGraphics(canvasCtx, this.game);
		this.ws = null;
		this.lastPingTime = performance.now();
		this.lastPongTime = performance.now();
		this.lastFrameTime = performance.now();
		this.currFrameTime = performance.now();
		this.cnt = 0;
	}
	update(currFrameTime) {
		const PING_INTERVAL = 1000; // ms
		const PONG_TIMEOUT = 10000; // ms
		this.cnt = this.cnt + 1;
		this.currFrameTime = currFrameTime;
		this.game.update(currFrameTime - this.lastFrameTime);
		this.graphics.draw(currFrameTime);
		this.lastFrameTime = currFrameTime;
		if (currFrameTime - this.lastPingTime > PING_INTERVAL) {
			this.wsSend({
				'type': 'ping'
			});
		}
		if (currFrameTime - this.lastPongTime > PONG_TIMEOUT) {
			this.game.restart();
			this.game.requestJoin();
		}
	}
	updateLoop(currFrameTime) {
		this.update(currFrameTime);
		window.requestAnimationFrame(
			(currFrameTime) => { this.updateLoop(currFrameTime); }
		);
	}
	startUpdateLoop() {
		window.requestAnimationFrame(
			(currFrameTime) => { this.updateLoop(currFrameTime); }
		);
	}
	handleUpdatePlayers(msg) {
		this.game.updatePlayerCounts(msg['players'], msg['spectators']);
	}
	handleUpdatePlayerPos(msg) {
		this.game.updatePlayerSlot(msg.face, msg.isDefuser, msg.debugSeed);
		this.game.highScores = msg['hiscores'];
	}
	handleUpdateState(msg) {
		if (!this.game.isReadyToStart()) {
			console.error('server shouldn\'t send state yet');
			return;
		}
		this.game.updateState(msg);
	}
	handleStop(msg) {
		this.game.stop(msg);
	}
	handlePong(msg) {
	}
	handleBadAuth() {
		window.location.href = '../';
	}
	onWsMessage(msg) {
		if (this.game.debugMode && msg['type'] != 'pong') {
			console.log(msg);
		}
		this.lastPongTime = performance.now();
		const msgType = msg.type;
		const handlers = {
			'badauth': (msg) => { this.handleBadAuth(); },
			'players': this.handleUpdatePlayers.bind(this),
			'playerPos': this.handleUpdatePlayerPos.bind(this),
			'updateState': this.handleUpdateState.bind(this),
			'stop': this.handleStop.bind(this),
			'pong': this.handlePong.bind(this),
		};
		if (msgType in handlers) {
			handlers[msgType](msg);
			return;
		}
		console.error(`invalid ws message type ${msgType}`);
	}
	onWsOpen() {
		this.game.requestJoin();
	}
	onWsClose() {
		this.game.stop();
		this.startWs();
	}
	wsSend(msg) {
		if (this.ws != null) {
			this.ws.send(msg);
			this.lastPingTime = this.currFrameTime;
		}
	}
	onMouseDown(e) {
		this.game.updateClick();
	}
	onMouseUp(e) {
		this.game.activeClick = null;
	}
	onMouseMove(e) {
		this.game.mouseX = e.offsetX;
		this.game.mouseY = e.offsetY;
	}
	startWs() {
		this.ws = new WebSocketManager();
		this.ws.init(
			this.onWsOpen.bind(this),
			this.onWsMessage.bind(this),
			this.onWsClose.bind(this),
			this.handleBadAuth.bind(this),
		);
	}
	start() {
		this.startUpdateLoop();

		this.startWs();

		const canvas = this.graphics.canvasCtx.canvas;
		canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
		canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
		canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
	}
};

function setup_canvas(width, height) {
	const c = document.getElementById('gameCanvas');
	const ctx = c.getContext('2d');
	c.width = width;
	c.height = height;
	return ctx;
}

function init() {
	const canvasCtx = setup_canvas(CANVAS_WIDTH, CANVAS_HEIGHT);
	const gameCli = new KtaneClient(canvasCtx);
	gameCli.start();
}

init();
