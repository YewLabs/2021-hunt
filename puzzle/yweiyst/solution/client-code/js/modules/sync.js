class KtaneSync {
	static getTimerVal(syncPoint, checkpoint) {
		if (checkpoint == null) {
			return null;
		}
		const timeSinceUpd = performance.now() - syncPoint;
		return checkpoint + timeSinceUpd;
	}
};

export { KtaneSync };
