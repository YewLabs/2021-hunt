import { KtaneSync } from './sync.js';

class KtaneSerialNumber {
	constructor(game) {
		this.name = 'serial';
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

class KtaneDateOfManufacture {
	constructor(game) {
		this.name = 'date';
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

class KtaneBatteries {
	constructor(game) {
		this.name = 'date';
		this.game = game;
		this.numPerFace = {};
	}
	reset(full) {
		if (full) {
			this.numPerFace = 0
		}
	}
	serverUpdate(msg) {
		this.numPerFace = msg['numPerFace'];
	}
};

class KtanePorts {
	constructor(game) {
		this.name = 'date';
		this.game = game;
		this.numPerFace = 0;
	}
	reset(full) {
		if (full) {
			this.numPerFace = 0
		}
	}
	serverUpdate(msg) {
		this.numPerFace = msg['numPerFace'];
	}
};

export { KtaneSerialNumber, KtaneDateOfManufacture, KtaneBatteries, KtanePorts };
