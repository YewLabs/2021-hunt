import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';
import { Rect, CardinalDirection, CubeFace } from '../geom.js';

const P = KtaneGraphicsParams.SIX;

class KtaneSixGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, null
		);

		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		const ledR = (this.rect.w - 4 * spacing) / 6;
		const offsetY = P.LED_SPACING/2 + P.LED_RADIUS;
		for (let i = 0; i < CubeFace.NUM; i++) {
			const ledXI = i % 3, ledYI = Math.floor(i / 3);
			C.drawCirc(
				this.canvasCtx,
				this.rect.w/2 + (ledXI - 1) * (2 * P.LED_RADIUS + P.LED_SPACING),
				this.rect.h/2 + (ledYI * 2 - 1) * offsetY,
				P.LED_RADIUS,
				this.game.six.getLit(i) ? P.LED_COLOR_ON : P.LED_COLOR_OFF,
				null, null,
				[
					["rgba(0, 0, 0, 0.5)", 0, -1, 4],
					["rgba(255, 0, 0, 0.9)", 0, 0, this.game.six.getLit(i) ? 13 : 0]
				],
				[["#441313", 0, -1, 9]]
			);
		}
		const disarmed = this.game.six.disarmed;
		G.drawDisarmedLed(this, disarmed);
		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneSixGraphics };

