import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { CardinalDirection, Rect } from '../geom.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';

const P = KtaneGraphicsParams.PASSWORDS;

class KtanePasswordsGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		this.disarmedMargin = this.rect.h/2 - KtaneGraphicsParams.DISARMED_RADIUS;
		const panelW = this.rect.w - 2*this.disarmedMargin - KtaneGraphicsParams.DISARMED_RADIUS;
		this.letterH = this.rect.h - spacing;
		this.letterW = this.letterH + 3*spacing;
		this.buttonW = this.rect.h - 2*spacing;
		this.buttonH = (panelW - this.letterW)/2 - 2*spacing;
		this.clickables = [
			this.makeSelectButton(false),
			this.makeSelectButton(true),
		];
	}
	makeSelectButton(isRight) {
		const orientation = isRight ? CardinalDirection.E : CardinalDirection.W;
		const buttonWidth = this.rect.h - KtaneGraphicsParams.SUBMODULE_SPACING * 2;
		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		const leftX = spacing + this.buttonH;
		const rightX = this.letterW + 3*spacing + this.buttonH;
		return new TriangleButton(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.PASSWORDS_BUTTON, orientation, () => {
				this.game.passwords.doInput(isRight);
			}),
			isRight ? rightX : leftX, this.rect.h/2,
			this.buttonW, this.buttonH * 4/5,
			orientation,
			KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
			KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
			KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR
		);
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.passwords.getTimeSinceStrike()
		);

		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		const letterX = 2*spacing + this.buttonH;
		const letterY = spacing / 2;
		C.drawRect(
			this.canvasCtx,
			letterX, letterY,  this.letterW, this.letterH,
			KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			KtaneGraphicsParams.SCREEN_INSET_SHADOW
		);
		const state = this.game.passwords;
		const useOldData = this.game.useOldOrientation && !this.game.rotManager.isDesynced();
		const letters = useOldData ? state.oldLetters : state.letters;
		const selected = useOldData ? state.oldSelected : state.selected;
		const selectedLetter = (selected == null) ?
			' ' : letters[selected].toUpperCase();
		C.drawText(
			this.canvasCtx,
			selectedLetter,
			letterX + this.letterW/2, letterY + this.letterH/2 + 2,
			'center', 'middle', 20,
			KtaneGraphicsParams.UI_FONT,
			'', '#ffffff'
		);

		const disarmed = this.game.passwords.disarmed;
		G.drawDisarmedLed(
			this, disarmed,
			this.rect.w - this.disarmedMargin - KtaneGraphicsParams.DISARMED_RADIUS,
			this.rect.h/2
		);
		G.drawClickables(this, active && !this.game.passwords.disarmed);
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

export { KtanePasswordsGraphics };
