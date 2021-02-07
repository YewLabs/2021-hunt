import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { Rect, CardinalDirection, CubeFace } from '../geom.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';
import { manualData } from './manual/data.js';
import FONTFACE from './font.js';

const P = KtaneGraphicsParams.MANUAL;

class KtaneManualGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.manualWidth = this.rect.h;
		this.sidebarWidth = (this.rect.w - this.rect.h) / 2;

		this.landscapePageButtons = [
			this.makePageButton(
				this.manualWidth - P.LANDSCAPE_PAGE_BUTTON_MARGIN + 5*P.LANDSCAPE_PAGE_BUTTON_HEIGHT/3,
				P.LANDSCAPE_PAGE_BUTTON_WIDTH,
				false, false
			),
			this.makePageButton(
				this.manualWidth - P.LANDSCAPE_PAGE_BUTTON_MARGIN + 2*P.LANDSCAPE_PAGE_BUTTON_HEIGHT/3,
				2*P.LANDSCAPE_PAGE_BUTTON_WIDTH,
				false, true
			),
		];
		this.portraitPageButtons = [
			this.makePageButton(
				this.manualWidth - 4*P.PORTRAIT_PAGE_BUTTON_WIDTH/3,
				this.manualWidth - P.PORTRAIT_PAGE_BUTTON_MARGIN + P.PORTRAIT_PAGE_BUTTON_HEIGHT,
				true, false
			),
			this.makePageButton(
				this.manualWidth - P.PORTRAIT_PAGE_BUTTON_WIDTH,
				this.manualWidth - P.PORTRAIT_PAGE_BUTTON_MARGIN + P.PORTRAIT_PAGE_BUTTON_HEIGHT,
				true, true
			),
		];
		this.clickables = [];
	}
	isImgValid() {
		if (!(this.game.manual.sectionNum in this.game.manual.imgs)) {
			return false;
		}
		if (!(this.game.manual.pageNum in this.game.manual.imgs[this.game.manual.sectionNum])) {
			return false;
		}
		return true;
	}
	genPageHtml() {
		const sectionNum = this.game.manual.sectionNum;
		const pageNum = this.game.manual.pageNum;
		if (!(sectionNum in this.game.manual.infos) || pageNum >= this.game.manual.getTotPages()) {
			return null;
		}
		const renderer = this.game.manual.getRenderer();
		const subPageNum = this.game.manual.getSubPageNum();
		const pageHtml = renderer.getPage(subPageNum);
		return pageHtml;
	}
	updateImg() {
		const state = this.game.manual;
		if (!state.imgReady) {
			return false;
		}
		if (this.isImgValid()) {
			return;
		}

		const sectionNum = state.sectionNum;
		const pageNum = state.pageNum;
		const pageHtml = this.genPageHtml();
		if (pageHtml == null) {
			return;
		}

		state.imgReady = false;
		C.makeHtmlImg(
			this.manualWidth, this.manualWidth,
`<style type="text/css">
	${FONTFACE}
	#wrapper {
		box-sizing: border-box;
		color: #222;
		font: 18px 'Special Elite', 'Courier New', monospace;
		line-height: 1.2;
		padding: ${P.MANUAL_PADDING/2}px ${P.MANUAL_PADDING}px;
		width: 100%;
	}
	ul {
		padding-left: 10px;
	}
	h1, h2 {
		font-size: 20px;
		text-decoration: underline;
		margin: 10px 0 8px;
	}
	h2 {
		font-size: 18px;
		margin: 10px 0 8px;
	}
	p, li {
		margin: 0 0 10px;
	}
	table, th, td {
		border: 1px solid #222;
	}
	table {
		border-collapse: collapse;
		border-spacing: 0;
		margin: 10px auto;
	}
	th, td {
		padding: 6px 12px 4px;
	}
	img {
		display: block;
		margin: 12px auto;
	}
</style>
`,
`<div id="wrapper">
	${pageHtml}
</div>`,
			(img) => {
				if (!(sectionNum in state.imgs)) {
					state.imgs[sectionNum] = {};
				}
				state.imgs[sectionNum][pageNum] = img;
				state.imgReady = true;
			}
		);
	}
	makePageButton(x, y, isPortrait, isRight) {
		const index = isRight ? 1 : 0;
		const w = isPortrait ? P.PORTRAIT_PAGE_BUTTON_WIDTH : P.LANDSCAPE_PAGE_BUTTON_WIDTH;
		const h = isPortrait ? P.PORTRAIT_PAGE_BUTTON_HEIGHT : P.LANDSCAPE_PAGE_BUTTON_HEIGHT;
		return new TriangleButton(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.MANUAL_PAGE_BUTTON, index, () => {
				this.game.manual.flipPage(isRight);
			}),
			x, y, w, h,
			isRight ? CardinalDirection.E : CardinalDirection.W,
			KtaneGraphicsParams.DULL_BUTTON_COLOR,
			KtaneGraphicsParams.DULL_BUTTON_PRESSED_COLOR,
			KtaneGraphicsParams.DULL_BUTTON_HOVER_COLOR
		);
	}
	chooseClickables() {
		const playerRot = this.game.getPlayerRot();
		const isSideways = CardinalDirection.isHorizontal(playerRot);
		const state = this.game.manual;
		const isFirstPage = state.pageNum <= 0;
		const isLastPage = state.pageNum + 1 >= state.getTotPages();
		this.clickables = [];
		const pageButtons = isSideways ? this.portraitPageButtons : this.landscapePageButtons;
		if (!isFirstPage) {
			this.clickables.push(pageButtons[0]);
		}
		if (!isLastPage) {
			this.clickables.push(pageButtons[1]);
		}
	}
	autorotate() {
		const playerRot = this.game.getPlayerRot();
		this.canvasCtx.translate(this.rect.w/2, this.rect.h/2);
		this.canvasCtx.rotate(-CardinalDirection.toAngle(playerRot));
		this.canvasCtx.translate(-this.manualWidth/2, -this.manualWidth/2);
		switch (playerRot) {
			case CardinalDirection.N:
			case CardinalDirection.S:
				this.canvasCtx.translate(-this.sidebarWidth-P.MANUAL_PADDING/2, -P.MANUAL_PADDING/2);
				break;
			case CardinalDirection.W:
			case CardinalDirection.E:
				this.canvasCtx.translate(-P.MANUAL_PADDING/2, -this.sidebarWidth-P.MANUAL_PADDING/2);
				break;
		}
	}
	drawManualText() {
		this.updateImg();
		if (this.isImgValid()) {
			const img = this.game.manual.imgs[this.game.manual.sectionNum][this.game.manual.pageNum];
			this.canvasCtx.drawImage(
				img, 0, 0
			);
		}
	}
	drawSectionName() {
		const secAbbr = KtaneGraphicsParams.MANUAL_SECTION_NAMES[this.game.manual.sectionNum];
		const playerRot = this.game.getPlayerRot();
		const text_height = 25;
		let x, y, dg;
		switch (playerRot) {
			case CardinalDirection.N:
			case CardinalDirection.S:
				x = this.sidebarWidth + 5;
				y = this.rect.w - text_height - 5;
				dg = 90;
				break;
			case CardinalDirection.W:
			case CardinalDirection.E:
				x = this.sidebarWidth - 10;
				y = this.rect.w - 5;
				dg = 0;
				break;
		}
		this.canvasCtx.translate(this.rect.w/2, this.rect.h/2);
		this.canvasCtx.rotate(-dg*Math.PI/180);
		this.canvasCtx.translate(-this.rect.w/2, -this.rect.h/2);

		const secName = manualData["manual"]["abbrs"][secAbbr].toUpperCase();
		this.canvasCtx.save();
		this.canvasCtx.font = `20px ${KtaneGraphicsParams.UI_FONT}`;
		const textWidth = this.canvasCtx.measureText(secName).width;
		this.canvasCtx.restore();

		C.drawText(
			this.canvasCtx,
			secName, x, y,
			'start', 'bottom', 20,
			KtaneGraphicsParams.UI_FONT, 'bold',
			'#666'
		);
		C.drawText(
			this.canvasCtx,
			`Page ${this.game.manual.pageNum+1} of ${this.game.manual.getTotPages()}`.toUpperCase(),
			x + textWidth + 10, y, 'start', 'bottom', 14,
			KtaneGraphicsParams.UI_FONT, 'bold',
			'#666'
		);
		this.canvasCtx.translate(this.rect.w/2, this.rect.h/2);
		this.canvasCtx.rotate(dg*Math.PI/180);
		this.canvasCtx.translate(-this.rect.w/2, -this.rect.h/2);
	}
	draw(active) {
		G.begin(this);
		C.drawRect(
			this.canvasCtx,
			0, 0, this.rect.w, this.rect.h,
			'#FFFFFF',
			null, null,
			KtaneGraphicsParams.NO_SHADOW,
			KtaneGraphicsParams.SCREEN_INSET_SHADOW
		);

		this.autorotate();
		this.drawSectionName();
		this.drawManualText();
		this.chooseClickables();
		G.drawClickables(this, active);

		G.end(this);
	}
	updateMouse() {
		let bestClick = null;
		G.begin(this);
		this.autorotate();

		this.chooseClickables();
		bestClick = G.updateClick(
			bestClick,
			G.updateMouseClickables(this)
		);

		G.end(this);
		return bestClick;
	}
};

export { KtaneManualGraphics };
