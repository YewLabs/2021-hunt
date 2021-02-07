import { KtaneSync } from './sync.js';

class KtaneTimer {
	constructor(game) {
		this.name = 'timer';
		this.game = game;

		this.lastServerUpdate = null;
		// timer value in milliseconds at the time of lastServerUpdate
		this.lastTimeLeft = null;
		this.lastTimeSinceStrike = null;
		this.numStrikes = 0;
		this.speed = 1;

		this.lastBeepTime = null;
	}
	reset(full) {
		if (full) {
			this.numStrikes = 0;
			this.lastServerUpdate = null;
			this.lastBeepTime = null;
		}
	}
	serverUpdate(msg) {
		this.lastServerUpdate = performance.now();
		this.lastTimeLeft = msg['timeLeft'];
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		this.numStrikes = msg['numStrikes'];
		this.speed = msg['speed'];
	}
	getTimeLeft() {
		const td = performance.now() - this.lastServerUpdate;
		const timeSinceUpd = td * this.speed;
		return Math.max(0, this.lastTimeLeft - timeSinceUpd);
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
	updateBeep() {
		const currTime = performance.now();
		if (this.lastBeepTime == null || (currTime - this.lastBeepTime) * this.speed >= 1000) {
			this.lastBeepTime = currTime;
			return true;
		}
		return false;
		// const timeLeft = this.getTimeLeft();
		// const timeLeftSeconds = Math.floor(timeLeft/1000);
		// if (this.lastBeepTimeLeft == null || Math.floor(this.lastBeepTimeLeft/1000) - timeLeftSeconds >= 1) {
		// 	this.lastBeepTimeLeft = timeLeft;
		// 	return true;
		// }
	}
};

export { KtaneTimer };
