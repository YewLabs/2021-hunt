import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

class KtaneBatteriesGraphics {
	constructor(canvasCtx, game, rect, index) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
		this.index = index;
	}
	drawBattery(x, y, w, h, flipped=false) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y);
		if (flipped) {
			this.canvasCtx.rotate(-Math.PI);
		}
		const nubWidth = w/16;
		const nubHeight = h/3;
		let gradient = this.canvasCtx.createLinearGradient(0, -h/2, 0, h/2);
		gradient.addColorStop(flipped, '#101216');
		gradient.addColorStop(1-flipped, '#2a2c2d');
		this.canvasCtx.fillStyle = gradient;
		this.canvasCtx.fillRect(
			-w/2, -h/2, w*3/4, h,
		);
		gradient = this.canvasCtx.createLinearGradient(0, -h/2, 0, h/2);
		gradient.addColorStop(flipped, '#6b4122');
		gradient.addColorStop(1-flipped, '#fc8e43');
		this.canvasCtx.fillStyle = gradient;
		this.canvasCtx.fillRect(
			-w/2+w*2/3, -h/2-1, w*1/3-nubWidth, h+2,
		);
		C.drawRect(
			this.canvasCtx,
			w/2-nubWidth, -nubHeight/2,
			nubWidth, nubHeight,
			'#d1d6d9', null, null,
			KtaneGraphicsParams.NO_SHADOW
		);
		this.canvasCtx.restore();
	}
	draw(active) {
		G.begin(this);
		switch (this.game.batteries.numPerFace[this.index]) {
		case 0:
			break;
		case 1:
			C.drawRect(
				this.canvasCtx,
				this.rect.w/4-10, this.rect.h/4-5, this.rect.w/2+20, this.rect.h/2+10,
				'#53575b'
			);
			C.drawRect(
				this.canvasCtx,
				this.rect.w/4-2, this.rect.h/4, this.rect.w/2, this.rect.h/2+4,
				KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR
			);
			this.drawBattery(this.rect.w/4*2+1, this.rect.h/4*2, this.rect.w/2+1, this.rect.h/2-2);
			C.drawRect(
				this.canvasCtx,
				this.rect.w/4-2, 3+this.rect.h/4, 3, this.rect.h/2 - 5,
				'#b7c1ca'
			);
			C.drawRect(
				this.canvasCtx,
				3*this.rect.w/4-2, 3*this.rect.h/8, 3, this.rect.h/4,
				'#b7c1ca'
			);
			break;
		case 2:
			C.drawRect(
				this.canvasCtx,
				this.rect.w/4-10, -5, this.rect.w/2+20, this.rect.h+10,
				'#53575b'
			);
			C.drawRect(
				this.canvasCtx,
				this.rect.w/4, 0, this.rect.w/2, this.rect.h/2,
				KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR
			);
			C.drawRect(
				this.canvasCtx,
				this.rect.w/4, this.rect.h/2-2, this.rect.w/2, this.rect.h/2+2,
				KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR
			);
			this.drawBattery(this.rect.w/4*2+1, this.rect.h/4*1, this.rect.w/2+1, this.rect.h/2-2);
			this.drawBattery(this.rect.w/4*2-1, this.rect.h/4*3, this.rect.w/2+1, this.rect.h/2-2, true);
			C.drawRect(
				this.canvasCtx,
				this.rect.w/4-2, 5, 3, this.rect.h - 10,
				'#b7c1ca'
			);
			C.drawRect(
				this.canvasCtx,
				3*this.rect.w/4-2, this.rect.h/8, 3, this.rect.h/4,
				'#b7c1ca'
			);
			C.drawRect(
				this.canvasCtx,
				3*this.rect.w/4-2, 5*this.rect.h/8, 3, this.rect.h/4,
				'#b7c1ca'
			);
			break;
		case 3:
			C.drawRect(
				this.canvasCtx,
				-5, -5, this.rect.w+10, this.rect.h+10,
				'#53575b'
			);
			C.drawRect(
				this.canvasCtx,
				0, 0, this.rect.w/2, this.rect.h/2,
				KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR
			);
			C.drawRect(
				this.canvasCtx,
				0, this.rect.h/2-2, this.rect.w, this.rect.h/2+2,
				KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR
			);
			this.drawBattery(this.rect.w/4*1+1, this.rect.h/4*1, this.rect.w/2+1, this.rect.h/2-2);
			this.drawBattery(this.rect.w/4*3-2, this.rect.h/4*3, this.rect.w/2+1, this.rect.h/2-2, true);
			this.drawBattery(this.rect.w/4*1-1, this.rect.h/4*3, this.rect.w/2+1, this.rect.h/2-2, true);
			C.drawRect(
				this.canvasCtx,
				-2, 5, 3, this.rect.h - 10,
				'#b7c1ca'
			);
			C.drawRect(
				this.canvasCtx,
				this.rect.w/2-2, this.rect.h/8, 3, this.rect.h/4,
				'#b7c1ca'
			);
			C.drawRect(
				this.canvasCtx,
				this.rect.w-3, 5*this.rect.h/8, 3, this.rect.h/4,
				'#b7c1ca'
			);
			break;
		case 4:
			C.drawRect(
				this.canvasCtx,
				-5, -5, this.rect.w+10, this.rect.h+10,
				'#53575b'
			);
			C.drawRect(
				this.canvasCtx,
				0, 0, this.rect.w, this.rect.h,
				KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR
			);
			this.drawBattery(this.rect.w/4*1+1, this.rect.h/4*1, this.rect.w/2+1, this.rect.h/2-2);
			this.drawBattery(this.rect.w/4*3-2, this.rect.h/4*3, this.rect.w/2+1, this.rect.h/2-2, true);
			this.drawBattery(this.rect.w/4*3-1, this.rect.h/4*1, this.rect.w/2+1, this.rect.h/2-2);
			this.drawBattery(this.rect.w/4*1-1, this.rect.h/4*3, this.rect.w/2+1, this.rect.h/2-2, true);
			C.drawRect(
				this.canvasCtx,
				-2, 5, 3, this.rect.h - 10,
				'#b7c1ca'
			);
			C.drawRect(
				this.canvasCtx,
				this.rect.w-3, this.rect.h/8, 3, this.rect.h/4,
				'#b7c1ca'
			);
			C.drawRect(
				this.canvasCtx,
				this.rect.w-3, 5*this.rect.h/8, 3, this.rect.h/4,
				'#b7c1ca'
			);
			break;
		}

		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneBatteriesGraphics };
