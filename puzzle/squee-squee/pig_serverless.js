// hi! this puzzle is not intended to be reverse engineered. thanks

// TEMPLATE

const intro = (context) => `
<style>
.submission-box {
    text-align: center;
    margin: auto;
    margin-top: 15px;
}

.solved {
    border: 3px solid black;
}

.blankrow {
    height: 24px;
}

</style>

<form>
    <label for="pronoun">Choose a pronoun for your pig:</label><br>
    <select name="pronoun" id="pronoun" onchange="updatePronoun()">
        <option value="he" ${
          context("he_pronoun") ? "selected" : ""
        }>he</option>
        <option value="she" ${
          context("she_pronoun") ? "selected" : ""
        }>she</option>
        <option value="they" ${
          context("they_pronoun") ? "selected" : ""
        }>they</option>
        <option value="it" ${
          context("it_pronoun") ? "selected" : ""
        }>it</option>
    </select>
</form>

<div class="submission-box ${context("name") ? "solved" : ""}">
${
  !context("name")
    ? '<form autocomplete="off" onsubmit="event.preventDefault(); makeGuess()"><input type="text" id="guess" name="guess" maxlength="50"><br><input type="submit" value="Submit"></form><div id="response" style="color:red"></div>'
    : `<p><b>${context("name").toUpperCase()}</b> is your pig’s name.</p>`
}
</div>
`;

const pigsaw = (context) => `
<h2>2. Pigsaw</h2>
<p>“Oink oink!”<br>
<i>Let’s solve a puzzle, oink!</i></p>

<p>${context(
  "name"
)} seems quite excited to be participating in the MIT Mystery Hunt. Maybe you should introduce <span class="object-pronoun">${context(
  "object_pronoun"
)}</span> on your team’s primary communication channel. After all, <span class="contracted-subject">${context(
  "contracted_subject"
)}</span> one of the gang now. That reminds you, since <span class="contracted-subject">${context(
  "contracted_subject"
)}</span> a valued team member, you should ensure ${context(
  "name"
)} stays healthy and out of physical danger. Team members that are incapacitated can’t solve puzzles.</p>

<p>You look around, and you find a piece of paper with strange shapes drawn on it. There are several letters and numbers written on it.</p>

<p>“Squee squee!”<br>
<i>Wow, a pigsaw puzzle! I really like pigsaw puzzles.</i></p>

<p>“Squee squee?”<br>
<i>[thoughtful squeeing] Could this be the solution to the pigsaw?</i></p>

<div style="margin:auto; max-width:30%">
    <img style="max-width:100%" src="pigsaw-puzzle-solution.png">
</div>

<p>You gasp. This <i>does</i> look like the pigsaw solution to you. But does ${context(
  "name"
)} have any idea what this diagram means? For the sake of your pig child’s youthful innocence, you hope not.</p>

<div class="submission-box ${context("dinner_unlocked") ? "solved" : ""}">
${
  context("dinner_unlocked")
    ? "<p><b>EAT DINNER</b> is correct!</p>"
    : '<form autocomplete="off" onsubmit="event.preventDefault(); makeGuess()"><input type="text" id="guess" name="guess" maxlength="50"><br><input type="submit" value="Submit"></form><div id="response" style="color:red"></div>'
}
</div>
`;

const dinner = (context) => `
<p>“Squee squee”<br>
<i>That was fun. It looks like we made a pigñata.</i></p>

<p>Pigñata? You would never smash a face that cute. </p>

<p>“Squeeeeeeeeeeeeeeeee”<br>
<i>[tired squeeing] Also, I’m exhausted and hungry. Can we eat some dinner?</i></p>

<p>Right, one of your duties as a pig parent is to feed your pig. You feed ${context(
  "name"
)} three quarters. Big dinner!</p>

<form onsubmit="event.preventDefault(); doIt()">
    <input type="submit" value="I did it">
</form>
</div>
`;

