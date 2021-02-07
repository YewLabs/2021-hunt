class Vector4 {
	constructor(x, y, z, w) {
		this.x = x;
		this.y = y;
		this.z = z;
		this.w = w;
	}
	dot(vec) {
		return this.x * vec.x + this.y * vec.y + this.z * vec.z + this.w * vec.w;
	}
	toArray() {
		return [this.x, this.y, this.z, this.w];
	}
};

class Matrix4x4 {
	constructor(x, y, z, w) {
		this.x = x;
		this.y = y;
		this.z = z;
		this.w = w;
	}
	multVec(vec) {
		return new Vector4(
			this.x.dot(vec),
			this.y.dot(vec),
			this.z.dot(vec),
			this.w.dot(vec),
		);
	}
	getTranspose() {
		return new Matrix4x4(
			new Vector4(this.x.x, this.y.x, this.z.x, this.w.x),
			new Vector4(this.x.y, this.y.y, this.z.y, this.w.y),
			new Vector4(this.x.z, this.y.z, this.z.z, this.w.z),
			new Vector4(this.x.w, this.y.w, this.z.w, this.w.w)
		);
	}
	leftMult(mat) {
		const t = this.getTranspose();
		return new Matrix4x4(
			t.multVec(mat.x),
			t.multVec(mat.y),
			t.multVec(mat.z),
			t.multVec(mat.w),
		);
	}
	toArray() {
		return [
			...this.x.toArray(),
			...this.y.toArray(),
			...this.z.toArray(),
			...this.w.toArray(),
		];
	}
	// f is how far the back of the frustrum extends
	// s is the lateral size of the frustrum
	static perspective(n, f, s) {
		return new Matrix4x4(
			new Vector4(n/s, 0, 0, 0),
			new Vector4(0, n/s, 0, 0),
			new Vector4(0, 0, (n+f) / (n-f), 2*f*n / (n-f)),
			new Vector4(0, 0, -1, 0)
		);
	}
	static translateZ(z) {
		return new Matrix4x4(
			new Vector4(1, 0, 0, 0),
			new Vector4(0, 1, 0, 0),
			new Vector4(0, 0, 1, z),
			new Vector4(0, 0, 0, 1)
		);
	}
	static rotateX(t) {
		return new Matrix4x4(
			new Vector4(1, 0, 0, 0),
			new Vector4(0, Math.cos(t), -Math.sin(t), 0),
			new Vector4(0, Math.sin(t), Math.cos(t), 0),
			new Vector4(0, 0, 0, 1)
		);
	}
	static rotateY(t) {
		return new Matrix4x4(
			new Vector4(Math.cos(t), 0, Math.sin(t), 0),
			new Vector4(0, 1, 0, 0),
			new Vector4(-Math.sin(t), 0, Math.cos(t), 0),
			new Vector4(0, 0, 0, 1)
		);
	}
	static rotateZ(t) {
		return new Matrix4x4(
			new Vector4(Math.cos(t), -Math.sin(t), 0, 0),
			new Vector4(Math.sin(t), Math.cos(t), 0, 0),
			new Vector4(0, 0, 1, 0),
			new Vector4(0, 0, 0, 1)
		);
	}
	static removeZ() {
		return new Matrix4x4(
			new Vector4(1, 0, 0, 0),
			new Vector4(0, 1, 0, 0),
			new Vector4(0, 0, 0, 0),
			new Vector4(0, 0, 0, 1)
		);
	}
	static from3x3(mat) {
		return new Matrix4x4(
			new Vector4(mat.x.x, mat.x.y, mat.x.z, 0),
			new Vector4(mat.y.x, mat.y.y, mat.y.z, 0),
			new Vector4(mat.z.x, mat.z.y, mat.z.z, 0),
			new Vector4(0, 0, 0, 1)
		);
	}
};
Matrix4x4.IDENTITY = new Matrix4x4(
	new Vector4(1, 0, 0, 0),
	new Vector4(0, 1, 0, 0),
	new Vector4(0, 0, 1, 0),
	new Vector4(0, 0, 0, 1)
);

export { Vector4, Matrix4x4 };
