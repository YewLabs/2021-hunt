import { CardinalDirection, CubeFace, Matrix3x3 } from './geom.js';
import { KtaneSync } from './modules/sync.js';
import { KtaneClick } from './input.js';
import { KtaneRotationManager } from './rotation.js';
import { KtaneGameGeom } from './game_geom.js';
import { KtaneTimer } from './modules/timer.js';
import { KtaneManual } from './modules/manual.js';
import { KtaneShakeIt } from './modules/shake_it.js';
import { KtaneWhosOnFirst } from './modules/whos_on_first.js';
import { KtaneSix } from './modules/six.js';
import { KtaneWires } from './modules/wires.js';
import { KtaneMaze } from './modules/maze.js';
import { KtaneSimon } from './modules/simon.js';
import { KtaneGravity } from './modules/gravity.js';
import { KtaneCube } from './modules/cube.js';
import { KtaneButtons } from './modules/buttons.js';
import { KtanePasswords } from './modules/passwords.js';
import { KtaneSerialNumber, KtaneDateOfManufacture, KtaneBatteries, KtanePorts } from './modules/indicators.js';
import { CanvasUtils as C } from './graphics_canvas.js';

// TODO: make sure this is false eventually
const AUTOSTART = false;
const AUTOROTATE = false;
const AUTORESTART = false;

class KtaneGamePhase {
};
KtaneGamePhase.LOBBY = 0;
KtaneGamePhase.RUNNING = 1;
KtaneGamePhase.STOPPED = 2;

class KtaneGame {
	constructor(wsSend) {
		this.wsSend = wsSend;

		this.phase = KtaneGamePhase.LOBBY;
		this.playerSlotFilled = 0; // bitmask
		this.numSpectators = 0;
		this.playerSlot = null;
		this.isDefuser = false;
		this.rotManager = new KtaneRotationManager();
		this.moduleSlots = null;
		this.lastServerUpdate = null;
		this.lastNumStrikes = 0;
		this.strikeReasons = [];
		this.timeLeft = null;
		this.winMessage = [];
		this.highScores = null;

		// Warning: add to this.modules every time we make a new module
		this.timer = new KtaneTimer(this);
		this.manual = new KtaneManual(this);
		this.shakeIt = new KtaneShakeIt(this);
		this.whosOnFirst0 = new KtaneWhosOnFirst(this);
		this.whosOnFirst1 = new KtaneWhosOnFirst(this);
		this.six = new KtaneSix(this);
		this.wires = new KtaneWires(this);
		this.maze = new KtaneMaze(this);
		this.simon = new KtaneSimon(this);
		this.gravity = new KtaneGravity(this);
		this.cube = new KtaneCube(this);
		this.buttons = new KtaneButtons(this);
		this.passwords = new KtanePasswords(this);
		this.serial = new KtaneSerialNumber(this);
		this.date = new KtaneDateOfManufacture(this);
		this.batteries = new KtaneBatteries(this);
		this.ports = new KtanePorts(this);
		this.modules = [
			this.timer,
			this.manual,
			this.shakeIt,
			this.whosOnFirst0,
			this.whosOnFirst1,
			this.six,
			this.wires,
			this.maze,
			this.simon,
			this.gravity,
			this.cube,
			this.buttons,
			this.passwords,
			this.serial,
			this.date,
			this.batteries,
			this.ports,
		];

		// global graphics state
		this.mouseX = 0;
		this.mouseY = 0;
		this.topmostHover = null;
		this.activeClick = null;
		this.useOldOrientation = false;
		this.debugSeed = null;

		this.debugText = '';
		window.game = this;
		this.debugMode = false;

		this.audioBeep = document.getElementById('beep');
		this.audioStrike = document.getElementById('strike');
		this.audioWin = document.getElementById('win');
		this.playingStrike = false;
		this.lastTimeSinceStrike = null;

		const getStorage = (s) => JSON.parse(window.localStorage.getItem(s));
		this.muted = getStorage('ktaneMuted') ?? false;
		this.volume = getStorage('ktaneVolume') ?? 1;
		this.updateVolume();
		this.updateInvertedControls(getStorage('ktaneInverted') ?? false);
		this.updateWebglEnabled(getStorage('ktaneWebgl') ?? true);
		this.updateShadowsEnabled(getStorage('ktaneShadows') ?? true);
		this.updateSpectatorMode(getStorage('ktaneSpectate') ?? false);

		const urlParams = new URLSearchParams(window.location.search);
		this.godToken = urlParams.get('god');
		if (this.godToken != null) {
			this.updateSpectatorMode(true);
		}
	}
	updateVolume() {
		const mutedVolume = this.muted ? 0 : this.volume;
		this.audioBeep.volume = 0.5 * mutedVolume;
		this.audioStrike.volume = 0.1 * mutedVolume;
		this.audioWin.volume = 1.0 * mutedVolume;
		localStorage.setItem('ktaneMuted', JSON.stringify(this.muted));
		localStorage.setItem('ktaneVolume', JSON.stringify(this.volume));
	}
	updateInvertedControls(newVal) {
		this.invertedControls = newVal;
		localStorage.setItem('ktaneInverted', JSON.stringify(newVal));
	}
	updateWebglEnabled(newVal) {
		this.webglEnabled = newVal;
		localStorage.setItem('ktaneWebgl', JSON.stringify(newVal));
	}
	updateShadowsEnabled(newVal) {
		this.shadowsEnabled = newVal;
		C.shadowsEnabled = newVal;
		localStorage.setItem('ktaneShadows', JSON.stringify(newVal));
	}
	updateSpectatorMode(newVal) {
		this.spectatorMode = newVal;
		localStorage.setItem('ktaneSpectate', JSON.stringify(newVal));
		this.requestJoin();
	}
	getTimeSinceStrike() {
		return KtaneSync.getTimerVal(
			this.lastServerUpdate,
			this.lastTimeSinceStrike
		);
	}
	isReadyToStart() {
		return this.playerSlot != null;
	}
	getViewMatrix() {
		return this.useOldOrientation ? this.rotManager.getTweenFrom() : this.rotManager.getTweenTo();
	}
	getPlayerRot() {
		return KtaneGameGeom.getPlayerRot(
			this.getViewMatrix(), this.playerSlot
		);
	}
	updateRot(viewMatrix, serverTxn) {
		if (this.phase != KtaneGamePhase.RUNNING) {
			this.phase = KtaneGamePhase.RUNNING;
		}
		this.rotManager.doServerRotate(viewMatrix, serverTxn);
		for (const module of this.modules) {
			module.reset(false);
		}
	}
	updateModuleSlots(moduleSlots) {
		this.moduleSlots = moduleSlots;
		for (const module of this.modules) {
			module.reset(true);
			this.rotManager.reset();
			this.lastServerUpdate = null;
			this.lastNumStrikes = 0;
		}

		if (AUTOROTATE) {
			// go to manual
			// this.requestRotate(CardinalDirection.N);

			// go to left face
			this.requestRotate(CardinalDirection.E);
		}
	}
	updateModules(moduleUpdates) {
		for (const moduleUpdate of moduleUpdates) {
			const moduleUpdateFuncs = {
				'timer': this.timer.serverUpdate.bind(this.timer),
				'manual': this.manual.serverUpdate.bind(this.manual),
				'shakeit': this.shakeIt.serverUpdate.bind(this.shakeIt),
				'whosonfirst0': this.whosOnFirst0.serverUpdate.bind(this.whosOnFirst0),
				'whosonfirst1': this.whosOnFirst1.serverUpdate.bind(this.whosOnFirst1),
				'six': this.six.serverUpdate.bind(this.six),
				'wires': this.wires.serverUpdate.bind(this.wires),
				'maze': this.maze.serverUpdate.bind(this.maze),
				'simon': this.simon.serverUpdate.bind(this.simon),
				'gravity': this.gravity.serverUpdate.bind(this.gravity),
				'cube': this.cube.serverUpdate.bind(this.cube),
				'buttons': this.buttons.serverUpdate.bind(this.buttons),
				'passwords': this.passwords.serverUpdate.bind(this.passwords),
				'serial': this.serial.serverUpdate.bind(this.serial),
				'date': this.date.serverUpdate.bind(this.date),
				'batteries': this.batteries.serverUpdate.bind(this.batteries),
				'ports': this.ports.serverUpdate.bind(this.ports),
			};
			const moduleName = moduleUpdate['module'];
			if (!(moduleName in moduleUpdateFuncs)) {
				continue;
			}
			moduleUpdateFuncs[moduleName](moduleUpdate);
		}
	}
	updateState(msg) {
		if ('moduleSlots' in msg) {
			this.updateModuleSlots(msg['moduleSlots']);
			this.debugSeed = msg['debugSeed'];
			// always output this so people have something
			// to report with
			console.log(`seed: ${this.debugSeed}`);
		}
		if ('viewMatrix' in msg) {
			this.updateRot(
				Matrix3x3.fromDict(msg['viewMatrix']),
				msg['rotateTxn']
			);
		}
		if ('moduleUpdates' in msg) {
			this.updateModules(msg['moduleUpdates']);
		}
		if ('timeSinceStrike' in msg) {
			this.lastServerUpdate = performance.now();

			const currNumStrikes = this.timer.numStrikes;
			if (currNumStrikes > this.lastNumStrikes) {
				this.audioStrike.currentTime = 0;
				this.audioStrike.play().catch((e)=>{});
				this.lastNumStrikes = currNumStrikes;
			}

			this.lastTimeSinceStrike = msg['timeSinceStrike'];
		}
	}
	stop(msg=null) {
		if (this.phase == KtaneGamePhase.RUNNING) {
			if (msg == null || !('timeLeft' in msg)) {
				this.strikeReasons = [];
				this.timeLeft = null;
				this.winMessage = [];
			}
			else {
				this.strikeReasons = msg['strikeReasons'];
				this.timeLeft = msg['timeLeft'];
				this.winMessage = msg['winMessage'];
				if (this.winMessage.length != 0) {
					this.audioWin.play().catch((e)=>{});
				}
			}
			this.phase = KtaneGamePhase.STOPPED;
		}
		this.playerSlot = null;
		this.requestJoin();
		if (AUTORESTART) {
			this.restart();
		}
	}
	restart() {
		this.phase = KtaneGamePhase.LOBBY;
	}
	getActiveFace() {
		const viewMat = this.getViewMatrix();
		return KtaneGameGeom.getActiveFace(viewMat, this.playerSlot);
	}
	getActiveSubmodule(prefix) {
		const faceModules = this.moduleSlots[this.getActiveFace()];
		for (const module of faceModules) {
			if (module.startsWith(prefix)) {
				return module;
			}
		}
		return `${prefix}-0`;
	}
	updatePlayerCounts(playerSlotFilled, numSpectators) {
		this.playerSlotFilled = playerSlotFilled;
		this.numSpectators = numSpectators;
	}
	updatePlayerSlot(playerSlot, isDefuser, debugSeed=null) {
		this.playerSlot = playerSlot;
		this.isDefuser = isDefuser;
		this.debugSeed = debugSeed;

		if (AUTOSTART) {
			this.requestStart();
		}
	}
	requestJoin() {
		const msg = {
			'type': 'join',
			'spectate': this.spectatorMode,
		};
		if (this.godToken != null) {
			msg['god'] = this.godToken;
		}
		this.wsSend(msg);
	}
	requestStart() {
		this.wsSend({
			'type': 'start'
		});
	}
	requestRotate(rotDir) {
		this.wsSend({
			'type': 'rotate',
			'rotDir': rotDir,
			'rotateTxn': this.rotManager.serverTxn
		});
	}
	updateClick() {
		if (this.topmostHover == null) {
			return;
		}
		const clickData = this.topmostHover;
		this.activeClick = clickData;
		switch (clickData.type) {
		case KtaneClick.CLEAR_STATE_BUTTON:
			this.wsSend({
				'type': 'clearState'
			});
			break;
		case KtaneClick.START_BUTTON:
			this.requestStart();
			break;
		case KtaneClick.STOP_BUTTON:
			this.wsSend({
				'type': 'stop'
			});
			break;
		case KtaneClick.RELOAD_BUTTON:
			this.wsSend({
				'type': 'stop'
			});
			this.wsSend({
				'type': 'reload'
			});
			break;
		case KtaneClick.ROTATE_BUTTON:
			if (this.rotManager.isRotating()) {
				break;
			}
			let rotDir = clickData.index;
			if (this.invertedControls) {
				rotDir = CardinalDirection.getOpposite(rotDir);
			}
			const viewMatrix = this.rotManager.getTweenTo();
			const rotFace = KtaneGameGeom.playerDirToRotFace(viewMatrix, this.playerSlot, rotDir);
			const newViewMatrix = KtaneGameGeom.rotByFace(viewMatrix, rotFace)
			this.rotManager.doClientRotate(newViewMatrix);
			this.requestRotate(rotDir);
			break;
		case KtaneClick.RESTART_BUTTON:
			this.restart();
			break;
		case KtaneClick.MUTE_BUTTON:
			this.muted = !this.muted;
			this.updateVolume();
			break;
		case KtaneClick.INVERTED_CONTROLS_TOGGLE:
			this.updateInvertedControls(!this.invertedControls);
			break;
		case KtaneClick.WEBGL_ENABLED_TOGGLE:
			this.updateWebglEnabled(!this.webglEnabled);
			break;
		case KtaneClick.SHADOWS_ENABLED_TOGGLE:
			this.updateShadowsEnabled(!this.shadowsEnabled);
			break;
		case KtaneClick.SPECTATOR_MODE_TOGGLE:
			this.updateSpectatorMode(!this.spectatorMode);
			break;
		}
		if (clickData.callback != null) {
			clickData.callback();
		}
	}
	update(elapsed) {
		this.rotManager.update(elapsed);
		if (this.phase == KtaneGamePhase.RUNNING) {
			if (this.timer.updateBeep()) {
				this.audioBeep.currentTime = 0;
				this.audioBeep.play().catch((e)=>{});
			}
		}
	}
	sendModuleInput(moduleName, data) {
		this.wsSend({
			'type': 'moduleInput',
			'module': moduleName,
			'rotateTxn': this.rotManager.serverTxn,
			...data
		});
	}
};

export { KtaneGamePhase, KtaneGame };
