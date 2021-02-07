import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

class KtaneEmptyGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
	}
	draw(active) {
		G.begin(this);
		C.strokeRect(
			this.canvasCtx,
			0, 0, this.rect.w, this.rect.h,
			// KtaneGraphicsParams.MODULE_STROKE_COLOR,
			// KtaneGraphicsParams.MODULE_STROKE_WIDTH
		);
		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneEmptyGraphics };
