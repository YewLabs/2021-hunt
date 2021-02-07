import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

const P = KtaneGraphicsParams.TIMER;

class KtaneTimerGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.timer.getTimeSinceStrike()
		);
		if (this.game.timer.speed != 1) {
			const currTime = performance.now();
			const scaledTime = currTime / P.SPEED_BLINK_PERIOD
			const phase = scaledTime - Math.floor(scaledTime);
			const t = (phase < 0.5) ? (2*phase) : (1 - 2*(phase - 0.5));
			C.fillRect(
				this.canvasCtx,
				0, 0, this.rect.w, this.rect.h,
				C.interpolateRgba(200, 0, 0, 0, 200, 0, 0, 0.8, t)
			);
		}

		const panelW = this.rect.w * P.PANEL_WIDTH_RATIO;
		const panelH = this.rect.h * P.PANEL_HEIGHT_RATIO;
		C.drawRect(
			this.canvasCtx,
			this.rect.w/2 - panelW/2,
			this.rect.h/2 - panelH/2 - P.OFFSET_Y,
			panelW, panelH,
			KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			KtaneGraphicsParams.SCREEN_INSET_SHADOW
		);

		const timeLeft = parseInt(Math.floor(this.game.timer.getTimeLeft() / 1000));
		const minutesLeft = Math.floor(timeLeft / 60);
		const secondsLeft = timeLeft % 60;
		const minutesStr = (minutesLeft.toString()).padStart(2, '0');
		const secondsStr = (secondsLeft.toString()).padStart(2, '0');
		const counterVal = `${minutesStr}:${secondsStr}`;
		C.drawText(
			this.canvasCtx, 
			counterVal,
			this.rect.w/2,
			this.rect.h/2 - P.OFFSET_Y,
			'center', 'middle', 60,
			KtaneGraphicsParams.TIMER_FONT, '', P.TEXT_COLOR,
			'red', 10
		);

		const ledPanelH = this.rect.h/2 - panelH/2;
		const ledY = this.rect.h - ledPanelH/2;
		for (let i = 0; i < P.MAX_STRIKES; i++) {
			const lit = i < this.game.timer.numStrikes;
			const color = lit ? P.STRIKE_COLOR_ON : P.STRIKE_COLOR_OFF;
			C.drawCirc(
				this.canvasCtx,
				this.rect.w/2 + (i-1) * (2*P.STRIKE_RADIUS + P.STRIKE_SPACING),
				ledY - P.OFFSET_Y,
				P.STRIKE_RADIUS,
				color,
				null, null,
				[
					["rgba(0, 0, 0, 0.5)", 0, -1, 4],
					["rgba(255, 0, 0, 0.9)", 0, 0, lit ? 13 : 0]
				],
				[["#441313", 0, -1, 9]]
			);
		}

		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneTimerGraphics };
