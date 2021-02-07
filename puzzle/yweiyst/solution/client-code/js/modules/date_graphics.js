import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

class KtaneDateOfManufactureGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
	}
	draw(active) {
		G.begin(this);
		// G.drawBackgroundWithStrike(
		// 	this, null
		// );

		const x = 0;
		const y = 0;
		const width = this.rect.w - 2*x;
		const height = this.rect.h - 2*y;

		C.drawRect(
			this.canvasCtx,
			x, y, width, height,
			'#f0f0f2',
			null, null,
			[['rgba(0, 0, 0, 0.4)', 0, 1, 4]]
		);

		C.drawText(
			this.canvasCtx,
			this.game.date.text.replace(/-/gi, '.'),
			this.rect.w/2, this.rect.h/2 + 2,
			'center', 'middle', 22,
			KtaneGraphicsParams.MANUAL_FONT
		);

		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneDateOfManufactureGraphics };
