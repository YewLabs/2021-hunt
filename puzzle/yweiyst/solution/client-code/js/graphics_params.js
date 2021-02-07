import { CubeFace } from './geom.js';

class KtaneGraphicsParams {
};
// WARNING: this is bad, should be a dict
KtaneGraphicsParams.CUBE_FACE_NAMES = [
	'FRONT',
	'BACK',
	'LEFT',
	'RIGHT',
	'TOP',
	'BOTTOM'
];
KtaneGraphicsParams.CARDINAL_DIRECTION_NAMES = [
	'N', 'E', 'S', 'W'
];
KtaneGraphicsParams.ROOM_DIRECTION_NAMES = {
	[CubeFace.TOP]: 'CEILING',
	[CubeFace.BOTTOM]: 'GROUND',
	[CubeFace.LEFT]: 'WEST',
	[CubeFace.RIGHT]: 'EAST',
	[CubeFace.FRONT]: 'SOUTH',
	[CubeFace.BACK]: 'NORTH',
};
KtaneGraphicsParams.MANUAL_SECTION_NAMES = [
	'I', 'G', 'S', '6', 'T', 'W', 'B', 'P', 'C', 'D'
];

KtaneGraphicsParams.DANGER_BUTTON_COLOR = '#FF5555';
KtaneGraphicsParams.DANGER_BUTTON_HOVER_COLOR = '#FF7777';
KtaneGraphicsParams.DANGER_BUTTON_PRESSED_COLOR = '#992222';
KtaneGraphicsParams.SUCCESS_BUTTON_COLOR = '#55FF55';
KtaneGraphicsParams.SUCCESS_BUTTON_HOVER_COLOR = '#77FF77';
KtaneGraphicsParams.SUCCESS_BUTTON_PRESSED_COLOR = '#229922';
KtaneGraphicsParams.DEFAULT_BUTTON_COLOR = '#fdf2d6';
KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR = '#e3dbba';
KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR = '#b4ad9d';
KtaneGraphicsParams.DULL_BUTTON_COLOR = '#BBBBBB';
KtaneGraphicsParams.DULL_BUTTON_HOVER_COLOR = '#DDDDDD';
KtaneGraphicsParams.DULL_BUTTON_PRESSED_COLOR = '#999999';
KtaneGraphicsParams.SECONDARY_BUTTON_COLOR = '#cbb893';
KtaneGraphicsParams.SECONDARY_BUTTON_HOVER_COLOR = '#fdf2d6';
KtaneGraphicsParams.SECONDARY_BUTTON_PRESSED_COLOR = '#a39783';

KtaneGraphicsParams.GREEN_LED_OFF = '#005500';
KtaneGraphicsParams.GREEN_LED_ON = '#33EE33';
KtaneGraphicsParams.RED_LED_OFF = '#470000';
KtaneGraphicsParams.RED_LED_ON = '#d92736';

KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR = '#212121';
KtaneGraphicsParams.NO_SHADOW = [[null, null, null, null]];
KtaneGraphicsParams.SCREEN_INSET_SHADOW = [['#555', 0, -1, 8]];

KtaneGraphicsParams.SUBMODULE_SPACING = 7;
KtaneGraphicsParams.DISARMED_OFFSET = 20;
KtaneGraphicsParams.DISARMED_RADIUS = 10;
KtaneGraphicsParams.DISARMED_COLOR_OFF = KtaneGraphicsParams.GREEN_LED_OFF;
KtaneGraphicsParams.DISARMED_COLOR_ON = KtaneGraphicsParams.GREEN_LED_ON;
KtaneGraphicsParams.STRIKE_PULSE = 1000;
KtaneGraphicsParams.BACKGROUND_STRIKE_COLOR = [0.9, 0.5, 0.5];
KtaneGraphicsParams.MANUAL_FONT = 'Special Elite';
KtaneGraphicsParams.UI_FONT = 'Roboto Condensed';
KtaneGraphicsParams.TIMER_FONT = 'dseg7';

KtaneGraphicsParams.MODULE_BACKGROUND_COLOR = [0.64, 0.67, 0.70];
KtaneGraphicsParams.MODULE_STROKE_COLOR = '#738894';
KtaneGraphicsParams.MODULE_STROKE_WIDTH = 3;

KtaneGraphicsParams.PAPER_BACKGROUND_COLOR = '#f0f0f2';
KtaneGraphicsParams.PAPER_ACCENT_COLOR = '#8a150e';

