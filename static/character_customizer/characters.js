var focusCanvas = "1";
function showCharacterCustomizer(firstTime) {
  $('#character-popup').show();
  if (firstTime) $('#unityContainer').hide();
  event && event.preventDefault();
  focusCanvas = "0";
  updateUnity();
  Object.keys(choices).forEach((key) => {
    var element = $("#" + key + "-choices")[0];
    var checked = element.querySelector(":checked");
    if (checked) element.scrollLeft = checked.parentNode.offsetLeft + (checked.parentNode.offsetWidth - element.offsetWidth) / 2;
  });
}
function closeOverlay() {
  var name = $("#name").val().trim();
  if (!name) {
    alert("You have to set a name to go on!");
    return;
  }
  if (!RegExp($("#name").attr("pattern"), "u").test(name)) {
    alert("Unfortunately, due to technical limitations, the Projection Device does not support most non-Latin characters.");
    return;
  }
  localStorage.mmo_hair = hairNum;
  localStorage.mmo_face = faceNum;
  localStorage.mmo_name = name;
  localStorage.mmo_color_hair = shifts.hair;
  localStorage.mmo_color_visor = shifts.visor;
  localStorage.mmo_skin = skinNum;
  $('#character-popup').hide();
  $('#unityContainer').show();
  focusCanvas = "1";
  updateUnity();
}
function noclick() {
  event.stopPropagation();
}

var hairNum = 0;
var hairs = [
  "curly-buns",
  "half-pony",
  "korra-lol",
  "kpop",
  "long-curly",
  "pink",
  "short-basic",
  "short-curly",
  "short-straight",
  "shoulder-straight",
  "blue-hair",
  "med_vcurl",
  "mohawk",
  "med_straight",
  "med_wavy",
  "hitop",
  "long_str",
  "low_pony",
  "buzzcuts",
  "leafboy",
];
var faceNum = 0;
var faces = [
  "calm_smile_curious",
  "calm_smile_eyelids",
  "blank",
  "mischievous",
  "asian",
  "cat_eye",
  "cute_uwu",
  "blushy_cute",
  "cool",
  "cute",
  "sassy",
  "no_mouth",
  "dead_inside",
  "eye_bags",
  "eye_glints",
  "happy",
  "bashful",
  "pouty",
  "puffy_eyes",
  "rage",
  "disapprove",
  "shocked",
  "T_T",
  "teehee",
  "too_bad",
  "XD",
  "hou",
];
var skinNum = 0;
var skinColors = [
  "#ffd7c2",
  "#e0ae90",
  "#e2a669",
  "#94471b",
  "#492103",
];

function setHair(num) {
  hairNum = num;
  var imgurl = "url(" + characterUrlBase + "/hairs/" + hairs[hairNum] + ".png" + ")";
  var maskimgurl = "url(" + characterUrlBase + "/hairs/" + hairs[hairNum] + ".png" + ")";
  $("#hair").css({
    "background-image": imgurl,
    "-webkit-mask-image": maskimgurl,
    "mask-image": maskimgurl,
  });
}
function setFace(num) {
  faceNum = num;
  var imgurl = "url(" + characterUrlBase + "/faces/" + faces[faceNum] + ".png" + ")";
  var maskimgurl = "url(" + characterUrlBase + "/faces/" + faces[faceNum] + ".png" + ")";
  $("#face").css({
    "background-image": imgurl,
    "-webkit-mask-image": maskimgurl,
    "mask-image": maskimgurl,
  });
}
function setSkin(num) {
  skinNum = num;
  $("#skin").css("background-color", skinColors[skinNum]);
}

var choices = {
  hair: hairs,
  face: faces,
  skin: skinColors,
};
var shifts = {
  visor: localStorage.mmo_color_visor || '#00ff00',
  hair: localStorage.mmo_color_hair || randomColor(),
};

