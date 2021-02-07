class ManualRenderer {
  constructor(data, manual) {
    this.data = data;
    this.manual = manual;
    // generate talk tables
    if (this.manual.talk && this.data.manual?.talk?.length === 1) {
      const n_talk_pages = Math.ceil(this.manual.talk.length / 10);
      for (let i = 0; i < n_talk_pages; i++) {
        this.data.manual.talk.push([{ table: `talk${i}` }]);
      }
    }
    // generate sequential tables
    if (this.manual.buttons && this.data.manual?.buttons?.length === 5) {
      const n_talk_pages = Math.ceil(this.manual.buttons.sequential.length / 2);
      for (let i = 0; i < n_talk_pages; i++) {
        this.data.manual.buttons.push([{ table: `sequential${i}` }]);
      }
    }
  }

  capitalize(s) {
    return s[0].toUpperCase() + s.slice(1);
  }

  name(obj) {
    return this.data.objects[obj] ?? obj;
  }

  image(name, size) {
    return `<img src="${this.data.images[name]}"${
      size ? ` style="width: ${size}px"` : ""
    }/>`;
  }

  list(objs) {
    const items = objs.map((x) => `  <li>${x}</li>`).join("\n");
    return `<ul>\n${items}\n</ul>`;
  }

  table(header, rows) {
    let head = "";
    if (header.length > 0) {
      const headr = header.map((hd) => `    <th>${hd}</th>`).join("\n");
      head = `  <tr>\n${headr}\n  </tr>`;
    }
    const body = rows
      .map((rw) => {
        const tr = rw.map((cl) => `    <td>${cl}</td>`).join("\n");
        return `  <tr>\n${tr}\n  </tr>`;
      })
      .join("\n");
    return `<div class="table-wrapper"><table>\n${head}\n${body}\n</table></div>`;
  }

  condition(cond) {
    if (cond === "") return "otherwise";
    if (cond.and || cond.or) {
      const op = cond.and ? "and" : "or";
      const [cd1, cd2] = cond[op].map((cd) => this.condition(cd));
      return `${cd1} ${op} ${cd2}`;
    }
    if (cond.not?.or) {
      const [cd1, cd2] = cond.not.or.map((cd) => this.condition(cd));
      return `neither ${cd1} nor ${cd2}`;
    }
    const neg = cond.not;
    const is = neg ? "isn't" : "is";
    const has = neg ? "doesn't have" : "has";
    cond = neg ? cond.not : cond;
    if (cond.gravity) {
      return `the text ${is} ${cond.gravity}`;
    } else if (cond.even || cond.odd) {
      const parity = cond.even ? "even" : "odd";
      return `${this.name(cond[parity])} ${is} ${parity}`;
    } else if (cond["serial has"]) {
      return `the serial code ${has} a ${cond["serial has"]}`;
    } else if (cond.range) {
      const obj = this.name(cond.range.obj);
      let min = cond.range?.min;
      let max = cond.range?.max;
      if (cond.range.obj === "month") {
        min = this.data.months[min];
        max = this.data.months[max];
      }
      if (min !== undefined && max !== undefined) {
        if (min === max) {
          return `${obj} ${is} ${min}`;
        } else {
          return `${obj} ${is} between ${min} and ${max} inclusive`;
        }
      } else if (min !== undefined) {
        return `${obj} ${is} at least ${min}`;
      } else if (max !== undefined) {
        return `${obj} ${is} at most ${max}`;
      }
    }
    throw "unknown condition";
  }

  makeTable(name) {
    if (name === "intro") {
      return this.table(
        [],
        [
          ["I", "Intro", "G", "Gravity Sensor"],
          ["S", "Shake It", "6", "Six Lights"],
          ["T", "Talk", "W", "Wires"],
          ["B", "Buttons", "P", "Passwords"],
          ["C", "Cube", "D", "Directions"],
        ]
      );
    } else if (name === "gravity") {
      return this.table(
        ["If...", "Direction"],
        this.manual.gravity.map(({ condition, direction }) => [
          this.condition(condition),
          this.name(direction),
        ])
      );
    } else if (name === "six") {
      return this.table(
        ["If...", "Order"],
        this.manual.six.map(({ condition, direction }) => [
          this.condition(condition),
          `${this.name(direction).slice(0, 3)}<br/>${this.name(direction).slice(
            3,
            6
          )}`,
        ])
      );
    } else if (name.slice(0, 4) === "talk") {
      const i = Number(name.slice(4));
      return this.table(
        ["Text", "Press"],
        this.manual.talk
          .slice(i * 10, (i + 1) * 10)
          .map(({ text, press }) => [text, press])
      );
    } else if (name === "wires") {
      return this.table(
        ["Wire", "Direction"],
        this.manual.wires.table.map(({ wire, direction }) => [
          this.name(wire),
          direction.map((o) => this.name(o)).join(", "),
        ])
      );
    } else if (name.slice(0, 10) === "sequential") {
      const i = Number(name.slice(10));
      return this.table(
        ["If...", "Press"],
        this.manual.buttons.sequential
          .slice(i * 2, (i + 1) * 2)
          .map(({ condition, buttons }) => [
            this.condition(condition),
            buttons.join(", "),
          ])
      );
    } else if (name === "simultaneous1") {
      return this.table(
        ["If...", "Press"],
        this.manual.buttons.simultaneous.table.map(
          ({ condition, instruction }) => [
            this.condition(condition),
            [
              `${this.name(instruction.modules)} modules`,
              this.name(instruction.category),
            ].join(", "),
          ]
        )
      );
    } else if (name === "simultaneous2") {
      return this.table(
        ["Category", "Buttons"],
        this.manual.buttons.simultaneous.categories.map(
          ({ category, buttons }) => [this.name(category), buttons.join(", ")]
        )
      );
    } else if (name === "passwords") {
      return this.table(
        [],
        ((arr) => {
          let res = [];
          for (let i = 0; i < arr.length + 4; i += 4) {
            res.push(arr.slice(i, i + 4));
          }
          return res;
        })(this.manual.passwords.words)
      );
    }
  }

  getPage(page) {
    return this.data.manual[this.manual["module"]][page]
      .map((tg) => {
        if (tg.list) {
          return this.list(tg.list.map((li) => eval("`" + li + "`")));
        } else if (tg.table) {
          return this.makeTable(tg.table);
        } else if (tg.img) {
          return this.image(tg.img, tg.size);
        }
        const tag = Object.keys(tg)[0];
        return `<${tag}>${eval("`" + tg[tag] + "`")}</${tag}>`;
      })
      .join("\n");
  }

  getNumPages() {
    return this.data.manual[this.manual["module"]].length;
  }
}

export { ManualRenderer };