KtaneGraphicsParams.GAME = {
};
KtaneGraphicsParams.STOPPED = {
	RESTART_BUTTON_WIDTH: 220,
	RESTART_BUTTON_HEIGHT: 60,
};
KtaneGraphicsParams.TIMER = {
	PANEL_HEIGHT_RATIO: 0.4,
	PANEL_WIDTH_RATIO: 0.9,
	TEXT_COLOR: '#FF0000',
	MAX_STRIKES: 3,
	STRIKE_COLOR_OFF: KtaneGraphicsParams.RED_LED_OFF,
	STRIKE_COLOR_ON: KtaneGraphicsParams.RED_LED_ON,
	STRIKE_SPACING: 35,
	STRIKE_RADIUS: 15,
	OFFSET_Y: 20,
	SPEED_BLINK_PERIOD: 1000, // ms
	TIMER_FONT: 'dddseg'
};
KtaneGraphicsParams.CUBE_CONTROL = {
	ROTATE_BUTTON_MARGIN: 10,
	ROTATE_BUTTON_WIDTH: 50,
	ROTATE_BUTTON_HEIGHT: 20,
};
KtaneGraphicsParams.FACE = {
	COLOR: '#b8dce1',
	STROKE: '#303c4c',
	STROKE_WIDTH: 5,
	BOTTOM_ROW_HEIGHT: 50,
	MODULE_SPACING: 15,
};
KtaneGraphicsParams.MANUAL_BUTTONS = {
};
KtaneGraphicsParams.MANUAL = {
	LANDSCAPE_PAGE_BUTTON_MARGIN: 17,
	LANDSCAPE_PAGE_BUTTON_WIDTH: 40,
	LANDSCAPE_PAGE_BUTTON_HEIGHT: 35,
	PORTRAIT_PAGE_BUTTON_WIDTH: 35,
	PORTRAIT_PAGE_BUTTON_HEIGHT: 33,
	PORTRAIT_PAGE_BUTTON_MARGIN: 7,
	MANUAL_PADDING: 9, // in px
};
KtaneGraphicsParams.SHAKE_IT = {
	COUNTER_WIDTH: 120,
	COUNTER_HEIGHT: 70,
};
KtaneGraphicsParams.WHOS_ON_FIRST = {
	CONSOLE_RATIO: 5/6,
	// warning: these must be synced with the server
	BUTTON_TEXTS: [
		'N', 'n', 'M', 'm'
	]
};
KtaneGraphicsParams.SIX = {
	LED_SPACING: 20,
	LED_COLOR_OFF: KtaneGraphicsParams.RED_LED_OFF,
	LED_COLOR_ON: KtaneGraphicsParams.RED_LED_ON,
	LED_RADIUS: 15,
};
KtaneGraphicsParams.WIRES = {
	NUM_WIRES: 5,
	NUM_SEGMENTS: 6,
	WIRES_MARGIN: 15,
	WIRE_THICKNESS: 15,
	WIRE_SPACING: 20,
	ATTACH_WIDTH: 20,
	ATTACH_COLOR: '#555555',
	COLORS: [
		'#f0f9f3',
		'#3a4faa',
		'#141416',
		'#f4df41',
		'#f0f9f3',
	],
	STRIPED_COLORS: [
		'#a6a5a2',
		'#28316a',
		'#4f5561',
		'#969036',
		'#a6a5a2',
	],
};
KtaneGraphicsParams.MAZE = {
	WIDTH: 10,
	HEIGHT: 10,
	WALL_THICKNESS: 2,
	CELL_WIDTH: 15,
	MARKER_COLOR: '#3a8ff4',
	GOAL_COLOR: '#f4df41',
	WALL_COLOR: '#f0f9f3',
	VERT_OFFSET: 10,
};
KtaneGraphicsParams.MAZE_CONTROL = {
	MOVE_BUTTON_RADIUS: 80,
	MOVE_BUTTON_OFFSET: 3,
};
KtaneGraphicsParams.SIMON_CONTROL = KtaneGraphicsParams.MAZE_CONTROL;
KtaneGraphicsParams.SIMON = {
	LIGHTS_RADIUS: 70,
	LIGHTS_OFFSET: 3,
	ROUND_NUM_PANEL_H: 40,
	ROUND_NUM_COLOR_OFF: KtaneGraphicsParams.GREEN_LED_OFF,
	ROUND_NUM_COLOR_ON: KtaneGraphicsParams.GREEN_LED_ON,
	ROUND_NUM_SPACING: 20,
	ROUND_NUM_RADIUS: 10,
	QUADRANT_COLOR_OFF: '#380000',
	QUADRANT_COLOR_ON: '#c92736',
	TEXT_COLOR_OFF: '#fbdfdd',
	TEXT_COLOR_ON: '#fbdfdd',
	NUM_ROUNDS: 3,
	BLINK_ON_TIME: 300, // ms
	BLINK_OFF_TIME: 200, // ms
	BLINK_SPACING: 1500, // ms
};
KtaneGraphicsParams.GRAVITY = {
};
KtaneGraphicsParams.CUBE = {
	START_BUTTON_WIDTH: 100,
	START_BUTTON_HEIGHT: 50
};
KtaneGraphicsParams.BUTTONS = {
	NUM_W: 2,
	NUM_H: 2,
};
KtaneGraphicsParams.PASSWORDS = {
	BUTTON_HEIGHT: 15,
};

export { KtaneGraphicsParams };