const sleeping = (context) => `
<p>${context(
  "name"
)} chews for a bit, and then with a soft oink, <span class="subject-pronoun">${context(
  "subject_pronoun"
)}</span> curl<span class="conjugate">${
  context("they_pronoun") ? "" : "s"
}</span> up next to your computer in the warm spot where the fan blows. <span class="contracted-subject capital">${context(
  "contracted_subject"
)}</span> quickly asleep. Looks like you have a minute to grab a bite to eat or have some water. (Removing the pigsaw is optional).</p>

<p>[${
  context("health_unlocked")
    ? "Timer expired"
    : `<span class="timer">${context("m_remaining")}:${context(
        "s_remaining"
      )}</span>`
}] ${context("name")} is sleeping peacefully.</p>
`;

const health = (context) => `
<h2>3. Health Check</h2>
<p>${context("name")} yawns <span class="object-pronoun">${context(
  "object_pronoun"
)}</span>self awake. Rise and shine, ${context("name")}, it’s a big day!</p>

<p>It’s time to do a health check for ${context(
  "name"
)}! You can’t just be all higgledy-piggledy when it comes to personal health. If it weren’t for healthy pigs, where would bacon come from?</p>

<p>${context(
  "name"
)}’s heart girth should be measured across the holes, and the height should include the ears. Rounding to the nearest whole number, what is the ratio of…</p>

<table>
<tr><td>… ${context(
  "name"
)}’s weight to the weight of a one-ounce lug of pig iron?</td></tr>
<tr><td>… the length of the long edge of a 16oz pack of Oscar Mayer bacon to ${context(
  "name"
)}’s heart girth?</td></tr>
<tr><td>… the circumference of a Trans-Alaska pipeline cleaning pig to ${context(
  "name"
)}’s heart girth?</td></tr>
<tr class="blankrow"><td></td></tr>
<tr><td>… ${context(
  "name"
)}’s height to the circumference of a quarter?</td></tr>
<tr><td>… the weight of $100 in quarters to ${context(
  "name"
)}’s weight?</td></tr>
<tr><td>… the weight of a mint-condition copy of Chickapig to ${context(
  "name"
)}’s weight?</td></tr>
<tr class="blankrow"><td></td></tr>
<tr><td>… the (short) circumference of an inflated pigskin to ${context(
  "name"
)}’s height?</td></tr>
<tr><td>… the heart girth of a Pass the Pigs: Big Pigs pig to ${context(
  "name"
)}’s heart girth?</td></tr>
<tr><td>… the height of a 0.65-ton feed capacity Osborne outdoor bulk feeder to ${context(
  "name"
)}’s height?</td></tr>
<tr><td>… the weight of 2/3 gallon of whole-fat milk (without carton) to ${context(
  "name"
)}’s weight?</td></tr>
<tr><td>… the height of Kevin Bacon to ${context("name")}’s height?</td></tr>
</table>

<p>What is the outcome of ${context("name")}’s health check?</p>

<div class="submission-box ${context("feeding1_unlocked") ? "solved" : ""}">
${
  context("feeding1_unlocked")
    ? "<p><b>FAT AND HAPPY</b> is correct!</p>"
    : '<form autocomplete="off" onsubmit="event.preventDefault(); makeGuess()"><input type="text" id="guess" name="guess" maxlength="50"><br><input type="submit" value="Submit"></form><div id="response" style="color:red"></div>'
}
</div>
`;

const feeding1 = (context) => `
<p>${context("name")} really is a fat and happy pig.</p>

<p>“Squee squee!”<br>
<i>All this puzzle solving is making me hungry!</i></p>

<p>Feed ${context("name")} four pennies.</p>

<form onsubmit="event.preventDefault(); doIt()">
    <input type="submit" value="I did it">
</form>
`;

const chewing1 = (context) => `
<p>[${
  context("feeding2_unlocked")
    ? "Timer expired"
    : `<span class="timer">${context("m_remaining")}:${context(
        "s_remaining"
      )}</span>`
}] ${context("name")} is chewing.</p>
`;

const feeding2 = (context) => `
<p>${context(
  "name"
)}’s tummy makes a gurgle. Guess <span class="contracted-subject">${context(
  "contracted_subject"
)}</span> still hungry. Pennies don’t seem to fill ${context(
  "name"
)} up, they’re really more of a snack food. You feed <span class="object-pronoun">${context(
  "object_pronoun"
)}</span> two more quarters.</p>

<form onsubmit="event.preventDefault(); doIt()">
    <input type="submit" value="I did it">
</form>
`;

const chewing2 = (context) => `
<p>[${
  context("coins_unlocked")
    ? "Timer expired"
    : `<span class="timer">${context("m_remaining")}:${context(
        "s_remaining"
      )}</span>`
}] ${context("name")} is chewing.</p>
`;

const coinsString = (context) => `
<h2>4. Coins</h2>
<p>“Squee squee!”<br>
<i>Yum! That was delicious!</i></p>

<p>Job well done.</p>

<p>“Squee squee”<br>
<i>Actually, now that I think about it, I don’t feel so good.</i></p>

<p>Of course. What were you thinking, feeding your pig child metal coins?! Are those even digestible? As a pig parent, maybe you should sample your child’s food—make sure it’s edible? No, that doesn't sound like a good idea either.</p>

<p>You decide the best course of action is to promptly remove all the coins from ${context(
  "name"
)}’s stomach. It’s time to make a cash withdrawal, total value $1.72.</p>

<p>“Squeeee squee”<br>
<i>Please be careful not to hurt me when you remove the coins.</i></p>

<p>In the meantime, your teammates have started on a <a href="new-puzzle.pdf">new puzzle</a>. Never one to miss out, ${context(
  "name"
)} is giving off swine-y sounds of excitement.</p>

<p>“Squee squee squee squee squee!!”<br>
<i>I know the rules for this type of logic puzzle! We need to put all the coins in the squares. Each square holds at most one coin, and you can’t put a coin in a box if it’s too big to fit. The numbers give the total value of the coins in the squares that intersect the arrow when you extend it. Also, because the puzzle writers aren’t mean, in any square where a dime fits, a penny fits too. Oh, here’s an idea for extracting an answer: first read the quarters, then the dimes, etc. </i></p>

<div class="submission-box ${context("photo_unlocked") ? "solved" : ""}">
${
  context("photo_unlocked")
    ? "<p><b>I GOT MY QUARTERS BACK</b> is correct!</p>"
    : '<form autocomplete="off" onsubmit="event.preventDefault(); makeGuess()"><input type="text" id="guess" name="guess" maxlength="50"><br><input type="submit" value="Submit"></form><div id="response" style="color:red"></div>'
}
</div>
`;

const photo = (context) => `
<h2>5. Photo</h2>
<p>“Squee squee?”<br>
<i>You have quarterbacks? I have a pigskin, do you want to play a quick game?</i></p>

<p>It’s probably not the time for that right now.</p>

<p>“Squee squee. Squee squee squee”<br>
<i>[reflective squeeing] This is my first Mystery Hunt, I’ve really had a good time. But I really want to meet other Hunters like me. Is there anyone who’s really like me?</i></p>

<p>${context(
  "name"
)}’s hogitation is giving you big “have I socialized my precious pig child enough” anxiety. You would love for this Mystery Hunt to be a smashing success for ${context(
  "name"
)}. Pigs like <span class="object-pronoun">${context(
  "object_pronoun"
)}</span> aren’t all that common at Mystery Hunt, but surely you can “oink-quaint” <span class="object-pronoun">${context(
  "object_pronoun"
)}</span> with at least one other?</p>

<p>Take a picture of another pig who can be ${context(
  "name"
)}’s friend alongside a piece of paper with “MYST 2021” written on it. The other pig should be three-dimensional, but it doesn’t have to be alive. During the hunt, teams emailed their submissions to HQ and received the answer <span class="answer spoiler">PIGPEN PALS.</span></p>

<div class="submission-box ${context("finish_unlocked") ? "solved" : ""}">
${
  context("finish_unlocked")
    ? "<p><b>PIGPEN PALS</b> is correct!</p>"
    : '<form autocomplete="off" onsubmit="event.preventDefault(); makeGuess()"><input type="text" id="guess" name="guess" maxlength="50"><br><input type="submit" value="Submit"></form><div id="response" style="color:red"></div>'
}
</div>
`;

