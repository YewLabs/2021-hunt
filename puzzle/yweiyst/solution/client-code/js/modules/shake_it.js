import { KtaneSync } from './sync.js';

class KtaneShakeIt {
	constructor(game) {
		this.name = 'shakeit';
		this.game = game;

		this.lastServerUpdate = null;
		// timer value in milliseconds at the time of lastServerUpdate
		this.lastUpdateTimer = null;
		this.lastTimeSinceStrike = null;
	}
	reset(full) {
	}
	serverUpdate(msg) {
		this.lastServerUpdate = performance.now();
		this.lastUpdateTimer = msg['timer'];
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
	}
	getTimerVal() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastUpdateTimer
		);
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
};

export { KtaneShakeIt };
