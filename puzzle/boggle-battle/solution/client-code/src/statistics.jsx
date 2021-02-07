export default class Statistics extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let highestScoringWordsDom = [];
    for (const entry of this.props.stats.highest_scoring) {
      highestScoringWordsDom.push(<div key={entry[0]}>{entry[0]} {entry[1]}</div>);
    }
    let levelStatsDom = [];
    for (let i = 0; i < 4; i++) {
      const bestScore = this.props.stats.best_score[i];
      const bestNumWords = this.props.stats.best_num_words[i];
      if (bestScore != null && bestNumWords != null) {
        levelStatsDom.push(<div key={i}>
          Level {i+1}: best score {(bestScore*100).toFixed(2)}%, best num words {(bestNumWords*100).toFixed(2)}%
        </div>);
      }
    }
    return (
      <div className="statistics">
        <div style={{
          marginBottom: "20px",
          textAlign: "center",
        }}>
          <div>
            Number of games played: { this.props.numgames }
          </div>
          <div>
            Total words found: { this.props.stats.tot_words }
          </div>
          <div style={{
            marginTop: "10px",
            marginBottom: "10px",
          }}>
            { levelStatsDom }
          </div>
          <div>
            Highest scoring words:
          </div>
          { highestScoringWordsDom }
        </div>
        <button onClick={this.props.navigate("mainmenu")}>
          Return to menu
        </button>
      </div>
    );
  }
}
