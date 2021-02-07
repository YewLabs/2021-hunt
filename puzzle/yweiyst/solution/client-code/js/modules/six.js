import { KtaneSync } from './sync.js';
import { Rect, CardinalDirection, CubeFace } from '../geom.js';

class KtaneSix {
	constructor(game) {
		this.name = 'six';
		this.game = game;

		this.lit = 0; // bitmask
		this.disarmed = false;
	}
	reset(full) {
		if (full) {
			this.lit = 0;
			this.disarmed = false;
		}
	}
	serverUpdate(msg) {
		this.lit = msg['lit'];
		this.disarmed = this.lit == ((1 << CubeFace.NUM) - 1);
	}
	getLit(index) {
		return ((this.lit >> index) & 1) == 1;
	}
};

export { KtaneSix };

