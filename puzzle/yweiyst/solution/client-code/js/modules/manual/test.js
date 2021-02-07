import { ManualRenderer } from "./render.js";
import { manualData } from "./data.js";
import manual from "./example_manual.js";

Object.keys(manualData["manual"]).forEach((section) => {
  manual.module = section;
  const render = new ManualRenderer(manualData, manual);
  const totpages = render.getNumPages();
  for (let i = 0; i < totpages; i++) {
    console.log(render.getPage(i));
  }
})
