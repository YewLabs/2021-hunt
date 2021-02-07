class Rect {
	constructor(x, y, w, h) {
		this.x = x;
		this.y = y;
		this.w = w;
		this.h = h;
	}
	inBounds(x, y) {
		return x > this.x && x < this.x + this.w && y > this.y && y < this.y + this.h;
	}
};
Rect.ZERO = new Rect(0, 0, 0, 0);

class Vector3 {
	constructor(x, y, z) {
		this.x = x;
		this.y = y;
		this.z = z;
	}
	dot(vec) {
		return this.x * vec.x + this.y * vec.y + this.z * vec.z;
	}
	static fromDict(d) {
		return new Vector3(
			d['x'], d['y'], d['z']
		);
	}
	toDict() {
		return {
			'x': this.x,
			'y': this.y,
			'z': this.z,
		}
	}
	equals(vec) {
		return this.x == vec.x && this.y == vec.y && this.z == vec.z;
	}
};

class CardinalDirection {
	static toAngle(d) {
		switch (d) {
		case CardinalDirection.N: return 0;
		case CardinalDirection.E: return Math.PI/2;
		case CardinalDirection.S: return Math.PI;
		case CardinalDirection.W: return 3*Math.PI/2;
		default:
			console.error('invalid CardinalDirection');
			return null;
		}
	}
	static isHorizontal(d) {
		return d == CardinalDirection.W || d == CardinalDirection.E;
	}
	static getOpposite(d) {
		switch (d) {
		case CardinalDirection.N: return CardinalDirection.S;
		case CardinalDirection.E: return CardinalDirection.W;
		case CardinalDirection.S: return CardinalDirection.N;
		case CardinalDirection.W: return CardinalDirection.E;
		default:
			console.error('invalid CardinalDirection');
			return null;
		}
	}
};

CardinalDirection.N = 0;
CardinalDirection.E = 1;
CardinalDirection.S = 2;
CardinalDirection.W = 3;
CardinalDirection.NUM = 4;

CardinalDirection.CLOCKWISE_FROM_N = [
	CardinalDirection.N,
	CardinalDirection.E,
	CardinalDirection.S,
	CardinalDirection.W,
];

class Matrix3x3 {
	constructor(x, y, z) {
		this.x = x;
		this.y = y;
		this.z = z;
	}
	multVec(vec) {
		return new Vector3(
			this.x.dot(vec),
			this.y.dot(vec),
			this.z.dot(vec),
		);
	}
	getTranspose() {
		return new Matrix3x3(
			new Vector3(this.x.x, this.y.x, this.z.x),
			new Vector3(this.x.y, this.y.y, this.z.y),
			new Vector3(this.x.z, this.y.z, this.z.z)
		);
	}
	leftMult(mat) {
		const t = this.getTranspose();
		return new Matrix3x3(
			t.multVec(mat.x),
			t.multVec(mat.y),
			t.multVec(mat.z),
		);
	}
	// axis must be a unit vector, matrix must be ortho aa
	// rotation follows right-hand rule
	static makeRotate90DegOrthoAA(axis) {
		return new Matrix3x3(
			new Vector3(Math.abs(axis.x), -axis.z, axis.y),
			new Vector3(axis.z, Math.abs(axis.y), -axis.x),
			new Vector3(-axis.y, axis.x, Math.abs(axis.z))
		);
	}
	static fromDict(d) {
		return new Matrix3x3(
			Vector3.fromDict(d['x']),
			Vector3.fromDict(d['y']),
			Vector3.fromDict(d['z'])
		);
	}
	toDict() {
		return {
			'x': this.x.toDict(),
			'y': this.y.toDict(),
			'z': this.z.toDict(),
		}
	}
	equals(m) {
		return (
			this.x.equals(m.x) &&
			this.y.equals(m.y) &&
			this.z.equals(m.z)
		);
	}
};
Matrix3x3.IDENTITY = new Matrix3x3(
	new Vector3(1, 0, 0),
	new Vector3(0, 1, 0),
	new Vector3(0, 0, 1)
);

class CubeFace {
	static toVec(face) {
		switch (face) {
			case CubeFace.FRONT:
				return new Vector3(0, 0, 1);
			case CubeFace.BACK:
				return new Vector3(0, 0, -1);
			case CubeFace.LEFT:
				return new Vector3(-1, 0, 0);
			case CubeFace.RIGHT:
				return new Vector3(1, 0, 0);
			case CubeFace.TOP:
				return new Vector3(0, 1, 0);
			case CubeFace.BOTTOM:
				return new Vector3(0, -1, 0)
		}
		console.error('unknown CubeFace value ' + face.toString())
		return null;
	}
	static fromVec(vec) {
		if (vec.z == 1) return CubeFace.FRONT;
		if (vec.z == -1) return CubeFace.BACK;
		if (vec.x == -1) return CubeFace.LEFT;
		if (vec.x == 1) return CubeFace.RIGHT;
		if (vec.y == 1) return CubeFace.TOP;
		if (vec.y == -1) return CubeFace.BOTTOM;
		console.error('vector doesn\'t represent a CubeFace')
		return null;
	}
	static toRot(face) {
		return Matrix3x3.makeRotate90DegOrthoAA(CubeFace.toVec(face));
	}
};

CubeFace.FRONT = 0;
CubeFace.BACK = 1;
CubeFace.LEFT = 2;
CubeFace.RIGHT = 3;
CubeFace.TOP = 4;
CubeFace.BOTTOM = 5;
CubeFace.NUM = 6;

CubeFace.FRONT_VEC = CubeFace.toVec(CubeFace.FRONT);
CubeFace.BACK_VEC = CubeFace.toVec(CubeFace.BACK);
CubeFace.LEFT_VEC = CubeFace.toVec(CubeFace.LEFT);
CubeFace.RIGHT_VEC = CubeFace.toVec(CubeFace.RIGHT);
CubeFace.TOP_VEC = CubeFace.toVec(CubeFace.TOP);
CubeFace.BOTTOM_VEC = CubeFace.toVec(CubeFace.BOTTOM);

export { Rect, Vector3, Matrix3x3, CardinalDirection, CubeFace };
