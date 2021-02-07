import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsParams } from './graphics_params.js';
import { KtaneGraphicsControl as G } from './graphics_control.js';
import { Rect, CubeFace } from './geom.js';
import { KtaneClick } from './input.js';
import { TextButton } from './graphics_components.js';
import { manualData } from "./modules/manual/data.js";

class KtaneLobbyGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.startButton = new TextButton(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.START_BUTTON),
			this.rect.w - 155, 380, 115, 30,
			'START',
			KtaneGraphicsParams.SUCCESS_BUTTON_COLOR,
			KtaneGraphicsParams.SUCCESS_BUTTON_PRESSED_COLOR,
			KtaneGraphicsParams.SUCCESS_BUTTON_HOVER_COLOR
		);
		this.clickables = [];
	}
	drawPlayers() {
		const PADDING_Y = 210;
		const FACE_NAMES_PADDING_X = 8;
		const ICON_PADDING = 3;
		const ICON_WIDTH = 15;
		const ICON_WIDTH_WITH_PADDING =
			ICON_WIDTH + 2 * ICON_PADDING;
		const FACE_NAMES_ALIGN_X = this.rect.w - 70;
		const SPEED_BLINK_PERIOD = 1000; // ms

		C.strokeRect(
			this.canvasCtx,
			FACE_NAMES_ALIGN_X,
			PADDING_Y,
			ICON_WIDTH_WITH_PADDING,
			CubeFace.NUM * ICON_WIDTH_WITH_PADDING,
			'#ffffff', 1.5
		);

		const order = [1, 0, 3, 2, 4, 5];

		for (let i = 0; i < CubeFace.NUM; i++) {
			const stripY = PADDING_Y + order[i] * ICON_WIDTH_WITH_PADDING;
			const currTime = performance.now() - 100*order[i];
			const scaledTime = currTime / SPEED_BLINK_PERIOD;
			const phase = scaledTime - Math.floor(scaledTime);
			const t = Math.min(1, 50*(phase - 0.5)**2);

			const faceName = KtaneGraphicsParams.ROOM_DIRECTION_NAMES[i];
			C.drawText(
				this.canvasCtx,
				faceName,
				FACE_NAMES_ALIGN_X - FACE_NAMES_PADDING_X,
				stripY + 4,
				'right', 'top',
				14, KtaneGraphicsParams.UI_FONT, '', '#ffffff'
			);

			const hasDefuser = ((this.game.playerSlotFilled >> i) & 1) == 1
			const isInSlot =
				this.game.playerSlot != null &&
				this.game.playerSlot == i;
			const isDefuser = this.game.isDefuser;

			if (hasDefuser) {
				const cellX = FACE_NAMES_ALIGN_X;
				const highlight = isInSlot && isDefuser;

				this.canvasCtx.fillStyle = highlight ? (
					C.interpolateRgba(0, 255, 0, 0, 0, 255, 0, 0.8, t)
				) : (
					C.interpolateRgba(255, 255, 255, 0, 255, 255, 255, 0.8, t)
				);

				this.canvasCtx.fillRect(
					cellX + ICON_PADDING,
					stripY + ICON_PADDING,
					ICON_WIDTH,
					ICON_WIDTH
				);
			}
		}

		C.drawText(
			this.canvasCtx,
			'SPECTATING',
			FACE_NAMES_ALIGN_X - FACE_NAMES_PADDING_X,
			PADDING_Y + 13 * ICON_WIDTH_WITH_PADDING / 2,
			'right', 'top',
			14, KtaneGraphicsParams.UI_FONT, '', '#ffffff'
		);

		C.drawText(
			this.canvasCtx,
			`${this.game.numSpectators}`,
			FACE_NAMES_ALIGN_X + ICON_WIDTH_WITH_PADDING / 2,
			PADDING_Y + 13 * ICON_WIDTH_WITH_PADDING / 2,
			'center', 'top',
			14, KtaneGraphicsParams.UI_FONT, '', '#ffffff'
		);
	}
	drawInstructions() {
		const X_OFFSET = this.rect.w / 2;
		const TITLE_Y = 135;
		const TITLE_HEIGHT = 50;
		const TITLE_SIZE = 40;
		const TEXT_Y = TITLE_Y + 120;
		const TEXT_HEIGHT = 23;
		const TEXT_SIZE = 18;
		const TEXT_X = X_OFFSET - 190;

		C.strokeLine(
			this.canvasCtx,
			X_OFFSET - 200, TITLE_Y - 40,
			X_OFFSET + 200, TITLE_Y - 40,
			'#ffffff', 2
		);
		C.strokeLine(
			this.canvasCtx,
			X_OFFSET - 200, TITLE_Y + 80,
			X_OFFSET + 200, TITLE_Y + 80,
			'#ffffff', 2
		);
		['YOU WILL EXPLODE', 'IF YOU STOP TALKING'].forEach((line, i) =>
			C.drawText(
				this.canvasCtx, line,
				X_OFFSET,
				TITLE_Y + TITLE_HEIGHT * i,
				'center', 'middle',
				TITLE_SIZE, KtaneGraphicsParams.MANUAL_FONT,
				'', '#ffffff'
			)
		);
		manualData.intro_text.forEach((line, i) =>
		 	C.drawText(
				this.canvasCtx, line,
				TEXT_X, TEXT_Y + TEXT_HEIGHT * i,
				'start', 'middle',
				TEXT_SIZE, KtaneGraphicsParams.UI_FONT,
				'', '#ffffff'
			)
		);
	}
	enoughPlayers() {
		let numPlayers = 0;
		for (let i = 0; i < CubeFace.NUM; i++) {
			if (((this.game.playerSlotFilled >> i) & 1) == 1) {
				numPlayers += 1;
				if (numPlayers >= 4) {
					return true;
				}
			}
		}
		return false;
	}
	getClickables() {
		this.clickables = [];
		if (this.game.debugMode || this.enoughPlayers()) {
			this.clickables.push(this.startButton);
		}
	}
	draw(active) {
		G.begin(this);
		if (!this.game.isReadyToStart()) {
			// still waiting for reply from server
			C.drawText(
				this.canvasCtx,
				'Connecting...',
				this.rect.w / 2,
				this.rect.h / 2,
				'center', 'middle', 20,
				KtaneGraphicsParams.UI_FONT, '',
				'#FFFFFF'
			);
			return;
		}
		this.drawPlayers();

		if (!this.enoughPlayers()) {
			C.drawText(
				this.canvasCtx,
				'Waiting for technicians...',
				this.rect.w - 155 + 115/2, 400,
				'center', 'middle', 14,
				KtaneGraphicsParams.UI_FONT, '',
				'#DDDDDD'
			);
		}

		this.getClickables();
		G.drawClickables(this, active);
		this.drawInstructions();

		G.end(this);
	}
	updateMouse() {
		if (!this.game.isReadyToStart()) {
			// still waiting for reply from server
			return;
		}
		let bestClick = null;
		G.begin(this);

		this.getClickables();
		bestClick = G.updateClick(
			bestClick,
			G.updateMouseClickables(this)
		);

		G.end(this);
		return bestClick;
	}
}

export { KtaneLobbyGraphics };
