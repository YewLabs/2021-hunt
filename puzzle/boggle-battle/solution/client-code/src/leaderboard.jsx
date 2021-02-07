const HISCORE_SCALE = 100000;

export default class Leaderboard extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let contents = <tr><td>Loading...</td></tr>;
    if (this.props.hiscores != null) {
      contents = [];
      for (const entry of this.props.hiscores) {
        contents.push(
          <tr key={entry[0]}>
            <td>{entry[0]}</td>
            <td>{((entry[1] / HISCORE_SCALE) * 100).toFixed(2)}%</td>
          </tr>
        );
      }
    }
    const buttons = [];
    for (let i = 0; i < 4; i++) {
      if (i <= this.props.maxlevel) {
        buttons.push(
          <button
            key={i}
            onClick={(e) => {
              this.props.onlevel(i);
            }}
          >
            Level {i + 1}
          </button>
        );
      }
    }
    return (
      <div className="leaderboard">
        <div className="levels">{buttons}</div>
        <table>
          <tbody>
            <tr>
              <th>Team</th>
              <th>Percent max</th>
            </tr>
            {contents}
          </tbody>
        </table>
        <button onClick={this.props.navigate("mainmenu")}>
          Return to menu
        </button>
      </div>
    );
  }
}
