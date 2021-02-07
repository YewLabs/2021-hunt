import produce from "immer";

import Menu from "./menu.jsx";
import Level from "./level.jsx";
import End from "./end.jsx";
import Statistics from "./statistics.jsx";
import Leaderboard from "./leaderboard.jsx";
import { sampleBoard } from "./data";

import "./main.scss";

// const OFFLINE_MODE = window.location.host == "localhost:8080";
const OFFLINE_MODE = false;
const urlParams = new URLSearchParams(window.location.search);
// TODO: make sure these are eventually false
const FAKE_SERVER_MODE = new URLSearchParams(window.location.search).has(
  "fakeserver"
);
const SERVER_TEST = false;

const WEBSOCKETS_PROTOCOL = location.protocol === "https:" ? "wss" : "ws";
const WEBSOCKETS_ENDPOINT = OFFLINE_MODE
  ? null
  : "wss://mh2021.krawthekrow.me/boggle"

const TICK_INTERVAL = 100; // in ms, make larger if performance suffers

if (OFFLINE_MODE) {
  console.log("WARNING: offline mode");
}
if (FAKE_SERVER_MODE) {
  console.log("WARNING: fake server mode");
}

const copyIfExists = (state, msg, prop) => {
  if (prop in msg) {
    state[prop] = msg[prop];
  }
};

const mergeWords = (state, msg) => {
  let newWords = [];
  if ("words" in msg) {
    if (state.words == null) {
      state.words = msg["words"];
    }
    else {
      for (const w of msg["words"]) {
        if (!state.words.some((ow) => w[0] == ow[0])) {
          state.words.push(w);
          newWords.push(w);
        }
      }
    }
    state.words.sort();
  }
  return newWords;
};

const mergeScore = (state, msg) => {
  if ("score" in msg) {
    if (state.score == null) {
      state.score = msg["score"];
      return;
    }
    if (msg["score"] > state.score) {
      state.score = msg["score"];
    }
  }
};

function mergeRoundTrophies(state, msg) {
  if ("roundTrophies" in msg) {
    state.roundTrophies |= msg["roundTrophies"];
  }
}

function mergeTrophies(state, msg) {
  if ("trophies" in msg) {
    if (state.trophies == null) {
      state.trophies = msg["trophies"];
      return;
    }
    state.trophies = [...state.trophies]
      .map((c, i) => {
        const trophy = msg["trophies"][i];
        return trophy == "?" ? c : trophy;
      })
      .join("");
  }
}

