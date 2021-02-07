import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { TextButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';

const P = KtaneGraphicsParams.MANUAL_BUTTONS;
const SECTION_NAMES = KtaneGraphicsParams.MANUAL_SECTION_NAMES;

class KtaneManualButtonsGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.buttons = [];
		const buttonWidth = this.rect.w / SECTION_NAMES.length;
		const buttonHeight = this.rect.h;
		for (let i = 0; i < SECTION_NAMES.length; i++) {
			this.buttons.push(
				new TextButton(
					this.canvasCtx, this.game,
					new KtaneClick(KtaneClick.MANUAL_BUTTON, i, () => {
						this.game.manual.setSection(i);
					}),
					i * buttonWidth, 0,
					buttonWidth, buttonHeight,
					SECTION_NAMES[i],
					KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
					KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
					KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR,
					20
				)
			);
		}
		this.clickables = this.buttons;
	}
	draw(active) {
		G.begin(this);
		for (let i = 0; i < this.buttons.length; i++) {
			const sectionNum = this.game.manual.selectedSectionNum;
			this.buttons[i].overridePressed = i == sectionNum;
		}
		G.drawClickables(this, active);
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

export { KtaneManualButtonsGraphics };

