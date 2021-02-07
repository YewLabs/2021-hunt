class KtaneClick {
	constructor(type, index=null, callback=null) {
		this.type = type;
		this.index = index;
		this.callback = callback;
	}
	equals(click) {
		return click != null &&
			this.type == click.type &&
			(this.index == null || this.index == click.index);
	}
};
KtaneClick.CLEAR_STATE_BUTTON = 0;
KtaneClick.START_BUTTON = 1;
KtaneClick.STOP_BUTTON = 2;
KtaneClick.ROTATE_BUTTON = 3;
KtaneClick.MANUAL_BUTTON = 4;
KtaneClick.MANUAL_PAGE_BUTTON = 5;
KtaneClick.WHOS_ON_FIRST_BUTTON = 6;
KtaneClick.WIRES_WIRE = 7;
KtaneClick.RELOAD_BUTTON = 8;
KtaneClick.MAZE_MOVE_BUTTON = 9;
KtaneClick.SIMON_MOVE_BUTTON = 10;
KtaneClick.CUBE_START_BUTTON = 11;
KtaneClick.BUTTONS_BUTTON = 12;
KtaneClick.RESTART_BUTTON = 13;
KtaneClick.PASSWORDS_BUTTON = 14;
KtaneClick.MUTE_BUTTON = 15;
KtaneClick.VOLUME_SLIDER = 16;
KtaneClick.INVERTED_CONTROLS_TOGGLE = 17;
KtaneClick.WEBGL_ENABLED_TOGGLE = 18;
KtaneClick.SHADOWS_ENABLED_TOGGLE = 19;
KtaneClick.SPECTATOR_MODE_TOGGLE = 20;

export { KtaneClick };
