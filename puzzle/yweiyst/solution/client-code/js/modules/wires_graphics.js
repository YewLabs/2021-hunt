import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';
import { Rect, CardinalDirection, CubeFace } from '../geom.js';

const P = KtaneGraphicsParams.WIRES;

class KtaneWireGraphics {
	constructor(canvasCtx, game, rect, clickData, color,stripe_color, striped, label) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
		this.clickData = clickData;

		this.color = color;
		this.stripe_color = stripe_color;
		this.striped = striped;
		this.label = label;
		this.isCut = false;
	}
	isHovering() {
		return G.isHovering(this);
	}
	drawLabel() {
		const PADDING_X = 5.5;
		const PADDING_Y = 8.5;
		C.drawText(
			this.canvasCtx,
			this.label,
			this.rect.x - PADDING_X, this.rect.y + PADDING_Y,
			'center', 'middle',
			16, KtaneGraphicsParams.UI_FONT,
			'', '#edeff0'
		);
		C.drawText(
			this.canvasCtx,
			this.label,
			this.rect.x + this.rect.w + PADDING_X, this.rect.y + PADDING_Y,
			'center', 'middle',
			16, KtaneGraphicsParams.UI_FONT,
			'', '#edeff0'
		);
	}
	draw(active) {
		G.begin(this);
		if (this.isCut) {
			this.canvasCtx.beginPath();
			this.canvasCtx.rect(
				0, 0,
				this.rect.w/3, this.rect.h
			);
			this.canvasCtx.rect(
				this.rect.w*2/3, 0,
				this.rect.w/3, this.rect.h
			);
			this.canvasCtx.clip();
		}
		const segmentWidth = this.rect.w / P.NUM_SEGMENTS;
		if (this.striped) {
			for (let i = 0; i < P.NUM_SEGMENTS; i++) {
				const segmentColor = (i % 2 == 0) ? this.stripe_color : this.color;
				C.drawRect(
					this.canvasCtx,
					i * segmentWidth, 0,
					segmentWidth, this.rect.h,
					segmentColor,
					null, null,
					KtaneGraphicsParams.NO_SHADOW,
					[['rgba(0, 0, 0, 0.9)', 0, -1, 9]]
				);
			}
		}
		else {
			C.drawRect(
				this.canvasCtx,
				0, 0,
				this.rect.w, this.rect.h,
				this.color,
				null, null,
				KtaneGraphicsParams.NO_SHADOW,
				[['rgba(0, 0, 0, 0.9)', 0, -1, 9]]
			);
		}
		if (!this.isCut && active && this.isHovering()) {
			C.strokeRect(
				this.canvasCtx,
				0, 0, this.rect.w, this.rect.h,
				'#FFFF00', 3
			);
		}
		G.end(this);
	}
	updateMouse() {
		if (this.isCut) {
			return null;
		}
		let clickData = null;
		G.begin(this);
		if (this.isHovering()) {
			clickData = this.clickData;
		}
		G.end(this);
		return clickData;
	}
};

class KtaneWiresGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.wires = [];
		this.panelWidth = this.rect.w - 3 * KtaneGraphicsParams.SUBMODULE_SPACING - 2 * KtaneGraphicsParams.DISARMED_RADIUS;
		const wireLength = this.panelWidth - 2 * P.WIRES_MARGIN;
		for (let i = 0; i < P.NUM_WIRES; i++) {
			this.wires.push(new KtaneWireGraphics(
				this.canvasCtx, this.game,
				new Rect(
					KtaneGraphicsParams.SUBMODULE_SPACING + P.WIRES_MARGIN,
					this.rect.h/2 + (i - (P.NUM_WIRES-1)/2) * (P.WIRE_SPACING + P.WIRE_THICKNESS) - P.WIRE_THICKNESS/2,
					wireLength, P.WIRE_THICKNESS
				),
				new KtaneClick(KtaneClick.WIRES_WIRE, i, () => {
					this.game.wires.doInput(i);
				}),
				null,
				null,
				null,
				i + 1
			));
		}
		this.clickables = this.wires;
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.wires.getTimeSinceStrike()
		);

		for (let i = 0; i < this.wires.length; i++) {
			this.wires[i].color = P.COLORS[this.game.wires.colors[i]];
			this.wires[i].stripe_color = P.STRIPED_COLORS[this.game.wires.colors[i]];
			this.wires[i].striped = this.game.wires.getStriped(i);
			this.wires[i].isCut = this.game.wires.getCut(i);
		}
		G.drawClickables(this, active);
		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		const attachHeight = this.rect.h - 2*spacing;
		C.drawRect(
			this.canvasCtx,
			spacing, spacing,
			P.ATTACH_WIDTH,
			attachHeight,
			P.ATTACH_COLOR,
			null, null,
			[['rgba(0, 0, 0, 0.8)', 0, 1, 4]]
		);
		C.drawRect(
			this.canvasCtx,
			spacing + this.panelWidth - P.ATTACH_WIDTH, spacing,
			P.ATTACH_WIDTH,
			attachHeight,
			P.ATTACH_COLOR,
			null, null,
			[['rgba(0, 0, 0, 0.8)', 0, 1, 4]]
		);
		for (let i = 0; i < this.wires.length; i++) {
			this.wires[i].drawLabel();
		}
		const disarmed = this.game.wires.disarmed;
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

export { KtaneWiresGraphics };
