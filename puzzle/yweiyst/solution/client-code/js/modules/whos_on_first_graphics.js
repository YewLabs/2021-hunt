import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';
import FONTFACE from './font.js';

const P = KtaneGraphicsParams.WHOS_ON_FIRST;

class KtaneWhosOnFirstGraphics {
	constructor(canvasCtx, game, rect, state) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
		this.state = state;

		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		this.consolePanelWidth = this.rect.h * P.CONSOLE_RATIO;
		this.consolePanelHeight = this.consolePanelWidth;
		this.consoleWidth = this.consolePanelWidth - 2 * spacing;

		const rightPanelWidth = this.rect.w - this.consoleWidth - 2 * spacing;
		const rightPanelOffset = 3 * spacing + 2 * KtaneGraphicsParams.DISARMED_RADIUS;
		const rightPanelHeight = this.rect.h - rightPanelOffset;
		const buttonWidth = rightPanelWidth - spacing;
		const buttonHeight = (rightPanelHeight - 2*spacing) / 4;
		this.inputButtons = [];
		for (let i = 0; i < 4; i++) {
			this.inputButtons.push(
				new TextButton(
					this.canvasCtx, this.game,
					new KtaneClick(KtaneClick.WHOS_ON_FIRST_BUTTON, i, () => {
						this.state.doInput(this.state.buttonOrder[i]);
					}),
					this.rect.w - rightPanelWidth,
					rightPanelOffset + i*buttonHeight + i*spacing/2,
					buttonWidth, buttonHeight,
					'',
					KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
					KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
					KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR,
					20
				)
			);
		}
		this.clickables = this.inputButtons;
	}
	isImgValid() {
		const state = this.state;
		if (!state.imgReady) {
			return false;
		}
		return state.cachedText != null && state.cachedText == state.text;
	}
	updateImg() {
		const state = this.state;
		if (!state.imgReady) {
			return;
		}
		if (this.isImgValid()) {
			return;
		}
		state.cachedText = state.text;
		state.imgReady = false;

		C.makeHtmlImg(
			this.consoleWidth, this.consoleWidth,
			`<style type="text/css">${FONTFACE}</style>`,
			`<div style="margin:10px;color:#00FF00;font-family:'Courier New',monospace;font-size:20px;font-weight:bold;">
				${state.cachedText}
			</div>`,
			(img) => {
				state.img = img;
				state.imgReady = true;
			}
		);
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.state.getTimeSinceStrike()
		);

		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		C.drawRect(
			this.canvasCtx,
			spacing, spacing,
			this.consoleWidth, this.consoleWidth,
			KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			KtaneGraphicsParams.SCREEN_INSET_SHADOW
		);
		this.updateImg();
		if (this.isImgValid()) {
			this.canvasCtx.drawImage(
				this.state.img, spacing, spacing
			);
		}
		const textInputHeight = this.rect.h - this.consolePanelHeight - spacing;
		C.drawRect(
			this.canvasCtx,
			spacing, this.consolePanelHeight,
			this.consolePanelWidth - 2 * spacing, textInputHeight,
			KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR,
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			KtaneGraphicsParams.SCREEN_INSET_SHADOW
		);

		const state = this.state
		const useOldData = this.game.useOldOrientation && !this.game.rotManager.isDesynced();
		const presses = useOldData ? state.oldPresses : state.presses;
		const buttonOrder = useOldData ? state.oldButtonOrder : state.buttonOrder;

		let inputString = '';
		for (let i = 0; i < presses.length; i++) {
			inputString += P.BUTTON_TEXTS[presses[i]];
		}
		C.drawText(
			this.canvasCtx,
			`> ${inputString}`,
			spacing + spacing,
			this.consolePanelHeight + textInputHeight/2,
			'left', 'middle', 20, 'Courier New', 'bold', '#00FF00'
		);
		const disarmed = this.state.disarmed;
		G.drawDisarmedLed(this, disarmed);
		for (let i = 0; i < this.inputButtons.length; i++) {
			if (buttonOrder == null) {
				this.inputButtons[i].text = '';
			}
			else {
				const buttonIndex = buttonOrder[i];
				this.inputButtons[i].text = P.BUTTON_TEXTS[buttonIndex];
			}
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

export { KtaneWhosOnFirstGraphics };
