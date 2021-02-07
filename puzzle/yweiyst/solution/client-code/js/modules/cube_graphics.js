import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';

const P = KtaneGraphicsParams.CUBE;

class KtaneCubeGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.clickables = [
			new TextButton(
				this.canvasCtx, this.game,
				new KtaneClick(KtaneClick.CUBE_START_BUTTON, null, () => {
					this.game.cube.doInput();
				}),
				this.rect.w/2 - P.START_BUTTON_WIDTH/2,
				this.rect.h/2 - P.START_BUTTON_HEIGHT/2 + 50,
				P.START_BUTTON_WIDTH,
				P.START_BUTTON_HEIGHT,
				'START',
				KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
				KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
				KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR,
				25
			)
		];
	}
	draw(active) {
		const PADDING_X = 30;
		const PADDING_Y = 50;
		const HEIGHT = 60;

		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.cube.getTimeSinceStrike()
		);
		C.drawRect(
			this.canvasCtx,
			PADDING_X, PADDING_Y,
			this.rect.w - 2*PADDING_X, HEIGHT,
			KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			KtaneGraphicsParams.SCREEN_INSET_SHADOW
		);
		C.drawText(
			this.canvasCtx,
			this.game.cube.text,
			this.rect.w/2, this.rect.h/2 - 22,
			'center', 'middle', 35,
			KtaneGraphicsParams.UI_FONT, '', '#0f0'
		);

		this.clickables[0].overridePressed = this.game.cube.started;
		G.drawClickables(this, active);
		const disarmed = this.game.cube.disarmed;
		G.drawDisarmedLed(this, disarmed);
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
};

export { KtaneCubeGraphics };
