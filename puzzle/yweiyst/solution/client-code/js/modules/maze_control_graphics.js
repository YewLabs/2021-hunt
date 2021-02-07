import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { QuadrantButton, TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';

const P = KtaneGraphicsParams.MAZE_CONTROL;

class KtaneMazeControlGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;

		this.moveButtons = G.forEachDir(
			this.rect.w/2, this.rect.h/2,
			P.MOVE_BUTTON_OFFSET,
			this.makeMoveButton.bind(this)
		);
		this.clickables = this.moveButtons;
	}
	makeMoveButton(x, y, direction) {
		return new QuadrantButton(
			this.canvasCtx, this.game,
			new KtaneClick(KtaneClick.MAZE_MOVE_BUTTON, direction, () => {
				this.game.maze.doInput(direction);
			}),
			x, y, P.MOVE_BUTTON_RADIUS,
			direction,
			KtaneGraphicsParams.DEFAULT_BUTTON_COLOR,
			KtaneGraphicsParams.DEFAULT_BUTTON_PRESSED_COLOR,
			KtaneGraphicsParams.DEFAULT_BUTTON_HOVER_COLOR
		);
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.maze.getTimeSinceStrike()
		);
		const disarmed = this.game.maze.disarmed;

		const synced = this.game.maze.clientTxn == this.game.maze.serverTxn;
		// C.drawCirc(
		// 	this.canvasCtx,
		// 	this.rect.w/2, this.rect.h/2,
		// 	P.MOVE_BUTTON_RADIUS + 2*P.MOVE_BUTTON_OFFSET,
		// 	(!disarmed && synced) ? '#FFFF00' : '#000000'
		// );

		G.drawClickables(this, active);
		G.forEachDir(
			this.rect.w/2, this.rect.h/2, P.MOVE_BUTTON_RADIUS*7/12,
			(x, y, direction) => {
				C.drawText(
					this.canvasCtx,
					KtaneGraphicsParams.CARDINAL_DIRECTION_NAMES[direction],
					x, y + 3,
					'center', 'middle', 30
				);
			}
		);

		G.drawDisarmedLed(this, disarmed);
		G.end(this);
	}
	updateMouse() {
		let bestClick = null;
		G.begin(this);
		bestClick = G.updateClick(
			bestClick,
			G.updateMouseClickables(this)
		);
		G.end(this);
		return bestClick;
	}
};

export { KtaneMazeControlGraphics };
