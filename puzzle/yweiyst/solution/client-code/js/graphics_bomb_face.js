import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsParams } from './graphics_params.js';
import { KtaneGraphicsControl as G } from './graphics_control.js';
import { KtaneGameGeom } from './game_geom.js';
import { Rect, CardinalDirection, CubeFace } from './geom.js';
import { KtaneEmptyGraphics } from './modules/empty_graphics.js';
import { KtaneTimerGraphics } from './modules/timer_graphics.js';
import { KtaneManualGraphics } from './modules/manual_graphics.js';
import { KtaneManualButtonsGraphics } from './modules/manual_buttons_graphics.js';
import { KtaneShakeItGraphics } from './modules/shake_it_graphics.js';
import { KtaneWhosOnFirstGraphics } from './modules/whos_on_first_graphics.js';
import { KtaneSixGraphics } from './modules/six_graphics.js';
import { KtaneWiresGraphics } from './modules/wires_graphics.js';
import { KtaneMazeGraphics } from './modules/maze_graphics.js';
import { KtaneMazeControlGraphics } from './modules/maze_control_graphics.js';
import { KtaneSimonGraphics } from './modules/simon_graphics.js';
import { KtaneSimonControlGraphics } from './modules/simon_control_graphics.js';
import { KtaneGravityGraphics } from './modules/gravity_graphics.js';
import { KtaneCubeGraphics } from './modules/cube_graphics.js';
import { KtaneButtonsGraphics } from './modules/buttons_graphics.js';
import { KtanePasswordsGraphics } from './modules/passwords_graphics.js';
import { KtaneSerialNumberGraphics } from './modules/serial_graphics.js';
import { KtaneDateOfManufactureGraphics } from './modules/date_graphics.js';
import { KtaneBatteriesGraphics } from './modules/batteries_graphics.js';
import { KtanePortsGraphics } from './modules/ports_graphics.js';

const P = KtaneGraphicsParams.FACE;

class KtaneBombFaceGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		const mainAreaHeight = this.rect.h - P.BOTTOM_ROW_HEIGHT;
		const bigModuleHeight = (mainAreaHeight - P.MODULE_SPACING * 3) / 2;
		const bigModuleWidth = (this.rect.w - P.MODULE_SPACING * 3) / 2;
		const smallModuleHeight = P.BOTTOM_ROW_HEIGHT - P.MODULE_SPACING;
		const smallModuleWidth = (this.rect.w - P.MODULE_SPACING * 4) / 3;
		const manualModuleWidth = this.rect.w - 2 * P.MODULE_SPACING;
		const manualModuleHeight = this.rect.h - P.BOTTOM_ROW_HEIGHT - 2 * P.MODULE_SPACING;
		this.sideModuleRects = [
			new Rect (
				P.MODULE_SPACING,
				P.MODULE_SPACING,
				bigModuleWidth, bigModuleHeight
			),
			new Rect (
				2 * P.MODULE_SPACING + bigModuleWidth,
				P.MODULE_SPACING,
				bigModuleWidth, bigModuleHeight
			),
			new Rect (
				P.MODULE_SPACING,
				2 * P.MODULE_SPACING + bigModuleHeight,
				bigModuleWidth, bigModuleHeight
			),
			new Rect (
				2 * P.MODULE_SPACING + bigModuleWidth,
				2 * P.MODULE_SPACING + bigModuleHeight,
				bigModuleWidth, bigModuleHeight
			),
			new Rect (
				P.MODULE_SPACING,
				mainAreaHeight,
				smallModuleWidth, smallModuleHeight
			),
			new Rect (
				2 * P.MODULE_SPACING + smallModuleWidth,
				mainAreaHeight,
				smallModuleWidth, smallModuleHeight
			),
			new Rect (
				3 * P.MODULE_SPACING + 2 * smallModuleWidth,
				mainAreaHeight,
				smallModuleWidth, smallModuleHeight
			),
		];

		const bigModuleTempRect = new Rect(
			0, 0, bigModuleWidth, bigModuleHeight
		);
		const smallModuleTempRect = new Rect(
			0, 0, smallModuleWidth, smallModuleHeight
		);
		const manualModuleRect = new Rect(
			P.MODULE_SPACING, P.MODULE_SPACING,
			manualModuleWidth,
			manualModuleHeight
		);
		const manualButtonsRect = new Rect(
			P.MODULE_SPACING, this.rect.h - P.BOTTOM_ROW_HEIGHT,
			this.rect.w - 2 * P.MODULE_SPACING,
			P.BOTTOM_ROW_HEIGHT - P.MODULE_SPACING
		);

		this.manualModuleRects = [manualModuleRect];

		this.moduleGraphics = {
			'timer': new KtaneTimerGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'manual-0': new KtaneManualGraphics(
				this.canvasCtx, this.game, manualModuleRect
			),
			'manual-1': new KtaneManualGraphics(
				this.canvasCtx, this.game, manualModuleRect
			),
			'shakeit': new KtaneShakeItGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'whosonfirst0': new KtaneWhosOnFirstGraphics(
				this.canvasCtx, this.game, bigModuleTempRect, this.game.whosOnFirst0
			),
			'whosonfirst1': new KtaneWhosOnFirstGraphics(
				this.canvasCtx, this.game, bigModuleTempRect, this.game.whosOnFirst1
			),
			'six': new KtaneSixGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'wires': new KtaneWiresGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'maze-0': new KtaneMazeControlGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'maze-1': new KtaneMazeGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'simon-0': new KtaneSimonControlGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'simon-1': new KtaneSimonGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'gravity': new KtaneGravityGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'cube': new KtaneCubeGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'serial': new KtaneSerialNumberGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'date': new KtaneDateOfManufactureGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			),
			'empty': new KtaneEmptyGraphics(
				this.canvasCtx, this.game, Rect.ZERO
			),
		};
		for (let i = 0; i < 3; i++ ){
			const fullName = `batteries-${i}`;
			this.moduleGraphics[fullName] = new KtaneBatteriesGraphics(
				this.canvasCtx, this.game, bigModuleTempRect, i
			);
		}
		for (let i = 0; i < 3; i++ ){
			const fullName = `ports-${i}`;
			this.moduleGraphics[fullName] = new KtanePortsGraphics(
				this.canvasCtx, this.game, bigModuleTempRect, i
			);
		}
		for (let i = 0; i < 4; i++ ){
			const fullName = `buttons-${i}`;
			this.moduleGraphics[fullName] = new KtaneButtonsGraphics(
				this.canvasCtx, this.game, bigModuleTempRect
			);
		}
		for (let i = 0; i < 4; i++ ){
			const fullName = `passwords-${i}`;
			this.moduleGraphics[fullName] = new KtanePasswordsGraphics(
				this.canvasCtx, this.game, smallModuleTempRect
			);
		}
		this.manualButtonsGraphics = new KtaneManualButtonsGraphics(
			this.canvasCtx, this.game, manualButtonsRect
		);
	}
	getModuleGraphics(name) {
		if (name in this.moduleGraphics) {
			return this.moduleGraphics[name];
		}
		return this.moduleGraphics['empty']
	}
	getModuleRects(face) {
		switch (face) {
		case CubeFace.FRONT:
		case CubeFace.BACK:
		case CubeFace.LEFT:
		case CubeFace.RIGHT:
			return this.sideModuleRects;
		case CubeFace.TOP:
		case CubeFace.BOTTOM:
			return this.manualModuleRects;
		default:
			console.error('invalid CubeFace');
			break;
		}
	}
	getModuleAt(face, index) {
		const faceModules = this.game.moduleSlots[face];
		if (index >= faceModules.length || faceModules[index] == '') {
			return 'empty';
		}
		return faceModules[index];
	}
	rotateCtx() {
		const playerRot = this.game.getPlayerRot();
		G.rotateAboutCenter(this, CardinalDirection.toAngle(playerRot));
	}
	draw(active) {
		G.begin(this);
		this.rotateCtx();

		C.drawRect(
			this.canvasCtx,
			0, 0, this.rect.w, this.rect.h,
			P.COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			[['rgba(0, 0, 0, 0.9)', 0, -1, 7], ['rgba(0, 0, 0, 0.7)', 0, -1, 10]]
		);
		// C.strokeRect(
		// 	this.canvasCtx,
		// 	0, 0, this.rect.w, this.rect.h,
		// 	P.STROKE, P.STROKE_WIDTH
		// );

		const activeFace = this.game.getActiveFace();
		const moduleRects = this.getModuleRects(activeFace);
		for (let i = 0; i < moduleRects.length; i++) {
			let moduleName = this.getModuleAt(activeFace, i);
			const graphics = this.getModuleGraphics(moduleName);
			graphics.rect = moduleRects[i];
			graphics.draw(active);
		}

		switch (activeFace) {
		case CubeFace.FRONT:
		case CubeFace.BACK:
		case CubeFace.LEFT:
		case CubeFace.RIGHT:
			break;
		case CubeFace.TOP:
		case CubeFace.BOTTOM:
			this.manualButtonsGraphics.draw(active);
			break;
		default:
			console.error('invalid CubeFace');
			break;
		}
		G.end(this);
	}
	updateMouse() {
		let bestClick = null;
		G.begin(this);
		this.rotateCtx();

		const activeFace = this.game.getActiveFace();
		const moduleRects = this.getModuleRects(activeFace);
		for (let i = 0; i < moduleRects.length; i++) {
			let moduleName = this.getModuleAt(activeFace, i);
			const graphics = this.getModuleGraphics(moduleName);
			bestClick = G.updateClick(
				bestClick,
				graphics.updateMouse()
			);
		}

		if (activeFace == CubeFace.TOP || activeFace == CubeFace.BOTTOM) {
			const manualButtonsClick = this.manualButtonsGraphics.updateMouse();
			bestClick = G.updateClick(bestClick, manualButtonsClick);
		}

		G.end(this);
		return bestClick;
	}
};

export { KtaneBombFaceGraphics };
