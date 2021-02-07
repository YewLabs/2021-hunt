class KtaneRotationPhase {
};
KtaneRotationPhase.INACTIVE = 0;
KtaneRotationPhase.CLIENT_ROTATE = 1;
KtaneRotationPhase.SERVER_ROTATE = 2;

class KtaneRotationManager {
	constructor() {
		this.phase = KtaneRotationPhase.INACTIVE;
		// If phase is CLIENT_ROTATE,
		// this.q should contain two elements with the first element
		// being the latest server rotation state.
		// If phase is SERVER_ROTATE,
		// last element of this.q should be latest server rotation state.
		this.q = [];
		this.progress = 0;
		this.serverTxn = 0;
	}
	reset() {
		this.phase = KtaneRotationPhase.INACTIVE;
		this.q = [];
		this.progress = 0;
		this.serverTxn = 0;
	}
	isDesynced() {
		return this.phase == KtaneRotationPhase.CLIENT_ROTATE;
	}
	appendRotation(mat) {
		if (this.q[this.q.length-1].equals(mat)) {
			return;
		}
		// if necessary, can break down complex rotations here
		this.q.push(mat);
	}
	doServerRotate(mat, serverTxn) {
		this.serverTxn = serverTxn;
		switch (this.phase) {
		case KtaneRotationPhase.INACTIVE:
			this.q.push(mat);
			this.phase = KtaneRotationPhase.SERVER_ROTATE;
			break;
		case KtaneRotationPhase.SERVER_ROTATE:
			this.appendRotation(mat);
			break;
		case KtaneRotationPhase.CLIENT_ROTATE:
			console.assert(
				this.q.length == 2,
				'should have two elements when phase is CLIENT_ROTATE'
			);
			this.phase = KtaneRotationPhase.SERVER_ROTATE;
			if (this.q[1].equals(mat)) {
				break;
			}
			// undo client rotation
			this.q = [this.q[1], this.q[0]];
			this.appendRotation(mat);
			this.progress = 1 - this.progress;
			break;
		}
	}
	doClientRotate(mat) {
		console.assert(
			this.phase == KtaneRotationPhase.SERVER_ROTATE &&
			this.q.length == 1,
			'client can only rotate when not actively rotating'
		);
		this.phase = KtaneRotationPhase.CLIENT_ROTATE;
		this.q.push(mat);
	}
	getTweenFrom() {
		return this.q[0];
	}
	getTweenTo() {
		return (this.q.length > 1) ? this.q[1] : this.q[0];
	}
	getTweenProgress() {
		return this.progress;
	}
	isRotating() {
		return !(
			this.phase == KtaneRotationPhase.SERVER_ROTATE &&
			this.q.length == 1
		);
	}
	update(elapsed) {
		if (this.q.length <= 1) {
			return;
		}
		const progressInc = elapsed / KtaneRotationManager.ROTATION_SPEED;
		switch (this.phase) {
		case KtaneRotationPhase.SERVER_ROTATE:
			this.progress += progressInc;
			if (this.progress >= 1) {
				this.progress = 0;
				this.q = this.q.slice(1);
			}
			break;
		case KtaneRotationPhase.CLIENT_ROTATE:
			if (this.progress >= 0.5) {
				// don't complete a client rotate without a server ack
				break;
			}
			this.progress += progressInc;
			break;
		}
	}
};
KtaneRotationManager.ROTATION_SPEED = 500; // ms per rotation

export { KtaneRotationManager }
