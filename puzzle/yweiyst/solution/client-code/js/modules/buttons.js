import { KtaneSync } from './sync.js';

class KtaneButtons {
	constructor(game) {
		this.name = 'buttons';
		this.game = game;

		this.lastServerUpdate = null;
		this.lastTimeSinceStrike = null;
		this.disarmed = false;
		this.buttonTexts = [];
		this.depressed = [];
		this.heldDown = null;

		// for rotation rendering
		this.oldButtonTexts = [];
		this.oldDepressed = [];
	}
	reset(full) {
		this.heldDown = null;
		this.oldButtonTexts = this.buttonTexts;
		this.oldDepressed = this.depressed;
		if (full) {
			this.lastServerUpdate = null;
			this.disarmed = false;
			this.buttonTexts = [];
			this.depressed = [];
		}
	}
	serverUpdate(msg) {
		this.lastServerUpdate = performance.now();
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		this.disarmed = msg['disarmed'];
		this.buttonTexts = msg['buttonTexts'];
		this.depressed = msg['depressed'];
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
	getFullName() {
		return this.game.getActiveSubmodule(this.name);
	}
	doInput(index, isDown = true) {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		if (this.disarmed) {
			return;
		}
		const button = this.buttonTexts[index];
		this.game.buttons.heldDown = index;
		this.game.sendModuleInput(
			this.getFullName(),
			{
				'button': button,
				'isDown': isDown,
			}
		);
	}
};

export { KtaneButtons };
