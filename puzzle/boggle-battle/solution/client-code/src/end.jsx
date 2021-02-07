import produce from "immer";

import Grid from "./grid.jsx";

import { trophyDescriptions } from "./data";

export default class End extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      trophies: false,
    };
  }

  viewTrophies = (e) => {
    this.setState(
      produce((state) => {
        state.trophies = true;
      })
    );
  };

  percentOf = (n, tot) => `${Math.floor((100 * n) / tot)}%`;

  render() {
    let trophies = [];
    trophyDescriptions.forEach((li, i) =>
      li.forEach((desc, j) => {
        if ((this.props.roundtrophies & (1 << (4 * i + j))) === 0) return;
        trophies.push(desc);
      })
    );
    const foundWords = new Set(this.props.words?.map(([w, sc]) => w));
    const renderWords = this.state.trophies ? (
      <div className="trophies">
        {trophies.map((desc, i) => (
          <div className="entry" key={i}>
            <div className="trophy">
              <div className="stand"></div>
              <img src="./static/trophy.svg" draggable="false" />
            </div>
            <span className="description">{desc}</span>
          </div>
        ))}
      </div>
    ) : (
      this.props.allwords?.map((w, i) => {
        const isSpecial =
          this.props.special != null && w[0] == this.props.special;
        const isFound = foundWords.has(w[0]);
        return (
          <span
            key={w[0]}
            className={`
                  ${isSpecial ? "special" : ""}
                  ${isFound ? "found" : "unfound"}
                `}
          >
            <span
              className={`
              score
              ${w[1] > 999 ? "small" : ""}
              `}
            >
              {w[1]}
            </span>{" "}
            {w[0]}
          </span>
        );
      })
    );
    return (
      <div className="end level">
        <div className="toolbar">
          <p className="points">
            Level {this.props.level + 1}. You found {this.props.words.length} of {this.props.totwords} words ({this.percentOf(this.props.words.length, this.props.totwords)}), for {this.props.score} points ({this.percentOf(this.props.score, this.props.maxscore)}).
          </p>
        </div>
        <Grid
          grid={this.props.grid}
          bonuses={this.props.bonuses}
          level={this.props.level + 1}
          disabled={true}
        />
        <div className="inputs">
          <div className="words">{renderWords}</div>
          {this.props.roundtrophies !== 0 && !this.state.trophies ? (
            <button onClick={this.viewTrophies}>View trophies</button>
          ) : (
            <button onClick={this.props.navigate("mainmenu")}>
              Return to menu
            </button>
          )}
        </div>
      </div>
    );
  }
}
