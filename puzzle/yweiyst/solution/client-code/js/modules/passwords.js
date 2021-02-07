import { KtaneSync } from './sync.js';

class KtanePasswords {
	constructor(game) {
		this.name = 'passwords';
		this.game = game;

		this.lastServerUpdate = null;
		this.lastTimeSinceStrike = null;
		this.disarmed = false;
		this.letters = null;
		this.selected = null;

		this.oldLetters = null;
		this.oldSelected = null;
	}
	reset(full) {
		this.oldLetters = this.letters;
		this.oldSelected = this.selected;
		if (full) {
			this.lastServerUpdate = null;
			this.disarmed = false;
			this.letters = null;
			this.selected = null;
		}
	}
	serverUpdate(msg) {
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		this.disarmed = msg['disarmed'];
		this.letters = msg['letters'];
		this.selected = msg['selected'];
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
	doInput(isRight) {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		if (this.disarmed) {
			return;
		}
		const selectedR = (this.selected + 1) % this.letters.length;
		const selectedL = (this.selected + this.letters.length - 1) % this.letters.length;
		const newSelected = isRight ? selectedR : selectedL;
		this.selected = newSelected;
		this.game.sendModuleInput(
			this.getFullName(),
			{
				'selection': this.selected,
			}
		);
	}
};

export { KtanePasswords };
