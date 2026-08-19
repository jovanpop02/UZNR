// Remembers whether the "Kako se koristi" panel on the admin home page is open.
//
// The panel is worth reading once and costs about a third of the fold every
// visit after that. It ships open, so a first-time visitor still sees it; once
// somebody folds it away it stays folded until they open it again.
//
// The preference is per browser, not per account: it is a display nicety, not
// something worth a column in the database.

(function () {
  'use strict';

  var KEY = 'uznr-admin-guide-open';

  document.addEventListener('DOMContentLoaded', function () {
    var guide = document.querySelector('details.uznr-guide');
    if (!guide) return;

    var stored;
    try {
      stored = window.localStorage.getItem(KEY);
    } catch (e) {
      // Private mode, or storage disabled by policy. The panel simply keeps
      // its server-rendered state.
      return;
    }

    if (stored === 'closed') {
      guide.open = false;
    } else if (stored === 'open') {
      guide.open = true;
    }

    guide.addEventListener('toggle', function () {
      try {
        window.localStorage.setItem(KEY, guide.open ? 'open' : 'closed');
      } catch (e) {
        /* nothing to do: the panel still works, it just will not be remembered */
      }
    });
  });
})();
