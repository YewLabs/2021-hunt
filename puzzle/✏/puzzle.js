// hi! this puzzle is not intended to be reverse engineered. thanks

const questions = [
  "-",
  "🔟✖️🔟",
  "🗿📄✂️🦎❓",
  "😀😨🤮😢❓",
  "🍞➕🥬➕🥩➕🧀➕🍞",
  "🧑👔⬆️🪄✨",
  "🧑🧑🐰👂👂",
  "🌝➖🌖",
  "🇧🇸🇹🇩🇬🇭🇯🇵🇰🇿🇲🇬🇲🇹🇵🇦🇶🇦🇷🇼❓",
  `🥝➕🥝➕🥝↔️9️⃣
🥝➕5️⃣↔️🍍➕🍍
🥝➕🍍↔️🥥➕1️⃣
🥥↔️❓
`,
  `🍓➕🍓➕🍓↔️🍏➕🍏➕🍌➕9️⃣
🍏➕🍌➕🍇↔️5️⃣
🍏➕🍏➕🍏➕🍇↔️🍓➕2️⃣
🍌➕🍓➕🍇↔️8️⃣
🍏↔️❓
`,
  "🐝🌧️    5️⃣",
  "🐀🐀🔙    4️⃣",
  "🔚☄️🔀🥕    7️⃣",
  "🕘🕜🕢🕥🕜",
  "🍬🍬🍬🚴🌕👉✨    1️⃣9️⃣8️⃣2️⃣",
  "👁📼📺7️⃣🗓☠️    2️⃣0️⃣0️⃣2️⃣",
  "⬆↗⬆⬆⬅⬅↙⬅⬆↗↖⬆➡↘➡➡⬆⬆↖⬆➡↘↘⬇↘➡➡↘↙⬅⬅↙⬇↙↙⬅",
  "👏👏👏 📞➡️📧ⓜ️⭕🗾ℹ️",
];

const answers = [
  "-",
  "💯",
  "🖖🖖🏻🖖🏼🖖🏽🖖🏾🖖🏿",
  "😠😡",
  "🥪🍔",
  "🕴",
  "👯",
  "🌛",
  "🇨🇦",
  "6️⃣",
  "🍌",
  "🧠",
  "⭐🌟",
  "🚜",
  "☮️✌🏾✌️✌🏻✌🏼✌🏽✌🏾✌🏿",
  "👽",
  "💍",
  "✈️",
  [],
];

const numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"];

function timeLeft(delta) {
  delta = Math.max(45 - Math.floor(delta / 1000), 1);
  return Array.from(delta.toString())
    .map((x) => numbers[Number(x)])
    .join("");
}

function getReply(level, lastTime, message) {
  const skip = level === 0;
  level = level === 0 ? 1 : level;
  const expectedAnswer = answers[level];
  const thisTime = Date.now();
  const rateLimit = lastTime && thisTime - lastTime < 45 * 1000;
  let prefix = "";
  let newTime = null;
  if (rateLimit) {
    prefix = `⏳⏳⏳❗ ${timeLeft(thisTime - lastTime)}🥈⌚`;
    newTime = lastTime;
  } else if (message && expectedAnswer.includes(message)) {
    level += 1;
    prefix = `${message}✅❗❗❗\n`;
  } else if (!skip && expectedAnswer) {
    prefix = `${message}❌\n`;
    newTime = Date.now();
  }
  const newMessage = rateLimit ? prefix : `${prefix}${questions[level]}`;
  return {
    level: level,
    lastTime: newTime,
    message: newMessage,
  };
}
