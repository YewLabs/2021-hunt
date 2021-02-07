import { KtaneSync } from './sync.js';
import { ManualRenderer } from './manual/render.js';
import { manualData } from './manual/data.js';

class KtaneManual {
	constructor(game) {
		this.name = 'manual';
		this.game = game;

		this.selectedSectionNum = 0;
		this.sectionNum = 0;
		this.pageNum = 0;
		this.infos = {};
		this.renderers = [];
		this.numPages = [];

		this.imgs = {};
		this.imgReady = true;
	}
	reset(full) {
		if (full) {
			this.sectionNum = 0;
			this.pageNum = 0;
			this.selectedSectionNum = 0;
			this.renderers = [];
			this.numPages = [];
			this.infos = {};
			this.imgs = {};
		}
	}
	serverUpdate(msg) {
		this.selectedSectionNum = msg['selectedSectionNum'];
		if (this.sectionNum != msg['sectionNum']) {
			this.sectionNum = msg['sectionNum'];
			this.pageNum = 0;
		}
		if ('pageNum' in msg) {
			this.pageNum = msg['pageNum'];
		}
		this.infos[this.sectionNum] = msg['infos'];
		this.renderers = this.infos[this.sectionNum].map((manualInfo) =>
			new ManualRenderer(manualData, manualInfo)
		);
		this.numPages = this.renderers.map((renderer) =>
			renderer.getNumPages()
		);
	}
	getSubPageNum() {
		let startPage = 0;
		for (let i = 0; i < this.numPages.length; i++) {
			if (this.pageNum < startPage + this.numPages[i]) {
				return this.pageNum - startPage;
			}
			startPage += this.numPages[i];
		}
		return null;
	}
	getRenderer() {
		let startPage = 0;
		for (let i = 0; i < this.renderers.length; i++) {
			if (this.pageNum < startPage + this.numPages[i]) {
				return this.renderers[i];
			}
			startPage += this.numPages[i];
		}
		return null;
	}
	getTotPages() {
		let totPages = 0;
		for (let i = 0; i < this.numPages.length; i++) {
			totPages += this.numPages[i];
		}
		return totPages;
	}
	setSection(sectionNum) {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		this.game.manual.selectedSectionNum = sectionNum;
		this.game.sendModuleInput(
			this.game.getActiveSubmodule(this.name),
			{
				'sectionNum': sectionNum
			}
		);
	}
	flipPage(isRight) {
		if (this.game.rotManager.isRotating()) {
			return;
		}
		if (isRight) {
			if (this.pageNum + 1 >= this.getTotPages()) {
				return;
			}
			this.pageNum++;
		}
		else {
			if (this.pageNum <= 0) {
				return;
			}
			this.pageNum--;
		}
		this.game.sendModuleInput(
			this.game.getActiveSubmodule(this.name),
			{
				'pageNum': this.pageNum
			}
		);
	}
};

export { KtaneManual };
