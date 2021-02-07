import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsParams } from './graphics_params.js';
import { KtaneGraphicsControl as G } from './graphics_control.js';
import { Rect, CubeFace } from './geom.js';
import { KtaneClick } from './input.js';
import { TextButton } from './graphics_components.js';

const P = KtaneGraphicsParams.STOPPED;
const MODULE_NICE_NAMES = {
	'shakeit': 'Shake It',
	'whosonfirst0': 'Talk',
	'whosonfirst1': 'Talk',
	'six': 'Six Lights',
	'wires': 'Wires',
	'maze': 'Maze',
	'simon': 'Flashing Lights',
	'gravity': 'Gravity Sensor',
	'cube': 'Cube',
	'buttons': 'Buttons',
	'passwords': 'Passwords',
};

class KtaneStoppedGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.restartButtonY = this.rect.h - P.RESTART_BUTTON_HEIGHT - 10;
		this.clickables = [
			new TextButton(
				this.canvasCtx, this.game,
				new KtaneClick(KtaneClick.RESTART_BUTTON),
				this.rect.w/2 - P.RESTART_BUTTON_WIDTH/2,
				this.restartButtonY,
				P.RESTART_BUTTON_WIDTH, P.RESTART_BUTTON_HEIGHT,
				'BACK TO LOBBY',
				KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
				KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
				KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR,
				30
			),
		];
	}
	drawText(text, y, textSize, bold=false, font=KtaneGraphicsParams.UI_FONT) {
		C.drawText(
			this.canvasCtx,
			text,
			this.rect.w/2,
			y,
			'center', 'middle', textSize,
			font, bold ? 'bold' : '',
			'#fff'
		);
	}
	draw(active) {
		G.begin(this);
		if (this.game.winMessage.length == 0) {
			let stopReason = 'CONNECTION LOST';
			let exploded = false;
			if (this.game.timeLeft != null && this.game.timeLeft < 0) {
				stopReason = 'TIME LIMIT EXCEEDED';
				exploded = true;
			}
			else if (this.game.strikeReasons.length >= 3) {
				stopReason = 'STRIKE LIMIT EXCEEDED';
				exploded = true;
			}
			if (exploded) {
				this.drawText(
					'The console explodes. The broken screen shows the final error message:',
					this.rect.h/2 - 50,
					18
				);
			}
			this.drawText(
				stopReason,
				this.rect.h/2,
				50,
				false, KtaneGraphicsParams.MANUAL_FONT
			);
		}
		else {
			let currY = 200;
			for (const line of this.game.winMessage) {
				C.drawText(
					this.canvasCtx,
					line, this.rect.w / 2 - 170, currY,
					'start', 'middle', 18,
					KtaneGraphicsParams.UI_FONT,
					'', '#ffffff'
				);
				currY += 23;
			}
		}

		if (this.game.strikeReasons.length > 0) {
			let strikeReasonsText = 'Strike reasons: ';
			for (let i = 0; i < this.game.strikeReasons.length; i++) {
				if (i != 0) {
					strikeReasonsText += ', ';
				}
				strikeReasonsText += MODULE_NICE_NAMES[this.game.strikeReasons[i]];
			}
			this.drawText(
				strikeReasonsText,
				this.restartButtonY - 51,
				18
			);
		}
		if (this.game.timeLeft != null && this.game.timeLeft > 0) {
			const timeRemainingText = `Time remaining: ${G.timeDeltaAsString(this.game.timeLeft)}`;
			this.drawText(
				timeRemainingText,
				this.restartButtonY - 28,
				18
			);
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

		G.end(this);
		return bestClick;
	}
}

export { KtaneStoppedGraphics };
