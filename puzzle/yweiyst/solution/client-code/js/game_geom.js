import { CubeFace, Matrix3x3, CardinalDirection } from './geom.js';

class KtaneGameGeom {
	// get player view relative to the front face
	static getRelativePlayerView(face) {
		let orient = Matrix3x3.IDENTITY;
		switch (face) {
		case CubeFace.FRONT:
			break;
		case CubeFace.BACK:
			orient = orient.leftMult(CubeFace.toRot(CubeFace.TOP));
			orient = orient.leftMult(CubeFace.toRot(CubeFace.TOP));
			break;
		case CubeFace.LEFT:
			orient = orient.leftMult(CubeFace.toRot(CubeFace.BOTTOM));
			break;
		case CubeFace.RIGHT:
			orient = orient.leftMult(CubeFace.toRot(CubeFace.TOP));
			break;
		case CubeFace.TOP:
			orient = orient.leftMult(CubeFace.toRot(CubeFace.LEFT));
			break;
		case CubeFace.BOTTOM:
			orient = orient.leftMult(CubeFace.toRot(CubeFace.RIGHT));
			break;
		default:
			console.error('invalild CubeFace');
			break;
		}
		return orient;
	}
	// returns an orientation that would display the face upright
	// same as relative player view since players should initially
	// see the face in upright orientation
	static getUprightOrientation(face) {
		return KtaneGameGeom.getRelativePlayerView(face);
	}
	static getPlayerViewMatrix(viewMat, playerSlot) {
		const relViewMat = KtaneGameGeom.getRelativePlayerView(playerSlot);
		return relViewMat.leftMult(viewMat);
	}
	static getActiveFace(viewMat, playerSlot) {
		const playerViewMat = KtaneGameGeom.getPlayerViewMatrix(viewMat, playerSlot);
		const activeVec = playerViewMat.multVec(CubeFace.FRONT_VEC);
		const activeFace = CubeFace.fromVec(activeVec);
		return activeFace;
	}
	// returns the direction the player's face is oriented relatve
	// to the default upright orientation
	static getPlayerRot(viewMat, playerSlot) {
		const playerViewMat = KtaneGameGeom.getPlayerViewMatrix(viewMat, playerSlot);
		const activeVec = playerViewMat.multVec(CubeFace.FRONT_VEC);
		const activeFace = CubeFace.fromVec(activeVec);
		let refMat = null;
		for (let i = 0; i < 4; i++) {
			refMat = (i == 0) ?
				KtaneGameGeom.getUprightOrientation(activeFace) :
				refMat.leftMult(CubeFace.toRot(activeFace));
			if (playerViewMat.equals(refMat)) {
				return CardinalDirection.CLOCKWISE_FROM_N[i];
			}
		}
		console.error('could not find orientation');
		return null;
	}
	static getRotFace(oldViewMat, newViewMat) {
		for (let i = 0; i < CubeFace.NUM; i++) {
			const refMat = oldViewMat.leftMult(CubeFace.toRot(i));
			if (refMat.equals(newViewMat)) {
				return i;
			}
		}
		console.error('could not find orientation');
		return null;
	}
	static rotDirToFace(d) {
		switch (d) {
		case CardinalDirection.N: return CubeFace.LEFT;
		case CardinalDirection.E: return CubeFace.TOP;
		case CardinalDirection.S: return CubeFace.RIGHT;
		case CardinalDirection.W: return CubeFace.BOTTOM;
		default:
			console.error('invalid CardinalDirection');
			return null;
		}
	}
	static rotByFace(viewMatrix, rotFace) {
		const rotAxis = CubeFace.toVec(rotFace);
		const rotMat = Matrix3x3.makeRotate90DegOrthoAA(rotAxis);
		const newViewMatrix = viewMatrix.leftMult(rotMat);
		return newViewMatrix;
	}
	static playerDirToRotFace(viewMatrix, playerFace, rotDir) {
		const playerViewMatrix = KtaneGameGeom.getPlayerViewMatrix(
			viewMatrix, playerFace
		);
		const rotFaceRel = KtaneGameGeom.rotDirToFace(rotDir);
		const rotAxisRel = CubeFace.toVec(rotFaceRel);
		const rotAxis = playerViewMatrix.multVec(rotAxisRel);
		const rotFace = CubeFace.fromVec(rotAxis);
		return rotFace;
	}

};

export { KtaneGameGeom };