const finish = (context) => `
<p>You’ve been hammering away for quite some time now; hopefully a little more hammering can finish the puzzle?</p>

<p>“Squee squee!”<br>
<i>A metapuzzle! This is so exciting! We’re so close!</i></p>

<p>This is it. You have a look back at the submissions you’ve made so far. You wish you could reflect ${context(
  "name"
)}’s optimism, but your eyes are worn from misplaced sleep; you’re pretty tired. You have an urge to hit something.</p>

<p>“Squee squee”<br>
<i>I have an idea. Why don’t we use the numbers ${
  context("fav_num") >= 0 ? "+" : ""
}${context("fav_num")}, -4, +14, -4, +2? Those are my favorite numbers.</i></p>

<p>What a dumb idea. ${context(
  "name"
)} must be really losing it. Your harried staring at the answers convinces you that you don’t have the entire answer. You get the sense there is a second half lurking somewhere dark. Where could the other half be?</p>

<p>Suddenly an idea hits you. An idea hits you really hard. You look at ${context(
  "name"
)}.</p>

<p>“Squee squee”</p>

<p>Do you really have it in you?</p>
`;

const virtualPig = (context) => `
<style>
#virtual-pig-wrapper {
  margin-top: 30px;
  align-items: flex-start;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
}
.pig {
  perspective: 100px;
  position: relative;
  margin-bottom: 60px;
}
.coins {
  display: flex;
  flex-direction: column;
}
.coins p {
  text-align: center;
  width: 100%;
}
.coin {
  align-items: center;
  box-sizing: border-box;
  flex-direction: column;
  display: flex;
  justify-content: center;
  height: 80px;
  width: 80px;
  position: relative;
}
.coin img {
  border-radius: 50%;
  position: absolute;
  touch-action: none;
  transform: scale(0.5);
  z-index: 2;
}
img.highlight {
  filter: contrast(140%);
}
.pig-hole {
  position: absolute;
  width: 27%;
  height: 15%;
  top: 3%;
  left: 33%;
  box-sizing: border-box;
}
.pig-hole.dashed {
  border: 5px dashed black;
}
#coindrop {
  left: 35%;
  position: absolute;
  top: -15%;
  transition: opacity 0.2s;
}
#buttons {
  display: flex;
  flex-direction: row;
  justify-content: center;
}
.pig #scale {
  background: #c1c2bf;
  bottom: 0;
  height: 20%;
  transform: rotateX(40deg);
  position: absolute;
  width: 100%;
  z-index: -1;
}
#measurements {
  margin-top: 1em;
  display: flex;
  justify-content: center;
}
#measurements p {
  margin: 1em;
}
</style>

<hr>
<div id="virtual-pig-wrapper">
  ${
    context("dinner_unlocked")
      ? '<div class="coins"><div class="coin"><img id="quarter" src="virtual-pig/25.png" alt="A quarter." /></div><div class="coin"><img id="dime" src="virtual-pig/10.png" alt="A dime." /></div><div class="coin"><img id="nickel" src="virtual-pig/5.png" alt="A nickel." /></div><div class="coin"><img id="penny" src="virtual-pig/1.png" alt="A penny." /></div></div>'
      : ""
  }
  <div class="pig" style="height:376px; width: 376px">
    ${
      context("finish_unlocked") && !context("trueend_unlocked")
        ? '<img id="pig-image0" src="virtual-pig/pig.png" alt="A piggy bank." draggable="false" style="position:absolute"/><img id="pig-image1" src="virtual-pig/pig1.png" alt="A piggy bank." draggable="false" style="visibility: hidden; position: absolute"/><img id="pig-image2" src="virtual-pig/pig2.png" alt="A piggy bank." draggable="false" style="visibility: hidden; position: absolute"/><img id="pig-image3" src="virtual-pig/pig3.png" alt="A piggy bank." draggable="false" style="visibility: hidden; position: absolute"/><img id="pig-image4" src="virtual-pig/pig4.png" alt="A piggy bank." draggable="false" style="visibility: hidden; position: absolute"/><img id="pig-image5" src="virtual-pig/pig5.png" alt="A piggy bank." draggable="false" style="visibility: hidden; position: absolute"/><img id="pig-image6" src="virtual-pig/pig6.png" alt="A piggy bank." draggable="false" style="visibility: hidden; position: absolute"/>'
        : `<img id="pig-image" src="virtual-pig/pig${
            context("trueend_unlocked") ? "6" : ""
          }.png" alt="A piggy bank." draggable="false" />`
    }
    ${
      context("dinner_unlocked")
        ? '<img id="coindrop" src="virtual-pig/coindrop.png" style="opacity: 0" /><div class="pig-hole"></div>'
        : ""
    }
    ${
      context("health_unlocked")
        ? '<div id="scale" style="display: none"></div>'
        : ""
    }
  </div>
  ${
    context("dinner_unlocked")
      ? `<div class="counter"><table><tr><th>Contents</th><th></th></tr><tr><td>Quarters</td><td id="quarter-count">${context(
          "quarter"
        )}</td></tr><tr><td>Dimes</td><td id="dime-count">${context(
          "dime"
        )}</td></tr><tr><td>Nickels</td><td id="nickel-count">${context(
          "nickel"
        )}</td></tr><tr><td>Pennies</td><td id="penny-count">${context(
          "penny"
        )}</td></tr></table></div>`
      : ""
  }
</div>
${
  context("health_unlocked")
    ? `<div id="buttons"><button id="scale-button" onclick="toggleScale()">Show scale</button>${
        context("finish_unlocked")
          ? '<button id="hammer-button" onclick="toggleHammer()">Activate hammer</button>'
          : ""
      }</div>`
    : ""
}
${
  context("health_unlocked")
    ? '<div id="measurements" style="display: none"><p>Height: 7.0 cm</p><p>Girth: 19.5 cm</p><p>Weight: <span id="weight">0</span> g</p></div>'
    : ""
}

${context("health_unlocked") ? `
<script>
function toggleScale() {
  let scale = gid("scale");
  let measurements = gid("measurements");
  if (scale.style.display === "none") {
    scale.style.display = "block";
    measurements.style.display = "flex";
    computeWeight();
    gid("scale-button").innerHTML = "Hide scale";
  } else {
    scale.style.display = "none";
    measurements.style.display = "none";
    gid("scale-button").innerHTML = "Show scale";
  }
}
</script>
`: ""}

${context("finish_unlocked") ? `
<script>
if (!declare_vars) {
  var hammer = false;
  var cracks = 0;
  declare_vars = true;
}
gid('hammer-button').innerHTML = hammer ? "Deactivate hammer" : "Activate hammer";

function toggleHammer() {
  if (gid("scale").style.display !== "none")
    toggleScale();
  if (!hammer) {
    for (let i = 0; i < 6; i++) {
      const elt = gid('pig-image'+i);
      if (elt) {
        elt.style.cursor = "pointer";
        elt.addEventListener("click", smash);
      }
    }
    gid("hammer-button").innerHTML = "Deactivate hammer";
  } else {
    for (let i = 0; i < 6; i++) {
      const elt = gid('pig-image'+i);
      if (elt) {
        elt.style.cursor = "default";
        elt.removeEventListener("click", smash);
      }
    }
    gid("hammer-button").innerHTML = "Activate hammer";
  }
  hammer = !hammer;
}

function smash(e) {
  if (cracks < 6) {
    const elt = document.getElementById("pig-image" + String(cracks));
    const newElt = document.getElementById("pig-image" + String(cracks+1));
    newElt.style.visibility = "visible";
    elt.style.visibility = "hidden";
    cracks++;
    if (cracks === 6) {
      doIt();
    }
  }
}
</script>` : ""}

