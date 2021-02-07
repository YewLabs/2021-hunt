const FLOORS = 13;

let floorLights = {};

let state = 0;

function clearSwitches() {
  const windows = document.getElementsByClassName("window");
  for (let i = 0; i < windows.length; i++) {
    windows[i].classList.remove("lit");
  }
};

function pressSwitch(index) {
  if (state > 0) {
    document.getElementsByClassName("switch")[FLOORS-state].classList.remove("selected");
  }

  clearSwitches();
  if (state == index) {
    state = 0;
    return;
  }
  state = index;
  document.getElementsByClassName("switch")[FLOORS-state].classList.add("selected");

  let string = floorLights[index].join("");
  string = ".".repeat(5 * FLOORS - string.length) + string;
  const windows = document.getElementsByClassName("window");
  for (let i = 0; i < windows.length; i++) {
    if (string[i] === "*") {
      windows[i].classList.add("lit");
    }
  }
};
