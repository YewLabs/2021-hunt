import { WebglUtils } from './graphics_webgl.js';
import { Vector4, Matrix4x4 } from './geom.js';
import { vertShaderSrc, fragShaderSrc } from './shaders.js';

class RotatingCubeGraphics {
	constructor(gl, frustrumScale) {
		this.gl = gl;
		this.initialized = false;
		this.frustrumScale = frustrumScale;

		this.faceTexture = null;
		this.shaderProgram = null;
		this.posBuf = null;
		this.texCoordBuf = null;
	}
	init(initFaceGraphics) {
		if (this.initialized) {
			return;
		}
		this.initialized = true;

		const gl = this.gl;
		this.faceTexture = gl.createTexture();
		this.shaderProgram = WebglUtils.createProgram(gl, vertShaderSrc, fragShaderSrc);
		this.posBuf = gl.createBuffer();
		gl.bindBuffer(gl.ARRAY_BUFFER, this.posBuf);
		const frontFaceQuad = [
			-1, 1, 1,
			-1, -1, 1,
			1, 1, 1,
			1, -1, 1,
		];
		gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(frontFaceQuad), gl.STATIC_DRAW);
		this.texCoordBuf = gl.createBuffer();
		gl.bindBuffer(gl.ARRAY_BUFFER, this.texCoordBuf);
		const wFrac = initFaceGraphics.rect.w / initFaceGraphics.canvasCtx.canvas.width;
		const hFrac = initFaceGraphics.rect.h / initFaceGraphics.canvasCtx.canvas.height;
		const texQuad = [
			0, 0,
			0, hFrac,
			wFrac, 0,
			wFrac, hFrac,
		];
		gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(texQuad), gl.STATIC_DRAW);

		gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
		gl.bindTexture(gl.TEXTURE_2D, this.faceTexture);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
		gl.texImage2D(
			gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE,
			initFaceGraphics.canvasCtx.canvas
		);
	}
	start() {
		const gl = this.gl;
		gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
		gl.clear(gl.COLOR_BUFFER_BIT);
		gl.useProgram(this.shaderProgram);
	}
	drawFace(faceCanvas, xrot, yrot, zrot) {
		const gl = this.gl;
		const texLocation = gl.getUniformLocation(this.shaderProgram, 'u_texture');
		const vmatLocation = gl.getUniformLocation(this.shaderProgram, 'u_vmatrix');
		gl.activeTexture(gl.TEXTURE0);
		gl.bindTexture(gl.TEXTURE_2D, this.faceTexture);
		gl.uniform1i(texLocation, 0);
		gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, gl.RGBA, gl.UNSIGNED_BYTE, faceCanvas);
		const frustrumScale = this.frustrumScale;

		let vmat = Matrix4x4.IDENTITY;
		vmat = vmat.leftMult(Matrix4x4.rotateX(xrot * Math.PI / 2));
		vmat = vmat.leftMult(Matrix4x4.rotateY(yrot * Math.PI / 2));
		vmat = vmat.leftMult(Matrix4x4.rotateZ(zrot * Math.PI / 2));
		vmat = vmat.leftMult(Matrix4x4.translateZ(-1 - 5));
		vmat = vmat.leftMult(Matrix4x4.perspective(5, 10, frustrumScale));
		vmat = vmat.leftMult(Matrix4x4.removeZ());
		gl.uniformMatrix4fv(vmatLocation, false, vmat.getTranspose().toArray());

		const posLocation = gl.getAttribLocation(this.shaderProgram, 'a_position');
		const texCoordLocation = gl.getAttribLocation(this.shaderProgram, 'a_texcoord');
		gl.bindBuffer(gl.ARRAY_BUFFER, this.posBuf);
		gl.enableVertexAttribArray(posLocation);
		gl.vertexAttribPointer(posLocation, 3, gl.FLOAT, false, 0, 0);
		gl.bindBuffer(gl.ARRAY_BUFFER, this.texCoordBuf);
		gl.enableVertexAttribArray(texCoordLocation);
		gl.vertexAttribPointer(texCoordLocation, 2, gl.FLOAT, false, 0, 0);

		gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
	}
};

export { RotatingCubeGraphics };
