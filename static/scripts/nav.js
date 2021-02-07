function enableDropdowns() {
  $('.nav-links-dropdown-toggle').each(function(i, elt) {
    $(elt).click(function(evt) {
      $('.nav-links-dropdown-toggle').each(function(j, e) {
        // hide others
        if (e != elt) {
          $(e).next().hide();
        }
      });
      $(elt).next().toggle();
      evt.preventDefault();
    });
    $(elt).parent().click(function(evt) {
      evt.stopPropagation();
    });
    $(window).click(function(evt) {
      $(elt).next().hide();
    });
  });
}

function enableBookmarks(puzzles, current, data) {
  var bookmarks = {};
  try {
    bookmarks = JSON.parse(localStorage.bookmarks);
  } catch {}
  function update() {
    var menu = $('#bookmarks ul').empty();
    var found = false;
    for (var url in bookmarks) {
      var a = $('<a>').attr('href', bookmarks[url].link).text(bookmarks[url].name);
      if (puzzles[url]) a.prepend($('<span>').text('(solved!)'));
      $('<li>').append(a).prependTo(menu);
      found = true;
    }
    if (!found) {
      menu.append($('<div>').append('You have no bookmarks. To add a bookmark, click the bookmark icon at the upper-right corner of any puzzle page.').addClass('no-bookmarks'));
    }
  }
  update();
  if (current) {
    $('#bookmark').show().click(function(evt) {
      evt.preventDefault();
      if (current in bookmarks) {
        delete bookmarks[current];
      } else {
        bookmarks[current] = data;
      }
      $(this).toggleClass('bookmarked', current in bookmarks);
      update();
      localStorage.bookmarks = JSON.stringify(bookmarks);
    }).toggleClass('bookmarked', current in bookmarks);
  }
}

function enableIframes() {
  $('nav a').click(function(evt) {
    if (this.getAttribute('href').startsWith('/submit/')) {
      evt.preventDefault();
      var target_url = '/embed' + this.getAttribute('href');
      if ($('#submit-popup').attr('src') == target_url) {
        $('#submit-popup,#submit-popup-close').toggle();
      } else {
        $('#submit-popup').attr('src', target_url).show();
        $('#submit-popup-close').show();
      }
      $('.nav-links-dropdown-menu').hide();
    }
  });
  $('#submit-popup-close').click(function() {
    $('#submit-popup,#submit-popup-close').hide();
  });
}

function enableNotifications(auth) {
  if (!auth) return;
  if (typeof SharedWorker != 'function') return;
  var notificationsWorker = new SharedWorker('/static/scripts/notify-worker.js?id=' + auth);
  notificationsWorker.port.addEventListener('message', function(e) {
    var data = JSON.parse(e.data);
    var container = $('<div>').addClass('notification').appendTo('#notifications');
    var button = $('<button>').text('×').appendTo(container);
    var toast = $('<a>').text(data.message).appendTo(container);
    if (data.link) toast.attr({href: data.link, target: '_blank'});
    if (data.special) container.addClass(data.special);
    container.slideUp(0).slideDown();
    if (timer) clearTimeout(timer);
    timer = setTimeout(function() {
      timer = null;
      $('#notifications .notification:not(.important)').remove();
    }, 10 * 1000);
    container.click(function() { container.remove(); });
    if (
      data.event_type == 'puzzle-solved'
      || data.event_type == 'metapuzzle-solved'
    ) {
      const i = data.message.lastIndexOf("(");
      const round = data.message.slice(i+1, data.message.length-1);
      const link = data.link;
      playSound(round, link, data.event_type == 'metapuzzle-solved');
    }
  });
  var timer = null;
  notificationsWorker.port.start();
  var url = (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host + '/ws/team';
  notificationsWorker.port.postMessage({action: 'auth', value: {url: url, auth: auth}});
  window.addEventListener('beforeunload', function() {
    notificationsWorker.port.postMessage({action: 'unload', value: null});
    notificationsWorker.port.close();
  });
}
