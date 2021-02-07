import { CardinalDirection, Rect } from './geom.js';
import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsParams } from './graphics_params.js';

class KtaneGraphicsControl {
	static drawClickables(comp, active) {
		for (const clickable of comp.clickables) {
			clickable.draw(active);
		}
	}
	static updateClick(oldClick, newClick) {
		return (newClick != null) ? newClick : oldClick;
	}
	static updateMouseClickables(comp) {
		let bestClick = null;
		for (const clickable of comp.clickables) {
			const clickData = clickable.updateMouse();
			bestClick = KtaneGraphicsControl.updateClick(bestClick, clickData);
		}
		return bestClick;
	}
	static begin(comp) {
		comp.canvasCtx.save();
		comp.canvasCtx.translate(comp.rect.x, comp.rect.y);
	}
	static end(comp) {
		comp.canvasCtx.restore();
	}
	static rotateAboutCenter(comp, angle) {
		comp.canvasCtx.translate(comp.rect.w/2, comp.rect.h/2);
		comp.canvasCtx.rotate(angle);
		comp.canvasCtx.translate(-comp.rect.w/2, -comp.rect.h/2);
	}
	static isHovering(comp) {
		const p = C.invPoint(
			comp.canvasCtx,
			comp.game.mouseX,
			comp.game.mouseY
		);
		return new Rect(0, 0, comp.rect.w, comp.rect.h).inBounds(p.x, p.y);
	}
	static timerToProgress(timer, pulseWidth) {
		return (timer == null) ? 1 : Math.min(timer / pulseWidth, 1);
	}
	static drawBackgroundWithStrike(comp, timeSinceStrike) {
		const strikePulseProgress = KtaneGraphicsControl.timerToProgress(
			timeSinceStrike, KtaneGraphicsParams.STRIKE_PULSE
		);
		const strikeColor = KtaneGraphicsParams.BACKGROUND_STRIKE_COLOR;
		const color = KtaneGraphicsParams.MODULE_BACKGROUND_COLOR;
		C.drawRect(
			comp.canvasCtx,
			0, 0, comp.rect.w, comp.rect.h,
			C.interpolateRgba(
				strikeColor[0], strikeColor[1], strikeColor[2], 1,
				color[0], color[1], color[2], 1,
				strikePulseProgress
			),
			// KtaneGraphicsParams.MODULE_STROKE_COLOR,
			// KtaneGraphicsParams.MODULE_STROKE_WIDTH
			null, null,
			[['rgba(0, 0, 0, 0.5)', 0, -1, 5]],
			[['rgba(0, 0, 0, 0.9)', 0, -1, 7], ['rgba(0, 0, 0, 0.7)', 0, -1, 10]]
		);
	}
	static drawDisarmedLed(comp, disarmed, x=null, y=null) {
		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		if (x == null) {
			x = comp.rect.w - spacing - KtaneGraphicsParams.DISARMED_RADIUS;
		}
		if (y == null) {
			y = spacing + KtaneGraphicsParams.DISARMED_RADIUS;
		}
		C.drawCirc(
			comp.canvasCtx,
			x, y,
			KtaneGraphicsParams.DISARMED_RADIUS,
			disarmed ? KtaneGraphicsParams.DISARMED_COLOR_ON :
				KtaneGraphicsParams.DISARMED_COLOR_OFF,
			null, null,
			[
				['rgba(0, 0, 0, 0.5)', 0, -1, 4],
				['rgba(29, 253, 73, 0.9)', 0, 0, disarmed ? 10 : 0]
			],
			[['#134413', 0, -1, 5]]
		);
	}
	static forEachDir(x, y, offset, func) {
		return [
			func(
				x, y - offset,
				CardinalDirection.N
			),
			func(
				x + offset, y,
				CardinalDirection.E
			),
			func(
				x, y + offset,
				CardinalDirection.S
			),
			func(
				x - offset, y,
				CardinalDirection.W
			),
		];
	}
	static timeDeltaAsString(td) {
		const totSeconds = Math.floor(td / 1000);
		const minutes = Math.floor(totSeconds / 60);
		const seconds = totSeconds - minutes * 60;
		return `${minutes}:${seconds.toString().padStart(2, '0')}`;
	}
	static directionalShadow() {
	}
};

export { KtaneGraphicsControl };
