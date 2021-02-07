import { KtaneSync } from './sync.js';

class KtaneGravity {
	constructor(game) {
		this.name = 'gravity';
		this.game = game;
		this.text = '';
	}
	reset(full) {
		if (full) {
			this.text = '';
		}
	}
	serverUpdate(msg) {
		this.text = msg['text'];
	}
};

export { KtaneGravity };