${context("dinner_unlocked") ? `
<script>
if (!interacted) {
  interact(".coin img").draggable({
    inertia: true,
    listeners: {
      move: dragMoveListener,
    },
  });

  interact(".pig-hole").dropzone({
    overlap: 0.1,
    ondropactivate: function (e) {
      e.target.classList.add("dashed");
    },
    ondragenter: function (e) {
      e.relatedTarget.classList.add("highlight");
    },
    ondragleave: function (e) {
      e.relatedTarget.classList.remove("highlight");
    },
    ondrop: function (e) {
      const t = e.relatedTarget;
      incrementCoin(t.id);
      t.style.transform = "translate(0, 0) scale(0.5)";
      t.setAttribute("data-x", 0);
      t.setAttribute("data-y", 0);
      t.classList.remove("highlight");
      const cd = document.getElementById("coindrop");
      cd.style.opacity = "1";
      setTimeout(() => {
        cd.style.opacity = "0";
      }, 500);
      computeWeight();
    },
    ondropdeactivate: function (e) {
      e.target.classList.remove("dashed");
    },
  });

  interacted = true;
}

function dragMoveListener(e) {
  const t = e.target;
  const x = (parseFloat(t.getAttribute("data-x")) || 0) + e.dx;
  const y = (parseFloat(t.getAttribute("data-y")) || 0) + e.dy;
  t.style.transform = "translate(" + x + "px, " + y + "px) scale(0.5)";
  t.setAttribute("data-x", x);
  t.setAttribute("data-y", y);
}

function setCoin(coin, count) {
  document.getElementById(coin.concat("-count")).textContent = Number(count);
}

function incrementCoin(coin) {
  const elt = document.getElementById(coin.concat("-count"));
  elt.textContent = Number(elt.textContent) + 1;
  coins(coin, elt.textContent);
}

function computeWeight() {
  let total = 116;
  [
    ["quarter", 5.67],
    ["dime", 2.268],
    ["nickel", 5],
    ["penny", 2.5],
  ].forEach(([coin, weight]) => {
    const elt = document.getElementById(coin.concat("-count"));
    total += Number(elt.textContent) * weight;
  });
  const e = gid("weight");
  if (e) e.textContent = Math.round(total);
}

${context("trueend_unlocked") ? 'interact(".pig-hole").unset()' : ""}

</script>
` : ""}

`;

const trueend = (context) => `
<p>Inside ${context(
        "name"
      )} you find a crumpled <a href="paper.pdf">piece of paper</a>.</p>
