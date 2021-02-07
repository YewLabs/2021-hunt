import { KtaneSync } from './sync.js';

const NUM_WIRES = 5;

class KtaneWires {
	constructor(game) {
		this.name = 'wires';
		this.game = game;

		this.colors = [];
		this.striped = 0; // bitmask
		this.lastServerUpdate = null;
		this.lastTimeSinceStrike = null;
		this.cuts = 0; // bitmask
		this.disarmed = false;
	}
	reset(full) {
		if (full) {
			this.colors = [];
			this.striped = 0;
			this.disarmed = false;
			this.cuts = 0;
		}
	}
	serverUpdate(msg) {
		this.lastServerUpdate = performance.now();
		this.lastTimeSinceStrike = msg['timeSinceStrike'];
		this.colors = msg['colors'];
		this.striped = msg['striped'];
		this.cuts = msg['cuts'];
		this.disarmed = this.cuts == ((1 << NUM_WIRES) - 1);
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
	getCut(index) {
		return ((this.cuts >> index) & 1) == 1;
	}
	setCut(index) {
		this.cuts |= (1 << index);
	}
	getStriped(index) {
		return ((this.striped >> index) & 1) == 1;
	}
	doInput(wireIndex) {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		if (this.disarmed || this.getCut(wireIndex)) {
			return;
		}
		this.setCut(wireIndex);
		this.game.sendModuleInput(
			this.name,
			{
				'cut': wireIndex
			}
		);
	}
};

export { KtaneWires };
