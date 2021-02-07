import { KtaneGraphicsParams } from './graphics_params.js';

class CanvasUtils {
	static invPoint(canvasCtx, x, y) {
		return canvasCtx.getTransform().inverse().transformPoint(new DOMPoint(x, y));
	}
	static doFill(canvasCtx, fill=null, color=null, offsetX=0, offsetY=0, blur=0) {
		if (fill != null) {
			canvasCtx.fillStyle = fill;
			if (color != null && CanvasUtils.shadowsEnabled) {
				canvasCtx.shadowColor = color;
				canvasCtx.shadowOffsetX = offsetX;
				canvasCtx.shadowOffsetY = offsetY;
				canvasCtx.shadowBlur = blur;
			}
			canvasCtx.fill();
		}
	}
	static doStroke(canvasCtx, stroke=null, lineWidth=null, color=null, offsetX=0, offsetY=0, blur=0) {
		if (stroke != null) {
			canvasCtx.lineWidth = lineWidth;
			canvasCtx.strokeStyle = stroke;
			if (color != null && CanvasUtils.shadowsEnabled) {
				canvasCtx.shadowColor = color;
				canvasCtx.shadowOffsetX = offsetX;
				canvasCtx.shadowOffsetY = offsetY;
				canvasCtx.shadowBlur = blur;
			}
			canvasCtx.stroke();
		}
	}
	static doShadow(canvasCtx, fill=null, shadows=[]) {
		shadows.forEach(([color, offsetX, offsetY, blur]) => {
			CanvasUtils.doFill(canvasCtx, fill, color, offsetX, offsetY, blur);
		});
	}
	static doInset(canvasCtx, stroke=null, insets=[]) {
		insets.forEach(([color, offsetX, offsetY, blur]) => {
			CanvasUtils.doStroke(canvasCtx, stroke, 0, offsetX, offsetY, blur);
		});
	}
	static insetCirc(canvasCtx, x, y, r, stroke=null, color=null, offsetX=0, offsetY=0, blur=0) {
		canvasCtx.save();
		canvasCtx.beginPath();
		canvasCtx.arc(x, y, r + 1, 0, 2 * Math.PI);
		canvasCtx.clip();
		CanvasUtils.doStroke(canvasCtx, stroke, 0, color, offsetX, offsetY, blur);
		canvasCtx.restore();
	}
	static drawCirc(canvasCtx, x, y, r, fill=null, stroke=null, lineWidth=1, shadows=KtaneGraphicsParams.NO_SHADOW, insets=[]) {
		canvasCtx.save();
		canvasCtx.beginPath();
		canvasCtx.arc(x, y, r, 0, 2 * Math.PI);
		shadows.forEach(([color, offsetX, offsetY, blur]) => {
			CanvasUtils.doFill(canvasCtx, fill, color, offsetX, offsetY, blur);
		});
		CanvasUtils.doStroke(canvasCtx, stroke, lineWidth);
		canvasCtx.restore();
		insets.forEach(([color, offsetX, offsetY, blur]) => {
			CanvasUtils.insetCirc(canvasCtx, x, y, r, fill, color, offsetX, offsetY, blur);
		});
	}
	static insetRect(canvasCtx, x, y, w, h, stroke=null, color=null, offsetX=0, offsetY=0, blur=0) {
		canvasCtx.save();
		canvasCtx.beginPath();
		canvasCtx.rect(x - 1, y - 1, w + 2, h + 2);
		canvasCtx.clip();
		CanvasUtils.doStroke(canvasCtx, stroke, 0, color, offsetX, offsetY, blur);
		canvasCtx.restore();
	}
	static drawRect(canvasCtx, x, y, w, h, fill=null, stroke=null, lineWidth=1, shadows=KtaneGraphicsParams.NO_SHADOW, insets=[]) {
		canvasCtx.save();
		canvasCtx.beginPath();
		canvasCtx.rect(x, y, w, h);
		shadows.forEach(([color, offsetX, offsetY, blur]) => {
			CanvasUtils.doFill(canvasCtx, fill, color, offsetX, offsetY, blur);
		});
		CanvasUtils.doStroke(canvasCtx, stroke, lineWidth);
		canvasCtx.restore();
		insets.forEach(([color, offsetX, offsetY, blur]) => {
			CanvasUtils.insetRect(canvasCtx, x, y, w, h, fill, color, offsetX, offsetY, blur);
		});
	}
	static fillRect(canvasCtx, x, y, w, h, fill='#000000') {
		CanvasUtils.drawRect(
			canvasCtx,
			x, y, w, h,
			fill
		);
	}
	static strokeRect(canvasCtx, x, y, w, h, stroke='#000000', lineWidth=1) {
		CanvasUtils.drawRect(
			canvasCtx,
			x, y, w, h,
			null, stroke, lineWidth
		);
	}
	static strokeLine(canvasCtx, x1, y1, x2, y2, stroke='#000000', lineWidth=1) {
		canvasCtx.save();
		canvasCtx.beginPath();
		canvasCtx.moveTo(x1, y1);
		canvasCtx.lineTo(x2, y2);
		CanvasUtils.doStroke(canvasCtx, stroke, lineWidth);
	}
	static drawText(canvasCtx, value, x, y, align='center', baseline='middle', fontSize=10, fontFace=KtaneGraphicsParams.UI_FONT, modifier='', fill='#000000', glow=null, blur=0) {
		canvasCtx.font = `${modifier} ${fontSize}px ${fontFace}`;
		canvasCtx.textAlign = align;
		canvasCtx.textBaseline = baseline;
		canvasCtx.fillStyle = fill;
		if (glow !== null && CanvasUtils.shadowsEnabled) {
			canvasCtx.save();
			canvasCtx.shadowColor = glow;
			canvasCtx.shadowBlur = blur;
			canvasCtx.fillText(value, x, y);
			canvasCtx.restore();
		} else {
			canvasCtx.fillText(value, x, y);
		}
	}
	static toRgb(str) {
		return [
			parseInt(str.slice(1, 3), 16) / 255,
			parseInt(str.slice(3, 5), 16) / 255,
			parseInt(str.slice(5, 7), 16) / 255
		];
	}
	static makeRgbaString(r, g, b, a) {
		const rc = Math.min(Math.max(r * 256, 0), 255);
		const gc = Math.min(Math.max(g * 256, 0), 255);
		const bc = Math.min(Math.max(b * 256, 0), 255);
		const ac = Math.min(Math.max(a, 0), 1);
		return `rgb(${rc}, ${gc}, ${bc}, ${ac})`;
	}
	static interpolateRgba(r1, g1, b1, a1, r2, g2, b2, a2, t) {
		return CanvasUtils.makeRgbaString(
			r1 * (1 - t) + r2 * t,
			g1 * (1 - t) + g2 * t,
			b1 * (1 - t) + b2 * t,
			a1 * (1 - t) + a2 * t
		);
	}
	static makeHtmlImg(w, h, htmlDefs, htmlVal, callback) {
		const DOMURL = window.URL || window.webkitURL || window;
		const data = `
<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">
	<defs>
		${htmlDefs}
	</defs>
	<foreignObject width="100%" height="100%">
	<div xmlns="http://www.w3.org/1999/xhtml" id="wrapper">
		${htmlVal}
	</div>
	</foreignObject>
</svg>`;
		const img = new Image();
		const svg = new Blob([data], {
			type: 'image/svg+xml;charset=utf-8'
		});
		const reader = new FileReader();
		reader.readAsDataURL(svg);
		reader.onload = (e) => {
			const url = e.target.result;
			img.src = url;
		};
		img.onload = () => {
			callback(img);
		};
	}
	static isTainted(ctx) {
		try {
			const pixel = ctx.getImageData(0, 0, 1, 1);
			return false;
		} catch(err) {
			return (err.code === 18);
		}
	}
};
CanvasUtils.allowShadows = true;

export { CanvasUtils };
