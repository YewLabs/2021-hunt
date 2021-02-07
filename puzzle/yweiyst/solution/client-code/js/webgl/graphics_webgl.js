class WebglUtils {
	static getContext(canvas) {
		const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
		if (gl && gl instanceof WebGLRenderingContext) {
			return gl;
		}
		return null;
	}
	static getNearestPowerOfTwo(x) {
		for (let i = 0; ; i++) {
			if ((1 << i) >= x) {
				return (1 << i);
			}
		}
	}
	static createShader(gl, shaderType, src) {
		const shader = gl.createShader(shaderType);
		gl.shaderSource(shader, src);
		gl.compileShader(shader);
		if (gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
			return shader;
		}
		console.error(gl.getShaderInfoLog(shader));
		gl.deleteShader(shader);
		return null;
	}
	static createProgram(gl, vertShaderSrc, fragShaderSrc) {
		const vertShader = WebglUtils.createShader(gl, gl.VERTEX_SHADER, vertShaderSrc);
		const fragShader = WebglUtils.createShader(gl, gl.FRAGMENT_SHADER, fragShaderSrc);
		const program = gl.createProgram();
		gl.attachShader(program, vertShader);
		gl.attachShader(program, fragShader);
		gl.linkProgram(program);
		if (gl.getProgramParameter(program, gl.LINK_STATUS)) {
			return program;
		}
		console.error(gl.getProgramInfoLog(program));
		gl.deleteProgram(program);
	}
};

export { WebglUtils };
