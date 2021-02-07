import { KtaneGamePhase } from './game.js';
import { Rect, CubeFace } from './geom.js';
import { KtaneClick } from './input.js';
import { KtaneLobbyGraphics } from './graphics_lobby.js';
import { KtaneGameGraphics } from './graphics_game.js';
import { KtaneStoppedGraphics } from './graphics_stopped.js';
import { CanvasUtils as C } from './graphics_canvas.js';
import { KtaneGraphicsControl as G } from './graphics_control.js';
import { KtaneGraphicsParams } from './graphics_params.js';
import { MuteButton, Slider, Toggle } from './graphics_components.js';

class KtaneGraphics {
	constructor(canvasCtx, game) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.prevFrameTime = performance.now();

		this.rect = new Rect(
			0, 0,
			this.canvasCtx.canvas.clientWidth,
			this.canvasCtx.canvas.clientHeight
		);

		this.lobbyGraphics = new KtaneLobbyGraphics(
			canvasCtx, game,
			new Rect(0, 0, this.rect.w, this.rect.h)
		);
		this.gameGraphics = new KtaneGameGraphics(
			canvasCtx, game,
			new Rect(0, 0, this.rect.w, this.rect.h)
		);
		this.stoppedGraphics = new KtaneStoppedGraphics(
			canvasCtx, game,
			new Rect(0, 0, this.rect.w, this.rect.h)
		);
		const webglSupported = this.gameGraphics.cubeGraphics.scratch3dCtx != null;