function onProgress(_, progress) {
  $('circle').css('stroke-dasharray', 314 * progress + ' 314');
  if (progress < 1) return;
  updateUnity();
  $('#loading').remove();
}
function updateUnity() {
  try {
    unityInstance.SendMessage("CharacterCustomization", "FocusCanvas", focusCanvas);
    unityInstance.SendMessage("CharacterCustomization", "setHair", hairs[hairNum]);
    unityInstance.SendMessage("CharacterCustomization", "setFace", faces[faceNum]);
    unityInstance.SendMessage("CharacterCustomization", "setHairColor", shifts.hair);
    unityInstance.SendMessage("CharacterCustomization", "setVisorColor", shifts.visor);
    unityInstance.SendMessage("CharacterCustomization", "setSkinBrightness", skinColors[skinNum]);
    unityInstance.SendMessage("CharacterCustomization", "setName", $("#name").val().trim());
  } catch {}
}
function teamColors() {
  var baseHue = (317.124 * teamId) % 360;
  var accentHue = (baseHue + 90 + 180 * ((8.9182 * teamId * teamId + teamId * 0.3) % 1)) % 360;
  var saturation = 0.2 + 0.6 * ((67.1338 * (teamId * teamId - 5.14 * teamId + 17)) % 1);
  var value = 0.65 + 0.25 * ((18.874 * (0.3 * teamId * teamId + 3.14 * teamId)) % 1);
  var lightness = value * (1 - saturation / 2) * 100;
  var s_l = (value - lightness) / Math.min(lightness, 1 - lightness) * 100;
  if (teamId < 100) {
    $("#clothes").css("background-color", "rgb(89, 102, 255)");
    $("#accents").css("background-color", "white");
  } else {
    $("#clothes").css("background-color", "hsl(" + baseHue + ", " + s_l + "%, " + lightness + "%)");
    $("#accents").css("background-color", "hsl(" + accentHue + ", 100%, 50%)");
  }
}
function randomColor() {
  var ret = '#';
  for (var i = 0; i < 6; ++i) ret += Math.floor(Math.random() * 0x10).toString(16);
  return ret;
}

$(document).ready(() => {
  setHair(+(localStorage.mmo_hair || Math.floor(Math.random() * hairs.length)));
  setFace(+(localStorage.mmo_face || Math.floor(Math.random() * faces.length)));
  setSkin(+(localStorage.mmo_skin || Math.floor(Math.random() * skinColors.length)));
  teamColors();

  Object.keys(choices).forEach((key) => {
    var element = $("#" + key + "-choices")[0];
    var handler;
    choices[key].forEach((choice, i) => {
      var radio = $("<input>").attr({type: "radio", name: key, value: i});
      var div = $("<div>");
      switch (key) {
        case "hair":
          div.css("background-image", "url(" + characterUrlBase + "/hairs/" + choice + ".png" + ")");
          handler = setHair;
          if (i == hairNum) radio[0].checked = true;
          break;
        case "face":
          div.css("background-image", "url(" + characterUrlBase + "/faces/" + choice + ".png" + ")");
          handler = setFace;
          if (i == faceNum) radio[0].checked = true;
          break;
        case "skin":
          div.css("background-color", choice);
          handler = setSkin;
          if (i == skinNum) radio[0].checked = true;
          break;
      }
      var button = $("<button>").append(div).click(() => {
        radio[0].checked = true;
        handler(i);
      });
      $("<label>").append(radio, button).appendTo(element);
    });
    var left = $(element).prev('.left').click(() => {
      element.scrollBy({left: -264, behavior: 'smooth'});
    });
    var right = $(element).next('.right').click(() => {
      element.scrollBy({left: 264, behavior: 'smooth'});
    });
    $(element).scroll(() => {
      left.toggleClass('noscroll', element.scrollLeft < 1);
      right.toggleClass('noscroll', element.scrollLeft + element.offsetWidth > element.scrollWidth - 1);
    });
  });

  Object.keys(shifts).forEach((key) => {
    $("#" + key + "color").on("input", (e) => {
      $("#" + key).css('background-color', e.target.value);
    });
    $("#" + key + "color").on("change", (e) => {
      shifts[key] = e.target.value;
    });
    $("#" + key + "color").on("cancel", () => {
      $("#" + key).css('background-color', shifts[key]);
    });
    $("#" + key + "color").val(shifts[key]);
    $("#" + key).css('background-color', shifts[key]);
  });

  if (localStorage.mmo_name) {
    $("#name").val(localStorage.mmo_name);
  } else {
    showCharacterCustomizer(true);
  }

  var lockout = false;
  $(".popup").mouseenter(function() {
    if (lockout || $(this).hasClass("chosen")) return;
    $(".chosen").removeClass("chosen");
    $(this).addClass("chosen");
    lockout = true;
    setTimeout(() => lockout = false, 100);
  });
});
