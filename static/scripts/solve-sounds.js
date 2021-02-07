function playSound(round, link, ismeta) {
  updateVolume(localStorage.getItem("volume"));
  var delay;
  if (document.hasFocus()) {
    delay = Math.random() * 100;
  }
  else {
    delay = Math.random() * 1500 + 1000;
  }
  const s = round.toLowerCase();
  const a = s.charCodeAt(1);
  const b = s.charCodeAt(2);
  var h = (a+2*b) % 24;

  if (ismeta && link[8] == 'e' && h == 14) {
    h--;
  }

  const volume = parseInt(localStorage.getItem("volume"));
  if (volume == 0) {
    return;
  }
  const filename = '/static/audio/' + h + '.mp3';
  const trigger_time = Date.now();
  let audio = new Audio(filename);
  audio.volume = volume / 200;

  setTimeout(function() {
    const now = Date.now(); // current time in milliseconds
    const last_sound_time = localStorage.getItem("last_sound");
    if (last_sound_time != null && now - last_sound_time < 7000) {
      return;
    }
    if (now - trigger_time > 15000) {
      return;
    }
    audio.onplay = function() {
      localStorage.setItem("last_sound", now);
    }
    audio.play()
  }, delay);
}

function updateVolume(volume) {
  $("#volume-slider").val(volume);
  $("#volume-output").html(volume);
  localStorage.setItem("volume", parseInt(volume));
  if (volume > 0) {
    $("#volume-icon-on").show();
    $("#volume-icon-off").hide();
  }
  else {
    $("#volume-icon-on").hide();
    $("#volume-icon-off").show();
  }
}

function enableVolumeSlider() {
  var volume = 100;
  try {
    volume = localStorage.getItem("volume");
  } catch {}
  if (volume == null) {
    volume = 100;
  }
  updateVolume(volume);
  $("#volume-slider").val(volume);
  $("#volume-slider").on('change', function() {
    updateVolume($("#volume-slider").val());
  });
  $("#volume-slider").on('input', function() {
    $("#volume-output").html($("#volume-slider").val());
  });
}