		this.muteButton = new MuteButton(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.MUTE_BUTTON),
			20, 20, 13, 7,
			KtaneGraphicsParams.DULL_BUTTON_COLOR,
			KtaneGraphicsParams.DULL_BUTTON_PRESSED_COLOR,
			KtaneGraphicsParams.DULL_BUTTON_HOVER_COLOR
		);
		this.volumeSlider = new Slider(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.VOLUME_SLIDER),
			55, 11, 20, 100,
			KtaneGraphicsParams.DULL_BUTTON_COLOR
		);
		const togglesX = 15;
		const togglesY = 50;
		const togglesSpacing = 18;
		this.invertedControlsToggle = new Toggle(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.INVERTED_CONTROLS_TOGGLE),
			togglesX, togglesY + togglesSpacing*0, 16, 8,
			'Inverted rotation'
		);
		this.webglEnabledToggle = new Toggle(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.WEBGL_ENABLED_TOGGLE),
			togglesX, togglesY + togglesSpacing*1, 16, 8,
			'3D rotation'
		);
		this.shadowsEnabledToggle = new Toggle(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.SHADOWS_ENABLED_TOGGLE),
			togglesX, togglesY + togglesSpacing*2, 16, 8,
			'Fancy graphics'
		);
		this.spectatorModeToggle = new Toggle(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.SPECTATOR_MODE_TOGGLE),
			togglesX, togglesY + togglesSpacing*3, 16, 8,
			'Always spectating'
		);

		this.clickables = [
			this.muteButton,
			this.volumeSlider,
			this.invertedControlsToggle,
			this.shadowsEnabledToggle,
			this.spectatorModeToggle,
		];
		if (webglSupported) {
			this.clickables.push(this.webglEnabledToggle);
		}
	}
	updateMouse() {
		let bestClick = null;
		switch (this.game.phase) {
		case KtaneGamePhase.LOBBY:
			bestClick = this.lobbyGraphics.updateMouse();
			break;
		case KtaneGamePhase.RUNNING:
			bestClick = this.gameGraphics.updateMouse();
			break;
		case KtaneGamePhase.STOPPED:
			bestClick = this.stoppedGraphics.updateMouse();
			break;
		default:
			console.error(`unknown game phase ${this.game.phase.toString()}`);
			break;
		}
		bestClick = G.updateClick(
			bestClick,
			G.updateMouseClickables(this)
		);
		this.game.topmostHover = bestClick;
	}
	getBackgroundOverlayColor() {
		const strikePulseProgress = G.timerToProgress(
			this.game.getTimeSinceStrike(), KtaneGraphicsParams.STRIKE_PULSE
		);
		const color = KtaneGraphicsParams.BACKGROUND_STRIKE_COLOR;
		return C.interpolateRgba(
			color[0], color[1], color[2], 1,
			0, 0, 0, 1,
			strikePulseProgress
		);
	}
	drawHighScores() {
		if (this.game.highScores == null) {
			return;
		}

		const SCORES_W = 250;
		const SCORES_H = 350;
		const SCORES_X = 10;
		const SCORES_Y = 250;
		const SCORE_COL_W = 25;
		const ROW_H = 18;
		const MAX_NUM_ROWS = 10;
		const numRows = Math.min(this.game.highScores.length, MAX_NUM_ROWS);

		C.drawText(
			this.canvasCtx,
			'High scores',
			SCORES_X, SCORES_Y - 10,
			'left', 'bottom', 16,
			KtaneGraphicsParams.UI_FONT, '',
			'#FFFFFF'
		);

		this.canvasCtx.save();
		const scoresClip = new Path2D();
		scoresClip.rect(SCORES_X, SCORES_Y, SCORES_W, SCORES_H);
		this.canvasCtx.clip(scoresClip);

		for (let i = 0; i < numRows; i++) {
			const row = this.game.highScores[i];
			const name = row[0];
			const score = row[1];
			C.drawText(
				this.canvasCtx,
				G.timeDeltaAsString(score),
				SCORES_X + SCORE_COL_W,
				SCORES_Y + i * ROW_H,
				'right', 'top', 12,
				KtaneGraphicsParams.UI_FONT, '',
				'#FFFFFF'
			);
			C.drawText(
				this.canvasCtx,
				name,
				SCORES_X + SCORE_COL_W + 10,
				SCORES_Y + i * ROW_H,
				'left', 'top', 12,
				KtaneGraphicsParams.UI_FONT, '',
				'#FFFFFF'
			);
		}
		this.canvasCtx.restore();
	}
	draw(currFrameTime) {
		document.body.style.background = this.getBackgroundOverlayColor();

		G.begin(this);
		
		this.game.debugText = currFrameTime;
		this.canvasCtx.clearRect(0, 0, this.rect.w, this.rect.h);

		this.updateMouse();

		const active = true;
		switch (this.game.phase) {
		case KtaneGamePhase.LOBBY:
			this.lobbyGraphics.draw(active);
			this.drawHighScores();
			break;
		case KtaneGamePhase.RUNNING:
			this.gameGraphics.draw(active);
			break;
		case KtaneGamePhase.STOPPED:
			this.stoppedGraphics.draw(active);
			if (this.game.winMessage.length > 0) {
				this.drawHighScores();
			}
			break;
		default:
			console.error(`unknown game phase ${this.game.phase.toString()}`);
		}

		this.canvasCtx.canvas.style.cursor =
			(this.game.topmostHover != null) ? 'pointer' : 'default';

		this.prevFrameTime = currFrameTime;

		this.volumeSlider.updateThumb();
		if (this.volumeSlider.isPressed()) {
			this.game.volume = 1 - this.volumeSlider.value;
			this.game.muted = this.game.volume === 0;
			this.game.updateVolume();
		}
		else {
			this.volumeSlider.value = this.game.muted ? 1 : (1 - this.game.volume);
		}

		this.muteButton.muted = this.game.muted;

		this.invertedControlsToggle.value = this.game.invertedControls;
		this.webglEnabledToggle.value = this.game.webglEnabled;
		this.shadowsEnabledToggle.value = this.game.shadowsEnabled;
		this.spectatorModeToggle.value = this.game.spectatorMode;

		G.drawClickables(this, true);

		if (this.game.debugMode) {
			C.drawText(
				this.canvasCtx,
				`${this.game.debugText}`,
				this.rect.w - 10,
				10,
				'right', 'top',
				10, KtaneGraphicsParams.UI_FONT,
				'', '#ffffff'
			);
			if (this.game.debugSeed != null) {
				C.drawText(
					this.canvasCtx,
					`${this.game.debugSeed}`,
					this.rect.w - 10,
					24,
					'right', 'top',
					10, KtaneGraphicsParams.UI_FONT,
					'', '#ffffff'
				);
			}
		}

		G.end(this);
	}
};

export { KtaneGraphics };
