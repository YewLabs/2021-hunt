import { KtaneSync } from './sync.js';

class KtaneWhosOnFirst {
	constructor(game) {
		this.name = 'whosonfirst';
		this.game = game;

		this.text = '';
		this.roundNum = 0;
		this.lastServerUpdate = null;
		this.lastTimeSinceStrike = null;
		this.disarmed = false;
		this.presses = [];
		this.buttonOrder = null;

		this.oldPresses = null;
		this.oldButtonOrder = null;

		this.cachedText = null;
		this.img = null;
		this.imgReady = true;
	}
	reset(full) {
		this.text = '';
		this.oldPresses = this.presses;
		this.oldButtonOrder = this.buttonOrder;
		if (full) {
			this.presses = [];
			this.text = '';
			this.disarmed = false;
			this.buttonOrder = null;
			this.cachedText = null;
			this.lastServerUpdate = null;
		}
	}
	getFullName() {
		return this.game.getActiveSubmodule(this.name);
	}
	serverUpdate(msg) {
		this.text = msg['text'];
		this.roundNum = msg['roundNum'];
		this.lastServerUpdate = performance.now();
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		this.buttonOrder = msg['buttonOrder'];
		this.disarmed = msg['disarmed'];
		const prevInputs = msg['prevInputs'];
		this.presses = prevInputs;
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
	doInput(buttonIndex) {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		if (this.disarmed || this.presses.length >= 4) {
			return;
		}
		this.presses.push(buttonIndex);
		this.game.sendModuleInput(
			this.getFullName(),
			{
				'press': buttonIndex
			}
		);
	}
};

export { KtaneWhosOnFirst };
