import { KtaneSync } from './sync.js';
import { QuadrantButton, TextButton, TriangleButton } from '../graphics_components.js';

class KtaneSimon {
	constructor(game) {
		this.name = 'simon';
		this.game = game;

		this.lastServerUpdate = null;
		this.lastTimeSinceStrike = null;
		this.lastPeriodReset = null;
		this.disarmed = false;
		this.roundNum = 0;
		this.seq = null;
		this.clientTxn = 0;
		this.serverTxn = 0;
	}
	reset(full) {
		this.clientTxn = 0;
		this.serverTxn = 0;
		if (full) {
			this.lastServerUpdate = null;
			this.disarmed = false;
			this.roundNum = 0;
			this.seq = null;
			this.clientTxn = 0;
			this.serverTxn = 0;
			this.lastPeriodReset = null;
		}
	}
	serverUpdate(msg) {
		this.lastServerUpdate = performance.now();
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		if ('roundNum' in msg) {
			if (this.seq == null || this.roundNum != msg['roundNum']) {
				this.lastReset = performance.now();
			}
			this.roundNum = msg['roundNum'];
		}
		this.disarmed = msg['disarmed'];
		if ('txn' in msg) {
			this.serverTxn = msg['txn'];
			if (this.serverTxn > this.clientTxn) {
				this.clientTxn = this.serverTxn;
			}
		}
		if ('seq' in msg) {
			this.seq = msg['seq'];
		}
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
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

export { KtaneSimon };
