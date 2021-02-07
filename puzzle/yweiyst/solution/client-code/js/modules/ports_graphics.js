import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';

class KtanePortsGraphics {
	constructor(canvasCtx, game, rect, index) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
		this.index = index;
	}
	drawPin(x, y, rad=1) {
		C.drawCirc(
			this.canvasCtx,
			x, y, rad, '#1d1411'
		);
	}
	drawInnerCatches(r) {
		C.doFill(this.canvasCtx, '#1d1411');
		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(-1, -8);
		this.canvasCtx.arc(0, 0, r, 3/2*Math.PI - 0.1, 3/2*Math.PI + 0.1);
		this.canvasCtx.lineTo(1, -8);
		this.canvasCtx.closePath();
		C.doFill(this.canvasCtx, '#1d1411');
		this.canvasCtx.rotate(Math.PI*2/3 + 0.3);
		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(-1, -8);
		this.canvasCtx.arc(0, 0, r, 3/2*Math.PI - 0.1, 3/2*Math.PI + 0.1);
		this.canvasCtx.lineTo(1, -8);
		this.canvasCtx.closePath();
		C.doFill(this.canvasCtx, '#1d1411');
		this.canvasCtx.rotate(Math.PI*2/3 - 0.3*2);
		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(-1, -8);
		this.canvasCtx.arc(0, 0, r, 3/2*Math.PI - 0.1, 3/2*Math.PI + 0.1);
		this.canvasCtx.lineTo(1, -8);
		this.canvasCtx.closePath();
		C.doFill(this.canvasCtx, '#1d1411');
	}
	drawPS2(x, y) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y);
		const OUTER_R = 12;
		const INNER_R = 10;
		C.drawCirc(this.canvasCtx, 0, 0, OUTER_R, null, '#998872', 7);
		C.drawCirc(this.canvasCtx, 0, 0, OUTER_R, null, '#dfd9cd', 3);
		C.drawCirc(
			this.canvasCtx,
			0, 0, OUTER_R, '#37623a'
		);
		C.drawCirc(
			this.canvasCtx,
			0, 0, INNER_R, '#94e5bb'
		);
		this.drawPin(-6, 0, 1.3);
		this.drawPin(-4, -4, 1.3);
		this.drawPin(-4, 4, 1.3);
		this.drawPin(6, 0, 1.3);
		this.drawPin(4, -4, 1.3);
		this.drawPin(4, 4, 1.3);
		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(-2, -2);
		this.canvasCtx.lineTo(2, -2);
		this.canvasCtx.lineTo(1, 2);
		this.canvasCtx.lineTo(-1, 2);
		this.canvasCtx.closePath();
		this.drawInnerCatches(INNER_R);
		this.canvasCtx.restore();
	}
	drawRJ45(x, y) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y);
		const OUTER_WIDTH = 24;
		const INNER_WIDTH = 18;
		const CATCH_WIDTH = 7;
		const CATCH_HEIGHT = 6;
		C.drawRect(
			this.canvasCtx,
			-OUTER_WIDTH/2, -OUTER_WIDTH/2, OUTER_WIDTH, OUTER_WIDTH,
			null, '#1d1411', 5
		);
		C.drawRect(
			this.canvasCtx,
			-OUTER_WIDTH/2, -OUTER_WIDTH/2, OUTER_WIDTH, OUTER_WIDTH,
			'#f1e9e2'
		);
		C.drawRect(
			this.canvasCtx,
			-INNER_WIDTH/2, -INNER_WIDTH/2, INNER_WIDTH, INNER_WIDTH,
			null, '#dfd9cd', 3
		);
		C.drawRect(
			this.canvasCtx,
			-INNER_WIDTH/2, -INNER_WIDTH/2, INNER_WIDTH, INNER_WIDTH,
			'#2e2725'
		);
		C.drawRect(
			this.canvasCtx,
			-OUTER_WIDTH/2, INNER_WIDTH/2,
			OUTER_WIDTH, (OUTER_WIDTH-INNER_WIDTH)/2,
			'#797179'
		);
		C.drawRect(
			this.canvasCtx,
			-CATCH_WIDTH/2, INNER_WIDTH/2-CATCH_HEIGHT,
			CATCH_WIDTH, CATCH_HEIGHT,
			'#e9ddb9'
		);
		this.canvasCtx.restore();
	}
	drawPinGrid(num, spacingX, spacingY, rad=1, offsetY=0) {
		for (let i = 0; i < num; i++) {
			const pinX = (i - (num-1)/2) * spacingX;
			const pinY = (0.5 - i % 2) * spacingY + offsetY;
			this.drawPin(pinX, pinY, rad);
		}
	}
	drawSVideo(x, y) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y);
		const OUTER_R = 12;
		const INNER_R = 10;
		C.drawCirc(this.canvasCtx, 0, 0, OUTER_R, null, '#998872', 7);
		C.drawCirc(this.canvasCtx, 0, 0, OUTER_R, null, '#dfd9cd', 3);
		C.drawCirc(
			this.canvasCtx,
			0, 0, OUTER_R, '#37623a'
		);
		C.drawCirc(
			this.canvasCtx,
			0, 0, INNER_R, '#feb801'
		);
		this.drawPinGrid(7, 2, 5, 1, -2);
		C.drawRect(this.canvasCtx, -2, 5, 4, 2, '#37623a');
		this.drawInnerCatches(INNER_R);
		this.canvasCtx.restore();
	}
	drawAudioJack(x, y) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y);
		const OUTER_R = 7;
		const INNER_R = 3;
		C.drawCirc(
			this.canvasCtx,
			0, 0, OUTER_R, null, '#998872', 7
		);
		C.drawCirc(
			this.canvasCtx,
			0, 0, OUTER_R, null, '#1c1202', 2
		);
		C.drawCirc(
			this.canvasCtx,
			0, 0, OUTER_R, '#f78b98'
		);
		C.drawCirc(
			this.canvasCtx,
			0, 0, 4.5, '#fdf8db'
		);
		C.drawCirc(
			this.canvasCtx,
			0, 0, INNER_R, '#1c1202'
		);
		this.canvasCtx.restore();
	}
	drawUSBSymbol(x, y) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y);
		this.canvasCtx.scale(0.8, 0.8);
		C.drawCirc(
			this.canvasCtx,
			-10, 0, 2.5, '#1d1411'
		);

		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(-10, 0);
		this.canvasCtx.lineTo(10, 0);
		C.doStroke(this.canvasCtx, '#1d1411');
		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(10, -1.5);
		this.canvasCtx.lineTo(10, 1.5);
		this.canvasCtx.lineTo(13, 0);
		this.canvasCtx.closePath();
		C.doFill(this.canvasCtx, '#1d1411');

		this.canvasCtx.moveTo(-6, 0);
		this.canvasCtx.lineTo(-3, -4);
		this.canvasCtx.lineTo(3, -4);
		C.doStroke(this.canvasCtx, '#1d1411');
		C.drawCirc(
			this.canvasCtx,
			3, -4, 1, '#1d1411'
		);

		this.canvasCtx.moveTo(-2, 0);
		this.canvasCtx.lineTo(2, 4);
		this.canvasCtx.lineTo(5, 4);
		C.doStroke(this.canvasCtx, '#1d1411');
		C.fillRect(
			this.canvasCtx,
			5, 4-1.5, 2, 2
		);

		this.canvasCtx.restore();
	}
	drawUSB(x, y) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y-5);
		const WIDTH = 35;
		const HEIGHT = 12;
		const OFFSET = 2;
		C.strokeRect(
			this.canvasCtx,
			-WIDTH/2, -HEIGHT/2, WIDTH, HEIGHT,
			'#1d1411', 5
		);
		C.strokeRect(
			this.canvasCtx,
			-WIDTH/2, -HEIGHT/2, WIDTH, HEIGHT,
			'#dfd9cd', 2
		);
		C.drawRect(
			this.canvasCtx,
			-WIDTH/2, -HEIGHT/2, WIDTH, HEIGHT,
			'#3d4a5a'
		);
		C.drawRect(
			this.canvasCtx,
			-WIDTH/2+OFFSET, -HEIGHT/2+OFFSET,
			WIDTH-2*OFFSET, HEIGHT/3,
			'#92a5f0'
		);
		this.drawUSBSymbol(0, HEIGHT/2 + 10);
		this.canvasCtx.restore();
	}
	drawParallelPort(x, y) {
		this.canvasCtx.save();
		this.canvasCtx.translate(x, y);
		const WIDTH = 75;
		const HEIGHT = 18;
		const R = HEIGHT/4;
		this.canvasCtx.beginPath();
		this.canvasCtx.moveTo(0, HEIGHT/2);
		this.canvasCtx.arc(-WIDTH/2+R, R, R, Math.PI/2, Math.PI*3/4);
		this.canvasCtx.arc(-WIDTH/2-R, -R, R, Math.PI*3/4, Math.PI*3/2);
		this.canvasCtx.arc(WIDTH/2+R, -R, R, Math.PI*3/2, Math.PI*1/4);
		this.canvasCtx.arc(WIDTH/2-R, R, R, Math.PI*1/4, Math.PI*1/2);
		this.canvasCtx.closePath();
		C.doStroke(this.canvasCtx, '#b6b2ac', 15);
		C.doStroke(this.canvasCtx, '#dfd9cd', 9);
		C.doStroke(this.canvasCtx, '#7c6c64', 6);
		C.doFill(this.canvasCtx, '#ac3667');
		this.drawPinGrid(25, 3, -7, 2);
		this.canvasCtx.restore();
	}
	draw(active) {
		G.begin(this);

		// 0 to 4 ports
		switch (this.game.ports.numPerFace[this.index]) {
		case 0:
			break;
		case 1:
			this.drawParallelPort(this.rect.w/2*1, this.rect.h/2);
			break;
		case 2:
			this.drawUSB(this.rect.w/6*1 - 3, this.rect.h/2);
			this.drawParallelPort(this.rect.w/6*4 + 3, this.rect.h/2);
			break;
		case 3:
			this.drawPS2(this.rect.w/6*1, this.rect.h/2);
			this.drawUSB(this.rect.w/6*3, this.rect.h/2);
			this.drawSVideo(this.rect.w/6*5, this.rect.h/2);
			break;
		case 4:
			this.drawRJ45(this.rect.w/8*1, this.rect.h/2);
			this.drawSVideo(this.rect.w/8*3 + 5, this.rect.h/2);
			this.drawAudioJack(this.rect.w/8*5 + 3, this.rect.h/2);
			this.drawPS2(this.rect.w/8*7, this.rect.h/2);
			break;
		}

		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtanePortsGraphics };
