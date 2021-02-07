import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { QuadrantButton, TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';

const P = KtaneGraphicsParams.SIMON;

class KtaneSimonGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.lightsY = this.rect.h/2 - P.ROUND_NUM_PANEL_H/2;
		this.lights = G.forEachDir(
			this.rect.w/2, this.lightsY,
			P.LIGHTS_OFFSET,
			this.makeLight.bind(this)
		);
	}
	// TODO: generalize quadrant drawing?
	makeLight(x, y, direction) {
		return new QuadrantButton(
			this.canvasCtx, this.game,
			null,
			x, y, P.LIGHTS_RADIUS,
			direction,
			null, null, null
		);
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.simon.getTimeSinceStrike()
		);

		let blinkIndex = null;
		if (this.game.simon.seq != null) {
			const blinkPeriod = P.BLINK_ON_TIME + P.BLINK_OFF_TIME;
			const totBlinkTime = blinkPeriod * this.game.simon.seq.length - P.BLINK_OFF_TIME;
			const period = totBlinkTime + P.BLINK_SPACING;
			const currTime = performance.now() - this.game.simon.lastReset;
			const phase = currTime - (Math.floor(currTime / period)) * period - P.BLINK_SPACING;
			blinkIndex = Math.floor(phase / blinkPeriod);
			const blinkPhase = phase - blinkIndex * blinkPeriod;
			if (blinkIndex < 0 || blinkPhase > P.BLINK_ON_TIME) {
				blinkIndex = null;
			}
		}

		for (let i = 0; i < this.lights.length; i++) {
			this.lights[i].color = (blinkIndex != null && this.game.simon.seq[blinkIndex] == i) ? P.QUADRANT_COLOR_ON : P.QUADRANT_COLOR_OFF;
			this.lights[i].draw(false);
		}

		G.forEachDir(
			this.rect.w/2, this.lightsY, P.LIGHTS_RADIUS*7/12,
			(x, y, direction) => {
				const color = (blinkIndex != null && this.game.simon.seq[blinkIndex] == direction) ? P.TEXT_COLOR_OFF : P.TEXT_COLOR_ON;
				C.drawText(
					this.canvasCtx,
					KtaneGraphicsParams.CARDINAL_DIRECTION_NAMES[direction],
					x, y + 3,
					'center', 'middle', 30,
					KtaneGraphicsParams.UI_FONT, '',
					color
				);
			}
		);

		for (let i = 0; i < P.NUM_ROUNDS; i++) {
			const ledY = this.rect.h - P.ROUND_NUM_PANEL_H/2 - 5;
			const ledX = this.rect.w/2 + (i-1) * (2 * P.ROUND_NUM_RADIUS + P.ROUND_NUM_SPACING);
			const lit = i < this.game.simon.roundNum;
			const ledColor = lit ? P.ROUND_NUM_COLOR_ON : P.ROUND_NUM_COLOR_OFF;
			C.drawCirc(
				this.canvasCtx,
				ledX, ledY, P.ROUND_NUM_RADIUS,
				ledColor,
				null, null,
				[
					["rgba(0, 0, 0, 0.5)", 0, -1, 4],
					["rgba(29, 253, 73, 0.9)", 0, 0, lit ? 10 : 0]
				],
				[["#134413", 0, -1, 5]]
			);
		}

		const disarmed = this.game.simon.disarmed;
		G.drawDisarmedLed(this, disarmed);
		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneSimonGraphics };
