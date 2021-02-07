import { Rect, CardinalDirection, CubeFace } from './geom.js';
import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsControl as G } from './graphics_control.js';
import { KtaneClick } from './input.js';
import { KtaneGraphicsParams as P } from './graphics_params.js';

function getButtonColor(comp, active) {
	if (!active) {
		return comp.color;
	}
	if (comp.isPressed()) {
		return comp.pressedColor;
	}
	if (comp.isHovering()) {
		return comp.hoverColor;
	}
	return comp.color;
}

class TextButton {
	constructor(canvasCtx, game, clickData, x, y, w, h, text, color, pressedColor, hoverColor, fontSize=null) {
		this.canvasCtx = canvasCtx;
		this.game = game;

		this.clickData = clickData;
		this.rect = new Rect(x, y, w, h - 5);
		this.text = text;
		this.color = color;
		this.pressedColor = pressedColor;
		this.hoverColor = hoverColor;
		this.fontSize = (fontSize == null) ? 14 : fontSize;

		this.overridePressed = false;
	}
	isHovering() {
		return G.isHovering(this);
	}
	isPressed() {
		if (this.overridePressed) {
			return true;
		}
		return this.clickData.equals(this.game.activeClick);
	}
	updateMouse() {
		let clickData = null;
		G.begin(this);
		if (this.isHovering()) {
			clickData = this.clickData;
		}
		G.end(this);
		return clickData;
	}
	draw(active) {
		G.begin(this);
		const color = this.overridePressed ? this.pressedColor : getButtonColor(this, active);
		const [r, g, b] = C.toRgb(color);
		const darken = (t) => C.interpolateRgba(r, g, b, 1, 0, 0, 0, 1, t);
		C.drawRect(
			this.canvasCtx,
			0, 0, this.rect.w, this.rect.h,
			color, null, 0,
			[
				[darken(0.3), 0, 2, 2],
				[darken(0.4), 0, 3, 4],
				[darken(0.5), 0, -2, 2.5],
				[darken(0.3), 0, -3, 3]
			],
			[
				[darken(0.5), 0, 0, (active && this.isHovering()) ? 5 : 3],
				(active && this.isPressed()) ? [darken(0.6), 0, 0, 10] : []
			]
		);
		C.drawText(
			this.canvasCtx,
			this.text,
			this.rect.w / 2,
			this.rect.h / 2 + this.fontSize / 10,
			'center', 'middle',
			this.fontSize,
			P.UI_FONT, '', '#000000'
		);
		G.end(this);
	}
};

const TRIANGLE_BUTTON_NORM_PATH = [
	[-1, 0],
	[1, 0],
	[0, -1],
];

class TriangleButton {
	constructor(canvasCtx, game, clickData, x, y, w, h, orientation, color, pressedColor, hoverColor) {
		this.canvasCtx = canvasCtx;
		this.game = game;

		this.clickData = clickData;
		this.orientation = orientation;
		this.color = color;
		this.pressedColor = pressedColor;
		this.hoverColor = hoverColor;
		this.rect = new Rect(x, y, w, h);
		this.normTransform = this.getNormTransform();
		this.path = [];
		for (const p of TRIANGLE_BUTTON_NORM_PATH) {
			const newp = this.normTransform.transformPoint(new DOMPoint(p[0], p[1]));
			this.path.push([newp.x, newp.y]);
		}
	}
	getNormTransform() {
		const mat = new DOMMatrix();
		mat.scaleSelf(this.rect.w/2, this.rect.h);
		return mat;
	}
	isHovering() {
		this.canvasCtx.save();
		this.canvasCtx.transform(
			this.normTransform.a,
			this.normTransform.b,
			this.normTransform.c,
			this.normTransform.d,
			this.normTransform.e,
			this.normTransform.f
		);
		const p = C.invPoint(
			this.canvasCtx,
			this.game.mouseX,
			this.game.mouseY
		);
		this.canvasCtx.restore();
		if (p.x - p.y > 1) {
			return false;
		}
		if (-p.x - p.y > 1) {
			return false;
		}
		if (p.y > 0) {
			return false;
		}
		return true;
	}
	isPressed() {
		return this.clickData.equals(this.game.activeClick);
	}
	doRotate() {
		this.canvasCtx.rotate(CardinalDirection.toAngle(this.orientation));
	}
	updateMouse() {
		let clickData = null;
		G.begin(this);
		this.doRotate();
		if (this.isHovering()) {
			clickData = this.clickData;
		}
		G.end(this);
		return clickData;
	}
	drawPath(transX=0) {
		for (let i = 0; i < this.path.length; i++) {
			if (i == 0) {
				this.canvasCtx.moveTo(transX + this.path[i][0], this.path[i][1]);
			}
			else {
				this.canvasCtx.lineTo(transX + this.path[i][0], this.path[i][1]);
			}
		}
		this.canvasCtx.closePath();
	}
	draw(active) {
		G.begin(this);
		this.doRotate();
		const color = getButtonColor(this, active);
		const [r, g, b] = C.toRgb(color);
		const darken = (t) => C.interpolateRgba(r, g, b, 1, 0, 0, 0, 1, t);

		// draw actual path
		this.canvasCtx.save();
		this.canvasCtx.beginPath();
		this.drawPath();
		C.doShadow(this.canvasCtx, color,
			[
				[darken(0.3), 0, 0.5, 1],
				[darken(0.6), 0, 1, 2.5],
				[darken(0.7), 0, -0.5, 1.1],
				[darken(0.3), 0, -1, 1.2]
			]
		);
		this.canvasCtx.restore();

		// draw inset
		this.canvasCtx.save();
		this.canvasCtx.globalCompositeOperation = 'source-atop';
		this.canvasCtx.beginPath();
		this.drawPath(-500);

		let shadowOffsetX = 0;
		let shadowOffsetY = 0;
		switch (this.orientation) {
		case CardinalDirection.N:
			shadowOffsetX = 500;
			break;
		case CardinalDirection.S:
			shadowOffsetX = -500;
			break;
		case CardinalDirection.W:
			shadowOffsetY = -500;
			break;
		case CardinalDirection.E:
			shadowOffsetY = 500;
			break;
		}
		if (active && this.isHovering()) {
			C.doStroke(
				this.canvasCtx,
				color, 0,
				darken(0.4), shadowOffsetX, shadowOffsetY, 0.5
			);
		}
		if (active && this.isPressed()) {
			C.doStroke(
				this.canvasCtx,
				color, 0,
				darken(0.9), shadowOffsetX, shadowOffsetY, 5
			);
		}
		this.canvasCtx.restore();

		G.end(this);
	}
};

class QuadrantButton {
	constructor(canvasCtx, game, clickData, x, y, r, orientation, color, pressedColor, hoverColor) {
		this.canvasCtx = canvasCtx;
		this.game = game;

		this.clickData = clickData;
		this.rect = new Rect(x, y, r, r);
		this.r = r;
		this.orientation = orientation;
		this.color = color;
		this.pressedColor = pressedColor;
		this.hoverColor = hoverColor;
	}
	drawPath(transX=0) {
		const sqrtR = Math.sqrt(this.r);
		this.canvasCtx.moveTo(transX, 0);
		this.canvasCtx.lineTo(transX-sqrtR, -sqrtR);
		this.canvasCtx.arc(transX, 0, this.r, Math.PI * 5/4, Math.PI * 7/4);
		this.canvasCtx.lineTo(transX, 0);
	}
	isHovering() {
		const p = C.invPoint(
			this.canvasCtx,
			this.game.mouseX,
			this.game.mouseY
		);
		if (p.x + p.y > 0) {
			return false;
		}
		if (-p.x + p.y > 0) {
			return false;
		}
		if (p.x * p.x + p.y * p.y > this.r * this.r) {
			return false;
		}
		return true;
	}
	isPressed() {
		return this.clickData.equals(this.game.activeClick);
	}
	doRotate() {
		this.canvasCtx.rotate(CardinalDirection.toAngle(this.orientation));
	}
	updateMouse() {
		let clickData = null;
		G.begin(this);
		this.doRotate();
		if (this.isHovering()) {
			clickData = this.clickData;
		}
		G.end(this);
		return clickData;
	}
	draw(active) {
		G.begin(this);
		this.doRotate();
		const color = getButtonColor(this, active);
		const [r, g, b] = C.toRgb(color);
		const darken = (t) => C.interpolateRgba(r, g, b, 1, 0, 0, 0, 1, t);

		this.canvasCtx.save();
		this.canvasCtx.beginPath();
		this.drawPath();
		C.doShadow(this.canvasCtx, color,
			[
				[darken(0.3), 0, 0.5, 1],
				[darken(0.6), 0, 1, 2.5],
				[darken(0.7), 0, -0.5, 1.1],
				[darken(0.3), 0, -1, 1.2]
			]
		);
		this.canvasCtx.restore();

		if (this.clickData !== null) {
			this.canvasCtx.save();
			this.canvasCtx.globalCompositeOperation = 'source-atop';
			this.canvasCtx.beginPath();
			this.drawPath(-500);

			let shadowOffsetX = 0;
			let shadowOffsetY = 0;
			switch (this.orientation) {
				case CardinalDirection.N:
					shadowOffsetX = 500;
					break;
				case CardinalDirection.S:
					shadowOffsetX = -500;
					break;
				case CardinalDirection.W:
					shadowOffsetY = -500;
					break;
				case CardinalDirection.E:
					shadowOffsetY = 500;
					break;
			}
			const shadowBlur = (active && this.isHovering()) ? 8 : 5;
			C.doStroke(
				this.canvasCtx,
				color, 0,
				darken(0.4), shadowOffsetX, shadowOffsetY, shadowBlur
			);
			if (active && this.isPressed()) {
				C.doStroke(
					this.canvasCtx,
					color, 0,
					darken(0.8), shadowOffsetX, shadowOffsetY, 20
				);
			}
			this.canvasCtx.restore();
		}

		G.end(this);
	}
};

const MUTE_BUTTON_NORM_PATH = [
	[0, -1],
	[1, -2],
	[1, 2],
	[0, 1],
	[-1, 1],
	[-1, -1],
];

class MuteButton {
	constructor(canvasCtx, game, clickData, x, y, w, h, color, pressedColor, hoverColor) {
		this.canvasCtx = canvasCtx;
		this.game = game;

		this.clickData = clickData;
		this.color = color;
		this.pressedColor = pressedColor;
		this.hoverColor = hoverColor;
		this.rect = new Rect(x, y, w, h);
		this.normTransform = this.getNormTransform();
		this.path = [];
		for (const p of MUTE_BUTTON_NORM_PATH) {
			const newp = this.normTransform.transformPoint(new DOMPoint(p[0], p[1]));
			this.path.push([newp.x, newp.y]);
		}
	}
	getNormTransform() {
		const mat = new DOMMatrix();
		mat.scaleSelf(this.rect.w/2, this.rect.h);
		return mat;
	}
	isHovering() {
		this.canvasCtx.save();
		this.canvasCtx.transform(
			this.normTransform.a,
			this.normTransform.b,
			this.normTransform.c,
			this.normTransform.d,
			this.normTransform.e,
			this.normTransform.f,
		);
		const p = C.invPoint(
			this.canvasCtx,
			this.game.mouseX,
			this.game.mouseY
		);
		const res = new Rect(-1, -2, 4, 4).inBounds(p.x, p.y);
		this.canvasCtx.restore();
		return res;
	}
	isPressed() {
		return this.clickData.equals(this.game.activeClick);
	}
	updateMouse() {
		let clickData = null;
		G.begin(this);
		if (this.isHovering()) {
			clickData = this.clickData;
		}
		G.end(this);
		return clickData;
	}
	drawPath(transX=0) {
		for (let i = 0; i < this.path.length; i++) {
			if (i == 0) {
				this.canvasCtx.moveTo(transX + this.path[i][0], this.path[i][1]);
			}
			else {
				this.canvasCtx.lineTo(transX + this.path[i][0], this.path[i][1]);
			}
		}
		this.canvasCtx.closePath();
	}
	draw(active) {
		G.begin(this);

		const color = getButtonColor(this, active);

		this.canvasCtx.beginPath();
		this.drawPath();
		C.doFill(this.canvasCtx, color);

		const center_x = (this.path[1][0] + this.path[2][0])/2 + this.rect.w / 4;
		const center_y = (this.path[1][1] + this.path[2][1])/2;
		const r1 = this.rect.w / 3;
		const r2 = 2*this.rect.w / 3;

		if (this.muted) {
			this.canvasCtx.beginPath();
			this.canvasCtx.moveTo(center_x, center_y - r1);
			this.canvasCtx.lineTo(center_x + 2*r1, center_y + r1);
			C.doStroke(this.canvasCtx, color, 2);

			this.canvasCtx.beginPath();
			this.canvasCtx.moveTo(center_x + 2*r1, center_y - r1);
			this.canvasCtx.lineTo(center_x, center_y + r1);
			C.doStroke(this.canvasCtx, color, 2);
		} else {
			this.canvasCtx.beginPath();
			this.canvasCtx.arc(center_x, center_y, r1, -Math.PI/2, Math.PI/2);
			C.doStroke(this.canvasCtx, color, 2);

			this.canvasCtx.beginPath();
			this.canvasCtx.arc(center_x, center_y, r2, -Math.PI/2, Math.PI/2);
			C.doStroke(this.canvasCtx, color, 2);
		}

		G.end(this);
	}
};

class Slider {
	constructor(canvasCtx, game, clickData, x, y, w, h, color) {
		this.canvasCtx = canvasCtx;
		this.game = game;

		this.clickData = clickData;
		this.color = color;
		this.rect = new Rect(x, y, w, h);

		this.value = 0;
		this.candidateValue = null;
		this.thumbR = this.rect.w/2;
		this.slideHeight = this.rect.h - 2*this.thumbR;
	}
	isHovering() {
		return G.isHovering(this);
	}
	isPressed() {
		return this.clickData.equals(this.game.activeClick);
	}
	doRotate() {
		this.canvasCtx.translate(this.rect.h, 0);
		this.canvasCtx.rotate(Math.PI/2);
		this.canvasCtx.translate(0, 0);
	}
	updateMouse() {
		let clickData = null;
		G.begin(this);
		this.doRotate();
		if (this.isHovering()) {
			clickData = this.clickData;
		}
		G.end(this);
		return clickData;
	}
	updateThumb() {
		G.begin(this);
		this.doRotate();
		if (this.isPressed()) {
			const p = C.invPoint(
				this.canvasCtx,
				this.game.mouseX,
				this.game.mouseY
			);
			const relPos = (p.y - this.thumbR) / this.slideHeight;
			this.value = Math.min(Math.max(relPos, 0), 1);
		}
		G.end(this);
	}
	draw(active) {
		G.begin(this);
		this.doRotate();

		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(this.rect.w/2, 0);
		this.canvasCtx.lineTo(this.rect.w/2, this.rect.h);
		C.doStroke(this.canvasCtx, this.color, 5);

		const thumbY = this.slideHeight * this.value + this.thumbR;
		C.drawCirc(
			this.canvasCtx,
			this.rect.w/2, thumbY, this.thumbR,
			this.color
		);

		G.end(this);
	}
};

class Toggle {
	constructor(canvasCtx, game, clickData, x, y, w, h, text) {
		this.canvasCtx = canvasCtx;
		this.game = game;

		this.clickData = clickData;
		this.rect = new Rect(x, y, w, h);
		this.text = text;
		this.textWidth = 0;
		this.strokeWidth = 1;
		this.clickAreaPadding = 4;
		this.textSpacing = 10;

		this.value = false;
	}
	isHovering() {
		const p = C.invPoint(
			this.canvasCtx,
			this.game.mouseX,
			this.game.mouseY
		);
		const padding = this.clickAreaPadding;
		return new Rect(
			-padding, -padding,
			this.rect.w + this.textSpacing + this.textWidth + 2*padding,
			this.rect.h + 2*padding
		).inBounds(p.x, p.y);
	}
	isPressed() {
		return this.clickData.equals(this.game.activeClick);
	}
	updateMouse() {
		let clickData = null;
		G.begin(this);
		if (this.isHovering()) {
			clickData = this.clickData;
		}
		G.end(this);
		return clickData;
	}
	draw(active) {
		G.begin(this);
		const offColor = '#BBBBBB';
		const onColor = '#DDDDDD';
		const onBgColor = '#888888';
		const color = this.value ? onColor : offColor;

		const r = this.rect.h/2;
		this.canvasCtx.beginPath();
		this.canvasCtx.arc(r, r, r, Math.PI/2, Math.PI*3/2);
		this.canvasCtx.arc(this.rect.w-r, r, r, Math.PI*3/2, Math.PI/2);
		this.canvasCtx.closePath();
		C.doStroke(this.canvasCtx, color, this.strokeWidth);
		if (this.value) {
			C.doFill(this.canvasCtx, onBgColor);
		}
		C.drawCirc(
			this.canvasCtx,
			this.value ? (this.rect.w-r) : r, r, r*5/6,
			color
		);
		C.drawText(
			this.canvasCtx,
			this.text,
			this.rect.w + this.textSpacing,
			this.rect.h/2 + 1,
			'left', 'middle',
			12,
			P.UI_FONT, '', offColor
		);
		this.textWidth = this.canvasCtx.measureText(this.text).width;

		G.end(this);
	}
};

export { TextButton, TriangleButton, QuadrantButton, MuteButton, Slider, Toggle };
