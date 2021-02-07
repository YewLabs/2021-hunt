import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

class KtaneSerialNumberGraphics {
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
		const stripe_width = 60;

		C.drawRect(
			this.canvasCtx,
			x, y, width, height,
			KtaneGraphicsParams.PAPER_BACKGROUND_COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			[['#212121', 0, -1, 7], ['#21212188', 0, -1, 10]]
		);

		C.drawRect(
			this.canvasCtx,
			x, y, stripe_width, height,
			'#8a150e',
			null, null,
		);

		C.drawText(
			this.canvasCtx,
			"SERIAL",
			KtaneGraphicsParams.SUBMODULE_SPACING,
			this.rect.h/2 + 2,
			'start', 'middle', 16,
			KtaneGraphicsParams.UI_FONT,
			'bold', '#fff'
		);

		C.drawText(
			this.canvasCtx,
			this.game.serial.text,
			(this.rect.w + stripe_width)/2,
			this.rect.h/2 + 3,
			'center', 'middle', 22,
			KtaneGraphicsParams.MANUAL_FONT
		);

		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneSerialNumberGraphics };
