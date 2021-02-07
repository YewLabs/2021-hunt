import { CanvasUtils as C } from '../graphics_canvas.js';
import { KtaneGraphicsParams } from '../graphics_params.js';
import { KtaneGraphicsControl as G } from '../graphics_control.js';
import { TextButton, TriangleButton } from '../graphics_components.js';
import { KtaneClick } from '../input.js';

const P = KtaneGraphicsParams.MAZE;

class KtaneMazeGraphics {
	constructor(canvasCtx, game, rect) {
		this.canvasCtx = canvasCtx;
		this.game = game;
		this.rect = rect;
	}
	hasHorzEdge(x, y) {
		if (x < 0 || x+1 >= P.WIDTH) {
			return false;
		}
		return this.game.maze.getHorzEdge(x, y);
	}
	hasVertEdge(x, y) {
		if (y < 0 || y+1 >= P.HEIGHT) {
			return false;
		}
		return this.game.maze.getVertEdge(x, y);
	}
	draw(active) {
		G.begin(this);
		G.drawBackgroundWithStrike(
			this, this.game.maze.getTimeSinceStrike()
		);

		const state = this.game.maze;
		const mazeW = P.WALL_THICKNESS * (P.WIDTH + 1) + P.CELL_WIDTH * P.WIDTH;
		const mazeH = P.WALL_THICKNESS * (P.HEIGHT + 1) + P.CELL_WIDTH * P.HEIGHT;
		const mazeX = this.rect.w/2 - mazeW/2;
		const mazeY = this.rect.h/2 - mazeH/2 + P.VERT_OFFSET;
		C.drawRect(
			this.canvasCtx,
			mazeX, mazeY, mazeW, mazeH,
			KtaneGraphicsParams.SCREEN_BACKGROUND_COLOR
		);
		if (this.game.maze.horzEdges != null) {
			// draw marker
			C.drawRect(
				this.canvasCtx,
				mazeX + state.x * P.CELL_WIDTH + (state.x+1) * P.WALL_THICKNESS + 3,
				mazeY + state.y * P.CELL_WIDTH + (state.y+1) * P.WALL_THICKNESS + 3,
				P.CELL_WIDTH - 6, P.CELL_WIDTH - 6,
				P.MARKER_COLOR
			);
			C.drawRect(
				this.canvasCtx,
				mazeX + state.goalX * P.CELL_WIDTH + (state.goalX+1) * P.WALL_THICKNESS + 3,
				mazeY + state.goalY * P.CELL_WIDTH + (state.goalY+1) * P.WALL_THICKNESS + 3,
				P.CELL_WIDTH - 6, P.CELL_WIDTH - 6,
				P.GOAL_COLOR
			);
			// draw walls
			for (let y = 0; y <= P.HEIGHT; y++) {
				for (let x = 0; x <= P.WIDTH; x++) {
					const offX = mazeX + x * (P.WALL_THICKNESS + P.CELL_WIDTH);
					const offY = mazeY + y * (P.WALL_THICKNESS + P.CELL_WIDTH);
					C.drawRect(
						this.canvasCtx,
						offX, offY,
						P.WALL_THICKNESS, P.WALL_THICKNESS,
						P.WALL_COLOR
					);
					if (y < P.WIDTH && !this.hasHorzEdge(x-1, y)) {
						C.drawRect(
							this.canvasCtx,
							offX, offY + P.WALL_THICKNESS,
							P.WALL_THICKNESS, P.CELL_WIDTH,
							P.WALL_COLOR
						);
					}
					if (x < P.WIDTH && !this.hasVertEdge(x, y-1)) {
						C.drawRect(
							this.canvasCtx,
							offX + P.WALL_THICKNESS, offY,
							P.CELL_WIDTH, P.WALL_THICKNESS,
							P.WALL_COLOR
						);
					}
				}
			}
		}

		const spacing = KtaneGraphicsParams.SUBMODULE_SPACING;
		C.drawText(
			this.canvasCtx,
			'N',
			this.rect.w/2,
			mazeY - spacing,
			'center', 'bottom', 15
		);
		const disarmed = this.game.maze.disarmed;
		G.drawDisarmedLed(this, disarmed);
		G.end(this);
	}
	updateMouse() {
		return null;
	}
};

export { KtaneMazeGraphics };
