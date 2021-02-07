import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

const P = KtaneGraphicsParams.SHAKE_IT;

const COUNTER_INTERVAL = 1000; // 1s

class KtaneShakeItGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.shakeIt.getTimeSinceStrike()
		);

		C.drawRect(
			this.canvasCtx,
			this.rect.w/2 - P.COUNTER_WIDTH/2,
			(this.rect.h - P.COUNTER_HEIGHT)/2,
			P.COUNTER_WIDTH,
			P.COUNTER_HEIGHT,
			KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			KtaneGraphicsParams.SCREEN_INSET_SHADOW
		);
		const timerVal = this.game.shakeIt.getTimerVal();
		const counterVal = (parseInt(timerVal / COUNTER_INTERVAL)).toString().padStart(3, '0');
		C.drawText(
			this.canvasCtx, 
			counterVal,
			this.rect.w/2,
			this.rect.h/2,
			'center', 'middle', '40',
			KtaneGraphicsParams.TIMER_FONT, '', '#FF0000',
			"red", 6
		);

		// C.drawText(
		// 	this.canvasCtx, 
		// 	"SHAKE IT",
		// 	this.rect.w/2,
		// 	this.rect.h - P.COUNTER_HEIGHT / 2,
		// 	'center', 'middle', '20',
		// 	KtaneGraphicsParams.UI_FONT
		// );

		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneShakeItGraphics };
