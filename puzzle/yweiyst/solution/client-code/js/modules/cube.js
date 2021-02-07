import { KtaneSync } from './sync.js';

class KtaneCube {
	constructor(game) {
		this.name = 'cube';
		this.game = game;
		this.lastServerUpdate = null;
		this.lastTimeSinceStrike = null;
		this.disarmed = false;
		this.text = '';
		this.started = false;
	}
	reset(full) {
		if (full) {
			this.disarmed = false;
			this.lastServerUpdate = null;
			this.text = '';
			this.started = false;
		}
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
	doInput() {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		if (this.disarmed) {
			return;
		}
		this.game.sendModuleInput(
			this.name, {}
		);
	}
	serverUpdate(msg) {
		this.lastServerUpdate = performance.now();
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		this.disarmed = msg['disarmed'];
		this.text = msg['text'];
		this.started = msg['started'];
	}
};

export { KtaneCube };
