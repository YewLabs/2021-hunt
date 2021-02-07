const debug = false;
function dlog(msg) {
    if (debug) { console.log(msg); }
};

const pronouns = {
    "subject-pronoun": {"he": "he", "she": "she", "they": "they", "it": "it"},
    "possessive": {"he": "his", "she": "her", "they": "their", "it": "its"},
    "object-pronoun": {"he": "him", "she": "her", "they": "them", "it": "it"},
    "contracted-subject": {"he": "he’s", "she": "she’s", "they": "they’re", "it": "it’s"},
};

const authToken = JSON.parse(document.getElementById('auth-token').textContent);
const elt = document.getElementById('virtual-auth-token');
const virtualAuthToken = elt ? JSON.parse(elt.textContent) : null;

const choiceMsg = `
If you would like to solve the virtual version of the puzzle,
submit <span class="answer">I WANT VIRTUAL BACON</span> for your pig’s name.
`;
const virtualMsg = `You are solving the virtual version of the puzzle.`;

const socket = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://") +
    `${window.location.host}/ws/puzzle/squee-squee`);

function refresh() {
    socket.send(JSON.stringify({'type': 'refresh', 'virtual-auth': virtualAuthToken}));
}


socket.onopen = function(e) {
    socket.send(JSON.stringify({'type': 'AUTH', 'data': authToken}));
    refresh();
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    dlog(data);
    if (data.type == "refresh_request") {
        refresh();
    } else if (data.type == "refresh") {
        if (data.selection == "physical")
            document.getElementById("fourthwall-message").innerHTML = '';
        else if (data.selection == "virtual")
            document.getElementById("fourthwall-followup").innerHTML = virtualMsg;
        else
            document.getElementById("fourthwall-followup").innerHTML = choiceMsg;
        document.getElementById('puzzle-content').innerHTML = data.content;
        start_timers();
        runScripts(document.getElementById('puzzle-content'));
    } else if (data.type == "pronoun") {
        setPronoun(data.pronoun);
    } else if (data.type == "incorrect_guess") {
        document.getElementById("response").innerHTML = data.msg; 
    } else if (data.type == "coin") {
        setCoin(data.coin, data.count);
    }
}

function str_to_sec(s) {
    let res = s.split(':');
    return 60*parseInt(res[0]) + parseInt(res[1]);
}

function sec_to_str(sec) {
    let m = Math.floor(sec / 60);
    let s = sec % 60;
    return m + ":" + String(s).padStart(2, '0');
}

function start_timers() {
    let timers = document.getElementsByClassName('timer');
    for (let i = 0; i < timers.length; i++) {
        let timer =  setInterval(function () {
            let remaining_time = str_to_sec(timers[i].innerHTML);
            if (remaining_time <= 0) {
                clearInterval(timer);
                refresh();
            } else {
                timers[i].innerHTML = sec_to_str(remaining_time-1);
            }
        }, 1000);
    }
}

function updatePronoun() {
    let pronoun = document.getElementById("pronoun").value;
    setPronoun(pronoun);
    socket.send(JSON.stringify({'type': 'pronoun', 'pronoun': pronoun}));
}

function setPronoun(pronoun) {
    document.getElementById("pronoun").value = pronoun;
    for (const type in pronouns) {
        let to_update = document.getElementsByClassName(type);
        for (let i = 0; i < to_update.length; i++)
            to_update[i].innerHTML = pronouns[type][pronoun];
    }
    let to_update = document.getElementsByClassName("capital");
    for (let i = 0; i < to_update.length; i++) {
        let val = to_update[i].innerHTML;
        to_update[i].innerHTML = val.charAt(0).toUpperCase() + val.slice(1);
    }
    let to_conjugate = document.getElementsByClassName("conjugate");
    for (let i = 0; i < to_conjugate.length; i++) {
        to_conjugate[i].innerHTML = pronoun == "they" ? '' : 's';
    }
}

function doIt() {
    socket.send(JSON.stringify({'type': 'doIt'}));
}

function rename() {
    socket.send(JSON.stringify({'type': 'rename'}));
}

function reset() {
    socket.send(JSON.stringify({'type': 'reset'}));
}

function makeGuess() {
    socket.send(JSON.stringify({
        'type': 'guess',
        'guess': document.getElementById("guess").value,
    }));
}

function coins(coin, count) {
    socket.send(JSON.stringify({
        'type': 'coin',
        'coin': coin,
        'count': count,
    }));
}

function runScripts(elt) {
    Array.from(elt.getElementsByTagName("script")).forEach((e) => {
        const scr = document.createElement("script");
        scr.text = e.innerHTML;
        e.src && scr.setAttribute("src", e.src);
        e.parentNode.replaceChild(scr, e);
    });
}

const gcnz = (c) => document.getElementsByClassName(c)[0];
const gid = (i) => document.getElementById(i);
let interacted = false;
let declare_vars = false;
