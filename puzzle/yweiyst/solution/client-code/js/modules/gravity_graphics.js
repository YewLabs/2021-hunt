import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

const P = KtaneGraphicsParams.GRAVITY;

class KtaneGravityGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
	}
	drawBolt(x, y) {
		const RADIUS = 5;
		C.drawCirc(
			this.canvasCtx, x, y, RADIUS,
			'#d4d9de'
		);
	}
	draw(active) {
		const PAPER_WIDTH = 210;
		const PAPER_HEIGHT = 60;
		const ACCENT_HEIGHT = 50;
		const INNER_PADDING_X = 25;
		const INNER_PADDING_Y = 15;
		const INNER_WIDTH = PAPER_WIDTH - 2*INNER_PADDING_X;
		const PADDING_X = (this.rect.w - PAPER_WIDTH)/2;
		const PADDING_Y = (this.rect.h - PAPER_HEIGHT - ACCENT_HEIGHT - INNER_PADDING_Y)/2;
		const BOLT_PADDING_X = 10;
		const BOLT_PADDING_Y = 11;
		const TOTAL_Y = PADDING_Y + ACCENT_HEIGHT + PAPER_HEIGHT + INNER_PADDING_Y;

		G.begin(this);
		G.drawBackgroundWithStrike(
			this, null
		);

		C.drawRect(
			this.canvasCtx,
			PADDING_X, PADDING_Y, PAPER_WIDTH, ACCENT_HEIGHT + PAPER_HEIGHT + INNER_PADDING_Y,
			'#61615f',
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			[['#212121', 0, -1, 2], ['#21212188', 0, -1, 4]]
		);

		C.drawRect(
			this.canvasCtx,
			PADDING_X + INNER_PADDING_X, PADDING_Y + ACCENT_HEIGHT, INNER_WIDTH, PAPER_HEIGHT,
			KtaneGraphicsParams.PAPER_BACKGROUND_COLOR,
		);

		C.drawText(
			this.canvasCtx,
			'GRAVITY SENSOR',
			this.rect.w/2, PADDING_Y + ACCENT_HEIGHT/2 + 2,
			'center', 'middle', 18,
			KtaneGraphicsParams.UI_FONT, 'bold', '#fff'
		);

		C.drawText(
			this.canvasCtx,
			this.game.gravity.text,
			this.rect.w/2, this.rect.h/2 + ACCENT_HEIGHT/2 - 2,
			'center', 'middle', 38,
			KtaneGraphicsParams.MANUAL_FONT
		);

		[
			[PADDING_X + BOLT_PADDING_X, PADDING_Y + BOLT_PADDING_Y],
			[PADDING_X + PAPER_WIDTH - BOLT_PADDING_X, PADDING_Y + BOLT_PADDING_Y],
			[PADDING_X + BOLT_PADDING_X, TOTAL_Y - BOLT_PADDING_Y],
			[PADDING_X + PAPER_WIDTH - BOLT_PADDING_X, TOTAL_Y - BOLT_PADDING_Y],
		].forEach(([x, y]) => this.drawBolt(x, y));

		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneGravityGraphics };

