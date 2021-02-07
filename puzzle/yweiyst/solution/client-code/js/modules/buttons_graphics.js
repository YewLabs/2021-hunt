import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';

const P = KtaneGraphicsParams.BUTTONS;

class KtaneButtonsGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		const spacingX = KtaneGraphicsParams.SUBMODULE_SPACING + 3;
		const spacingY = KtaneGraphicsParams.SUBMODULE_SPACING;
		const panelHeight = this.rect.h - KtaneGraphicsParams.DISARMED_OFFSET - KtaneGraphicsParams.DISARMED_RADIUS;
		const buttonWidth = (this.rect.w - (P.NUM_W+1) * spacingX) / P.NUM_W;
		const buttonHeight = (panelHeight - (P.NUM_H+1) * spacingY) / P.NUM_H;
		const buttonGridW = buttonWidth + spacingX;
		const buttonGridH = buttonHeight + spacingY;
		const buttonGridX = spacingX;
		const buttonGridY = this.rect.h - panelHeight + spacingY;
		this.buttons = [];
		for (let i = 0; i < P.NUM_H; i++) {
			for (let j = 0; j < P.NUM_W; j++) {
				const index = i * P.NUM_W + j;
				this.buttons.push(
					new TextButton(
						this.canvasCtx, this.game,
						new KtaneClick(KtaneClick.BUTTONS_BUTTON, index, () => {
							this.game.buttons.doInput(index);
						}),
						buttonGridX + buttonGridW * j,
						buttonGridY + buttonGridH * i,
						buttonWidth, buttonHeight,
						'',
						KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
						KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
						KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR,
						25
					)
				);
			}
		}
		this.clickables = this.buttons;
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.buttons.getTimeSinceStrike()
		);

		const state = this.game.buttons;
		const useOldData = this.game.useOldOrientation && !this.game.rotManager.isDesynced();
		const buttonTexts = useOldData ? state.oldButtonTexts : state.buttonTexts;
		const depressed = useOldData ? state.oldDepressed : state.depressed;

		const disarmed = this.game.buttons.disarmed;
		G.drawDisarmedLed(this, disarmed);
		for (let i = 0; i < this.buttons.length; i++) {
			const buttonText = buttonTexts[i];
			this.buttons[i].text = buttonText;
			this.buttons[i].overridePressed = depressed.includes(buttonText);
		}
		if (this.game.buttons.heldDown != null && !this.buttons[this.game.buttons.heldDown].clickData.equals(this.game.activeClick)) {
			this.game.buttons.doInput(this.game.buttons.heldDown, false);
			this.game.buttons.heldDown = null;
		}
		G.drawClickables(this, active && !this.game.buttons.disarmed);
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

export { KtaneButtonsGraphics };
