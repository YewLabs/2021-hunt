import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsParams } from './graphics_params.js';
import { KtaneGraphicsControl as G } from './graphics_control.js';
import { Rect, CardinalDirection, CubeFace } from './geom.js';
import { TextButton, TriangleButton } from './graphics_components.js';
import { KtaneClick } from './input.js';
import { KtaneGameGeom } from './game_geom.js';
import { KtaneBombFaceGraphics } from './graphics_bomb_face.js';
import { WebglUtils } from './webgl/graphics_webgl.js';
import { RotatingCubeGraphics } from './webgl/rotating_cube.js';

const P = KtaneGraphicsParams.CUBE_CONTROL;

const FACE_MARGIN = P.ROTATE_BUTTON_HEIGHT + 2 * P.ROTATE_BUTTON_MARGIN;

class KtaneCubeControlGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.faceGraphics = this.makeFaceGraphics(this.canvasCtx);

		const rotateButtonOffset = P.ROTATE_BUTTON_MARGIN + P.ROTATE_BUTTON_HEIGHT;
		this.rotateButtons = G.forEachDir(
			this.rect.w/2, this.rect.h/2, this.rect.w/2 - rotateButtonOffset,
			this.makeRotateButton.bind(this)
		);
		this.clickables = this.rotateButtons;

		// for 3d rendering
		const scratchOldCanvas = document.getElementById('scratchOld');
		const scratchNewCanvas = document.getElementById('scratchNew');
		const scratch3dCanvas = document.getElementById('scratch3d');
		const pow2w = WebglUtils.getNearestPowerOfTwo(this.faceGraphics.rect.w);
		const pow2h = WebglUtils.getNearestPowerOfTwo(this.faceGraphics.rect.h);
		scratchOldCanvas.width = pow2w;
		scratchOldCanvas.height = pow2h;
		scratchNewCanvas.width = pow2w;
		scratchNewCanvas.height = pow2h;
		scratch3dCanvas.width = this.rect.w;
		scratch3dCanvas.height = this.rect.h;
		const scratchOldCtx = scratchOldCanvas.getContext('2d');
		const scratchNewCtx = scratchNewCanvas.getContext('2d');
		this.scratch3dCtx = WebglUtils.getContext(scratch3dCanvas);
		if (this.scratch3dCtx == null) {
			this.game.updateWebglEnabled(false);
		}
		this.rotatingOldFaceGraphics = this.makeFaceGraphics(scratchOldCtx);
		this.rotatingNewFaceGraphics = this.makeFaceGraphics(scratchNewCtx);
		this.rotatingOldFaceGraphics.rect.x = 0;
		this.rotatingOldFaceGraphics.rect.y = 0;
		this.rotatingNewFaceGraphics.rect.x = 0;
		this.rotatingNewFaceGraphics.rect.y = 0;

		this.rotatingCubeGraphics = new RotatingCubeGraphics(
			this.scratch3dCtx,
			this.rect.w / this.rotatingNewFaceGraphics.rect.w
		);
	}
	initRotatingCube() {
		this.rotatingCubeGraphics.init(
			this.rotatingOldFaceGraphics
		);
	}
	makeFaceGraphics(canvasCtx) {
		return new KtaneBombFaceGraphics(
			canvasCtx, this.game,
			new Rect(
				FACE_MARGIN, FACE_MARGIN,
				this.rect.w - 2 * FACE_MARGIN,
				this.rect.h - 2 * FACE_MARGIN
			)
		);
	}
	makeRotateButton(x, y, orientation) {
		return new TriangleButton(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.ROTATE_BUTTON, orientation),
			x, y, P.ROTATE_BUTTON_WIDTH, P.ROTATE_BUTTON_HEIGHT,
			orientation,
			KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
			KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
			KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR
		);
	}
	drawRotating() {
		C.drawText(
			this.canvasCtx, 
			'Rotating...',
			this.rect.w / 2,
			this.rect.h / 2,
			'center', 'middle', 20,
			KtaneGraphicsParams.UI_FONT, '',
			'#FFFFFF'
		);
	}
	drawRotatingFace(faceGraphics, xrot, yrot, zrot) {
		this.rotatingCubeGraphics.drawFace(
			faceGraphics.canvasCtx.canvas, xrot, yrot, zrot
		);
	}
	drawRotatingCube(rotFace) {
		this.game.useOldOrientation = true;
		this.rotatingOldFaceGraphics.draw(false);
		this.game.useOldOrientation = false;
		this.rotatingNewFaceGraphics.draw(false);
		this.game.useOldOrientation = false;

		this.initRotatingCube();
		this.rotatingCubeGraphics.start();

		const progress = this.game.rotManager.progress;
		if (rotFace == CubeFace.FRONT) {
			this.drawRotatingFace(this.rotatingOldFaceGraphics, 0, 0, -progress);
		}
		else if (rotFace == CubeFace.BACK) {
			this.drawRotatingFace(this.rotatingOldFaceGraphics, 0, 0, progress);
		}
		else {
			// rotation angles from/to
			let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
			switch (rotFace) {
			case CubeFace.LEFT:
				x1 = progress;
				x2 = progress - 1;
				break;
			case CubeFace.RIGHT:
				x1 = -progress;
				x2 = 1 - progress;
				break;
			case CubeFace.TOP:
				y1 = -progress;
				y2 = 1 - progress;
				break;
			case CubeFace.BOTTOM:
				y1 = progress;
				y2 = progress - 1;
				break;
			}
			if (progress < 0.5) {
				this.drawRotatingFace(this.rotatingNewFaceGraphics, x2, y2, 0);
				this.drawRotatingFace(this.rotatingOldFaceGraphics, x1, y1, 0);
			}
			else {
				this.drawRotatingFace(this.rotatingOldFaceGraphics, x1, y1, 0);
				this.drawRotatingFace(this.rotatingNewFaceGraphics, x2, y2, 0);
			}
		}
	}
	draw(active) {
		G.begin(this);
		const isRotating = this.game.rotManager.isRotating();
		if (isRotating) {
			const tweenFrom = this.game.rotManager.getTweenFrom();
			const tweenTo = this.game.rotManager.getTweenTo();
			if (tweenFrom.equals(tweenTo)) {
				console.error('rotation manager should guarantee distinct tween endpoints');
			}
			const rotFaceAbs = KtaneGameGeom.getRotFace(tweenFrom, tweenTo);
			if (!this.game.webglEnabled || rotFaceAbs == null) {
				this.drawRotating();
			}
			else {
				const rotVecAbs = CubeFace.toVec(rotFaceAbs);
				const rotVecRelFront = tweenFrom.getTranspose().multVec(rotVecAbs);
				const relView = KtaneGameGeom.getRelativePlayerView(this.game.playerSlot);
				const rotVecRel = relView.getTranspose().multVec(rotVecRelFront);
				const rotFaceRel = CubeFace.fromVec(rotVecRel);
				this.drawRotatingCube(rotFaceRel);
				this.canvasCtx.drawImage(this.scratch3dCtx.canvas, 0, 0)
			}
		}
		else {
			this.faceGraphics.draw(active && this.game.isDefuser);
		}
		G.drawClickables(this, active);
		G.end(this);
	}
	updateMouse() {
		let bestClick = null;
		G.begin(this);

		bestClick = G.updateClick(
			bestClick,
			G.updateMouseClickables(this)
		);
		if (!this.game.rotManager.isRotating() && this.game.isDefuser) {
			const faceClickData = this.faceGraphics.updateMouse();
			bestClick = G.updateClick(bestClick, faceClickData);
		}

		G.end(this);
		return bestClick;
	}
};

export { KtaneCubeControlGraphics };
