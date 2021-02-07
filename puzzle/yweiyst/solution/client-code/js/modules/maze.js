import { KtaneSync } from './sync.js';

class KtaneMaze {
	constructor(game) {
		this.name = 'maze';
		this.game = game;

		this.lastServerUpdate = null;
		this.lastTimeSinceStrike = null;
		this.disarmed = false;
		this.x = null;
		this.y = null;
		this.goalX = 0;
		this.goalY = 0;
		this.horzEdges = null;
		this.vertEdges = null;
		this.clientTxn = 0;
		this.serverTxn = 0;
	}
	reset(full) {
		this.clientTxn = 0;
		this.serverTxn = 0;
		if (full) {
			this.lastServerUpdate = null;
			this.disarmed = false;
			this.x = null;
			this.y = null;
			this.horzEdges = null;
			this.vertEdges = null;
		}
	}
	serverUpdate(msg) {
		this.lastServerUpdate = performance.now();
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		this.serverTxn = msg['txn'];
		if (this.serverTxn > this.clientTxn) {
			this.clientTxn = this.serverTxn;
		}
		this.disarmed = msg['disarmed'];
		if ('horzEdges' in msg) {
			this.horzEdges = msg['horzEdges'];
			this.vertEdges = msg['vertEdges'];
			this.x = msg['x'];
			this.y = msg['y'];
		}
		if (this.serverTxn > this.clientTxn) {
			this.clientTxn = this.serverTxn;
			this.game.sendModuleInput(
				this.game.getActiveSubmodule(this.name),
				{
					'txn': this.clientTxn,
				}
			);
		}
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
	getHorzEdge(x, y) {
		return ((this.horzEdges[y] >> x) & 1) == 1;
	}
	getVertEdge(x, y) {
		return ((this.vertEdges[x] >> y) & 1) == 1;
	}
	doInput(direction) {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		if (this.disarmed) {
			return;
		}
		this.clientTxn++;
		this.game.sendModuleInput(
			this.game.getActiveSubmodule(this.name),
			{
				'direction': direction,
				'txn': this.clientTxn,
			}
		);
	}
};

export { KtaneMaze };