`;

// CLIENT CODE

const pronouns = {
  "subject-pronoun": { he: "he", she: "she", they: "they", it: "it" },
  possessive: { he: "his", she: "her", they: "their", it: "its" },
  "object-pronoun": { he: "him", she: "her", they: "them", it: "it" },
  "contracted-subject": {
    he: "he’s",
    she: "she’s",
    they: "they’re",
    it: "it’s",
  },
};

const gcn = (c) => Array.from(document.getElementsByClassName(c));
const gid = (i) => document.getElementById(i);
let interacted = false;
let declare_vars = false;

const refresh = () => sendMessage("refresh");
const doIt = () => sendMessage("doIt");
const rename = () => sendMessage("rename");
const reset = () => sendMessage("reset");
const makeGuess = () => sendMessage("guess", { guess: gid("guess").value });
const coins = (coin, count) => sendMessage("coin", { coin, count });
const updatePronoun = () => {
  let pronoun = gid("pronoun").value;
  setPronoun(pronoun);
  sendMessage("pronoun", { pronoun });
};

const receiveMessage = (data) => {
  if (data.type == "refresh_request") {
    refresh();
  } else if (data.type == "refresh") {
    gid("puzzle-content").innerHTML = data.content;
    start_timers();
    runScripts(gid("puzzle-content"));
  } else if (data.type == "pronoun") {
    setPronoun(data.pronoun);
  } else if (data.type == "incorrect_guess") {
    gid("response").innerHTML = data.msg;
  } else if (data.type == "coin") {
    setCoin(data.coin, data.count);
  }
};

const str_to_sec = (s) =>
  s.split(":").reduce((a, c, i) => a + (i ? 1 : 60) * Number(c), 0);
const sec_to_str = (sec) =>
  `${Math.floor(sec / 60).toString()}:${String(sec % 60).padStart(2, "0")}`;
const start_timers = () =>
  gcn("timer").forEach((e) => {
    let timer = setInterval(() => {
      let rem = str_to_sec(e.innerHTML);
      if (rem <= 0) {
        clearInterval(timer);
        refresh();
      } else {
        e.innerHTML = sec_to_str(rem - 1);
      }
    }, 1000);
  });

const setPronoun = (pronoun) => {
  gid("pronoun").value = pronoun;
  Object.entries(pronouns).forEach(([kind, arr]) =>
    gcn(kind).forEach((e) => (e.innerHTML = arr[pronoun]))
  );
  gcn("capital").forEach((e) => {
    let val = e.innerHTML;
    e.innerHTML = val.charAt(0).toUpperCase() + val.slice(1);
  });
  gcn("conjugate").forEach((e) => (e.innerHTML = pronoun == "they" ? "" : "s"));
};

const runScripts = (elt) =>
  Array.from(elt.getElementsByTagName("script")).forEach((e) => {
    const scr = document.createElement("script");
    scr.text = e.innerHTML;
    e.src && scr.setAttribute("src", e.src);
    e.parentNode.replaceChild(scr, e);
  });

// SERVER CODE

const OBJECT_PRONOUNS = {
  he: "him",
  she: "her",
  they: "them",
  it: "it",
};

const CONTRACTED_SUBJECTS = {
  he: "he’s",
  she: "she’s",
  they: "they’re",
  it: "it’s",
};

const STAGES = [
  "intro",
  "pigsaw",
  "dinner",
  "sleeping",
  "health",
  "feeding1",
  "chewing1",
  "feeding2",
  "chewing2",
  "coins",
  "photo",
  "finish",
  "trueend",
];

const SUBPUZZLE_ANSWERS = {
  pigsaw: "EATDINNER",
  health: "FATANDHAPPY",
  coins: "IGOTMYQUARTERSBACK",
  photo: "PIGPENPALS",
};

const STAGE_TIME = {
  sleeping: 60,
  chewing1: 10,
  chewing2: 10,
};

const DO_IT = ["dinner", "feeding1", "feeding2"];

const STARTING_COUNTS = {
  quarter: 0,
  dime: 2,
  nickel: 4,
  penny: 3,
};

const render_to_string = (context) =>
  [
    intro(context),
    context("pigsaw_unlocked") ? pigsaw(context) : "",
    context("dinner_unlocked") ? dinner(context) : "",
    context("sleeping_unlocked") ? sleeping(context) : "",
    context("health_unlocked") ? health(context) : "",
    context("feeding1_unlocked") ? feeding1(context) : "",
    context("chewing1_unlocked") ? chewing1(context) : "",
    context("feeding2_unlocked") ? feeding2(context) : "",
    context("chewing2_unlocked") ? chewing2(context) : "",
    context("coins_unlocked") ? coinsString(context) : "",
    context("photo_unlocked") ? photo(context) : "",
    context("finish_unlocked") ? finish(context) : "",
    virtualPig(context),
    context("trueend_unlocked") ? trueend(context) : "",
  ].join("");

const render_puzzle_stages = (context) => {
  const current_stage = context("stage");
  let unlocked = true;
  STAGES.forEach((stage) => {
    context("set", { [stage.concat("_unlocked")]: unlocked });
    if (stage === current_stage) unlocked = false;
  });
  return render_to_string(context);
};

let puzzle_state = {};

const sendMessage = (type, data) => {
  if (type === "refresh") {
    const context = update_and_get_context();
    const content = render_puzzle_stages(context);
    receiveMessage({ type, content });
  } else if (type === "pronoun") {
    puzzle_state.pronoun = data.pronoun;
  } else if (type === "doIt") {
    let stage = puzzle_state.stage;
    if (DO_IT.includes(stage) || stage === "finish") {
      puzzle_state.previous_action_time = Date.now();
      puzzle_state.stage = next_stage(stage);
      receiveMessage({ type: "refresh_request" });
    }
  } else if (type === "guess") {
    const [correct, msg] = submit(data.guess);
    correct
      ? receiveMessage({ type: "refresh_request" })
      : receiveMessage({ type: "incorrect_guess", msg });
  } else if (type === "reset") {
    puzzle_state.stage = "intro";
    puzzle_state.pronoun = "he";
    puzzle_state.name = null;
    puzzle_state.previous_action_time = null;
    Object.entries(STARTING_COUNTS).forEach(
      ([coin, count]) => (puzzle_state[coin.concat("_count")] = count)
    );
    receiveMessage({ type: "refresh_request" });
  } else if (type === "rename") {
    puzzle_state.stage = "intro";
    puzzle_state.name = null;
    puzzle_state.previous_action_time = null;
    receiveMessage({ type: "refresh_request" });
  } else if (type === "coin") {
    const { coin, count } = data;
    puzzle_state[coin.concat("_count")] = count;
  }
};

const next_stage = (stage) =>
  STAGES[STAGES.findIndex((s) => s === stage) + 1] ?? STAGES[0];
const normalize = (guess) => guess.toUpperCase().replace(/[^A-Z]/g, "");

const submit = (guess) => {
  let stage = puzzle_state.stage;
  if (stage === "intro") {
    const name = guess.trim();
    if (name.length === 0) return [false, "Name cannot be blank"];
    if (!name[0].match(/[a-zA-Z]/)) return [false, "Invalid name"];
    puzzle_state.stage = next_stage(stage);
    puzzle_state.name = name;
    return [true, null];
  }
  const g = normalize(guess);
  if (g && SUBPUZZLE_ANSWERS[stage] === g) {
    puzzle_state.previous_action_time = Date.now();
    puzzle_state.stage = next_stage(stage);
    return [true, null];
  }
  return [false, `${g} is incorrect`];
};

const update_and_get_context = () => {
  let { stage, pronoun, name, previous_action_time } = puzzle_state;
  let state = {
    name: name,
    subject_pronoun: pronoun,
    contracted_subject: CONTRACTED_SUBJECTS[pronoun],
    object_pronoun: OBJECT_PRONOUNS[pronoun],
  };
  Object.keys(STARTING_COUNTS).forEach(
    (coin) => (state[coin] = puzzle_state[coin.concat("_count")])
  );
  if (name) {
    state.fav_num = "W".charCodeAt() - name.toUpperCase().charCodeAt();
  }
  Object.keys(OBJECT_PRONOUNS).forEach(
    (p) => (state[p.concat("_pronoun")] = p === pronoun)
  );
  if (STAGE_TIME[stage]) {
    const rem =
      STAGE_TIME[stage] -
      Math.floor((Date.now() - previous_action_time) / 1000);
    state.m_remaining = Math.floor(rem / 60);
    state.s_remaining = String(rem % 60).padStart(2, "0");
    if (rem <= 0) {
      stage = next_stage(stage);
      puzzle_state.stage = stage;
    }
  }
  state.stage = stage;
  return (query, data) => {
    if (query === "set") return Object.assign(state, data);
    return state[query];
  };
};

reset();