class Main extends React.Component {
  constructor(props) {
    super(props);

    this.ws = null;
    this.timerInterval = null;
    this.stopTimer = null;

    // counter used for synchronization, see server code
    this.numGames = 0;

    this.state = {
      connected: false,
      navigation: "mainmenu",
      running: false,
      maxLevel: 0,
      roundTrophies: 0,
      totNumWords: null,
      level: null,
      timeLeft: null,
      timeLeftCheckpoint: null,
      renderedTimeLeft: null,
      totTime: null,
      maxScore: null,
      words: null,
      trophies: null,
      grid: null,
      bonuses: null,
      // used for the flashing animation in the grid
      wordResponses: [],
      // used for the flashing animation in the word list
      wordResponsesD: {},
      hiscores: null,
      blanks: null,
      allWords: null,
      stats: null,
      // this copy of numGames is for stats display
      numGames: null,
    };

    // FOR DEBUGGING ONLY
    window.main = this;
    this.debugStage = 0;
  }
  componentDidMount() {
    this.initWs();
  }
  handleBadAuth = () => {
    let team = null;

    while (team == null) {
      team = prompt('Enter team name (max 256 chars). Make sure this is the same for everyone in your team! You can change this later in the URL.');
    }
    window.location.href = `${window.location.pathname}?token=${encodeURIComponent(team)}`;
  }
  initWs = () => {
    if (OFFLINE_MODE) {
      this.setState(
        produce((state) => {
          state.connected = true;
          state.maxLevel = 3;
          state.running = false;
          state.timeLeft = 300 * 1000;
          state.timeLeftCheckpoint = new Date();
          state.renderedTimeLeft = 300 * 1000;
          state.totTime = 300 * 1000;
          state.trophies = "????????????????";
        })
      );
      this.updateTimeLeft({ timeLeft: 300 * 1000 });
      return;
    }
    this.ws = new WebSocket(WEBSOCKETS_ENDPOINT);
    this.ws.onopen = (e) => {
			const urlParams = new URLSearchParams(window.location.search);
			if (!urlParams.has('token')) {
				this.handleBadAuth();
			}
			let token = '';
			try {
				token = decodeURIComponent(urlParams.get('token'));
			} catch (e) {
				this.handleBadAuth();
			}
			if (token == '') {
				this.handleBadAuth();
			}

      this.wsSend({
        type: "AUTH",
        data: token,
      });

      this.requestGetUpdate();
      if (SERVER_TEST) {
        this.requestGetHiscores(0);
        this.requestStart(0);
      }

      this.handleWsOpen();
    };
    this.ws.onmessage = (e) => {
      // console.log("received " + e.data);
      const data = JSON.parse(e.data);
      this.handleWsMessage(data);
    };
    this.ws.onclose = (e) => {
      this.handleWsClose();
      this.initWs();
    };
  };
  wsSend = (msg) => {
    const data = JSON.stringify(msg);
    // console.log("sending " + data);
    this.ws.send(data);
  };
  handleWsOpen = () => {};
  handleWsClose = () => {
    this.numGames = 0;
    this.setState(
      produce(this.state, (state) => {
        state.connected = false;
      })
    );
  };
  handleWsMessage = (msg) => {
    const msg_type = msg["type"];
    const handlers = {
      "full": this.handleFullUpdate,
      "grade": this.handleGrade,
      "hiscores": this.handleHiscores,
    };
    handlers[msg_type](msg);
  };
  requestGetHiscores = (level) => {
    this.wsSend({
      type: "getHiscores",
      level: level,
    })
  };
  requestStart = (level) => {
    this.wsSend({
      type: "start",
      level: level,
    });
  };
  requestGetUpdate = () => {
    this.wsSend({
      type: "getUpdate",
    });
  };
  requestStop = () => {
    if (OFFLINE_MODE) {
      this.setState(produce(state => {
        state.navigation = "end";
        state.running = false;
      }));
      return;
    }
    this.wsSend({
      type: "stop",
      numGames: this.numGames,
    });
  };
  requestWord = (word) => {
    this.wsSend({
      type: "word",
      numGames: this.numGames,
      word: word,
    });
  };
  checkNumGames = (msg) => {
    const numGamesServer = msg["numGames"];
    if (numGamesServer < this.numGames) {
      // console.log("numGames check failed");
      return false;
    }
    this.numGames = numGamesServer;
    return true;
  };
  updateTimeLeft = (msg) => {
    if (!("timeLeft" in msg)) {
      return;
    }
    if (this.stopTimer !== null) {
      clearTimeout(this.stopTimer);
    }
    if (this.timerInterval !== null) {
      clearInterval(this.timerInterval);
    }
    this.stopTimer = setTimeout(this.requestStop, msg["timeLeft"]);
    this.timerInterval = setInterval(() => {
      this.setState(produce(state => {
        state.renderedTimeLeft = state.timeLeft - (new Date().getTime() - state.timeLeftCheckpoint.getTime());
      }))
    }, TICK_INTERVAL);
  };
  handleFullUpdate = (msg) => {
    if (!this.checkNumGames(msg)) {
      return;
    }
    if ('debugSeed' in msg) {
      console.log(`seed: ${msg['debugSeed']}`);
    }
    this.setState(produce(state => {
      if (state.running && !msg.running) {
        state.navigation = "end";
      }
      if (!state.running && msg.running) {
        state.score = null;
        state.words = null;
        state.special = null;
        state.roundTrophies = 0;
        state.allWords = null;
        state.wordResponsesD = {};
      }
      state.connected = true;
      copyIfExists(state, msg, "maxLevel");
      copyIfExists(state, msg, "running");
      copyIfExists(state, msg, "level");
      copyIfExists(state, msg, "timeLeft");
      if ("timeLeft" in msg) {
        state.timeLeftCheckpoint = new Date();
        state.renderedTimeLeft = msg["timeLeft"];
      }
      copyIfExists(state, msg, "totTime");
      copyIfExists(state, msg, "totNumWords");
      copyIfExists(state, msg, "maxScore");
      copyIfExists(state, msg, "grid");
      copyIfExists(state, msg, "bonuses");
      copyIfExists(state, msg, "special");
      copyIfExists(state, msg, "blanks");
      copyIfExists(state, msg, "allWords");
      copyIfExists(state, msg, "stats");
      copyIfExists(state, msg, "numGames");
      mergeScore(state, msg);
      mergeRoundTrophies(state, msg);
      mergeTrophies(state, msg);
      const newWords = mergeWords(state, msg);
      for (const newWord of newWords) {
        this.setWordResponse(state, newWord[0], "correct");
      }
      if (state.allWords !== null) {
        state.allWords.sort();
      }
    }));
    this.updateTimeLeft(msg);

    if (SERVER_TEST && this.debugStage == 0) {
      this.requestWord("orange");
      this.requestWord("yellow");
      this.requestWord("green");
      this.requestWord("green");
      this.debugStage++;
    }
  };
  handleGrade = (msg) => {
    const response = ["wrong", "duplicate", "correct"][msg["grade"]];
    const word = msg["word"];
    this.setState(
      produce((state) => {
        this.setWordResponse(state, word, response);
      })
    );
  };
  setWordResponse(state, word, response) {
    const fulfilled = () =>
      this.setState(
        produce((state) => {
          state.wordResponses = state.wordResponses.filter((x) => x.word !== word);
        })
      );
    state.wordResponses.push({
      word,
      fulfilled,
      response,
    });

    const oldResponse = (word in state.wordResponsesD) ? state.wordResponsesD[word] : null;
    const response0 = `${response}0`;
    const response1 = `${response}1`;
    if (oldResponse == null || (oldResponse != response0 && oldResponse != response1)) {
      state.wordResponsesD[word] = response0;
      return;
    }
    if (oldResponse == response0) {
      state.wordResponsesD[word] = response1;
      requestAnimationFrame(() => {
        this.setState(produce((state) => {
          if (word in state.wordResponsesD && state.wordResponsesD[word] == response1) {
            state.wordResponsesD[word] = response0;
          }
        }));
      });
    }
  }
  handleHiscores = (msg) => {
    this.setState(produce(state => {
      state.hiscores = msg['hiscores'];
    }));
  }
  handleSelectLevel = (level) => {
    if (OFFLINE_MODE) {
      this.setState(produce(state => {
        state.running = true;
        state.level = level;
        state.words = [];
        state.score = 0;
        state.totNumWords = 10;
        state.grid = sampleBoard[level];
        // bitmask indicating which trophies we got
        state.roundTrophies = 0b1100;
      }));
      return;
    }
    this.requestStart(level);
  };
  navigate = (target) => {
    if (target == "leaderboard") {
      this.handleChangeLeaderboardLevel(0);
    }
    this.setState(
      produce((state) => {
        state.navigation = target;
      })
    );
  };
  handleChangeLeaderboardLevel = (level) => {
    this.setState(
      produce((state) => {
        state.level = level;
        state.hiscores = null;
      })
    );
    this.requestGetHiscores(level);
  };
  handleQuit = () => {
    this.requestStop();
  };
  handleWord = (word) => {
    word = word.toLowerCase();
    if (OFFLINE_MODE) {
      this.setState(
        produce((state) => {
          state.words.push([word, 10]);
        })
      );
      return;
    }
    this.requestWord(word);
  };
  render() {
    const navigate = (s) => (e) => this.navigate(s);
    const onselectlevel = (level) => (e) => this.handleSelectLevel(level);

    if (!this.state.connected) {
      return <div className="msg">Connecting...</div>;
    }
    if (this.state.running) {
      return (
        <Level
          grid={this.state.grid}
          bonuses={this.state.bonuses}
          level={`level${this.state.level + 1}`}
          timeleft={this.state.renderedTimeLeft}
          tottime={this.state.totTime}
          totwords={this.state.totNumWords}
          maxscore={this.state.maxScore}
          score={this.state.score}
          words={this.state.words}
          special={this.state.special}
          wordresponses={this.state.wordResponses}
          wordresponsesd={this.state.wordResponsesD}
          onword={this.handleWord}
          onquit={this.handleQuit}
        />
      );
    }

    switch (this.state.navigation) {
      case "mainmenu":
        return (
          <Menu
            navigate={navigate}
            maxlevel={this.state.maxLevel}
            onselectlevel={onselectlevel}
            trophies={this.state.trophies}
            blanks={this.state.blanks}
          />
        );
      case "statistics":
        return <Statistics navigate={navigate} stats={this.state.stats} numgames={this.numGames} />;
      case "leaderboard":
        return <Leaderboard navigate={navigate} hiscores={this.state.hiscores} onlevel={this.handleChangeLeaderboardLevel} maxlevel={this.state.maxLevel} />;
      case "end":
        return (
          <End
            grid={this.state.grid}
            bonuses={this.state.bonuses}
            level={this.state.level}
            navigate={navigate}
            roundtrophies={this.state.roundTrophies}
            totwords={this.state.totNumWords}
            maxscore={this.state.maxScore}
            score={this.state.score}
            words={this.state.words}
            special={this.state.special}
            allwords={this.state.allWords}
          />
        );
      default:
        return <div className="msg">Loading...</div>;
    }
  }
}

const domContainer = document.querySelector("#mainContainer");
ReactDOM.render(<Main />, domContainer);
