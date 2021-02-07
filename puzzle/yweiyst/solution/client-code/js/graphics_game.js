import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsParams } from './graphics_params.js';
import { KtaneGraphicsControl as G } from './graphics_control.js';
import { CubeFace, Rect } from './geom.js';
import { TextButton } from './graphics_components.js';
import { KtaneClick } from './input.js';
import { KtaneCubeControlGraphics } from './graphics_cube.js';

const P = KtaneGraphicsParams.GAME;

class KtaneGameGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.sidePanelWidth = (this.rect.w - this.rect.h)/2;
		this.cubeGraphics = new KtaneCubeControlGraphics(
			canvasCtx, game, new Rect(
				this.sidePanelWidth,
				0,
				this.rect.w - 2 * this.sidePanelWidth,
				this.rect.h
			)
		);

		this.stopGameButton = new TextButton(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.STOP_BUTTON),
			10, this.rect.h - 25 - 10, 100, 25,
			'STOP GAME',
			KtaneGraphicsParams.DULL_BUTTON_COLOR,
			KtaneGraphicsParams.DULL_BUTTON_PRESSED_COLOR,
			KtaneGraphicsParams.DULL_BUTTON_HOVER_COLOR
		);
		this.clickables = [];
	}
	drawSideText(text, y, textSize, bold=false, color='#FFFFFF') {
		C.drawText(
			this.canvasCtx,
			text,
			this.rect.w - this.sidePanelWidth/2,
			120 + y,
			'center', 'middle', textSize,
			KtaneGraphicsParams.UI_FONT, bold ? 'bold' : '',
			color
		);
	}
	getClickables() {
		this.clickables = [];
		if (this.game.debugMode) {
			this.clickables.push(this.stopGameButton);
		}
	}
	draw(active) {
		G.begin(this);
		const defusingStr = this.game.isDefuser ? 'REPAIRING' : 'SPECTATING';
		const viewStr = KtaneGraphicsParams.ROOM_DIRECTION_NAMES[this.game.playerSlot];
		const cubeStr = {
			[CubeFace.TOP]: 'TOP',
			[CubeFace.BOTTOM]: 'BOTTOM',
			[CubeFace.LEFT]: 'LEFT',
			[CubeFace.RIGHT]: 'RIGHT',
			[CubeFace.FRONT]: 'FRONT',
			[CubeFace.BACK]: 'BACK',
		}[this.game.getActiveFace()];
		this.drawSideText(
			'YOU ARE', 50, 20
		);
		this.drawSideText(
			defusingStr, 90, 30, true
		);
		this.drawSideText(
			'FROM THE', 130, 20
		);
		this.drawSideText(
			viewStr, 170, 30, true
		);
		this.drawSideText(
			'VIEWING THE', 210, 20
		);
		this.drawSideText(
			cubeStr, 250, 30, true
		);
		this.drawSideText(
			'FACE OF THE', 290, 20
		);
		this.drawSideText(
			'CONSOLE', 320, 20
		);

		if (!this.game.isDefuser && !this.game.spectatorMode) {
			const mutedColor = '#BBBBBB';
			this.drawSideText(
				'You may take over', 420, 14, false, mutedColor
			);
			this.drawSideText(
				'when a defuser', 440, 14, false, mutedColor
			);
			this.drawSideText(
				'disconnects.', 460, 14, false, mutedColor
			);
		}

		this.getClickables();
		G.drawClickables(this, active);
		this.cubeGraphics.draw(active);
		G.end(this);
	}
	updateMouse() {
		let bestClick = null;
		G.begin(this);

		this.getClickables();
		bestClick = G.updateClick(
			bestClick,
			G.updateMouseClickables(this)
		);
		const cubeClickData = this.cubeGraphics.updateMouse();
		bestClick = G.updateClick(bestClick, cubeClickData);

		G.end(this);
		return bestClick;
	}
};

export { KtaneGameGraphics };
