/* Drag-to-reorder for the UZNR admin.
 *
 * Two kinds of table need it, and they save in different ways:
 *
 *   1. Changelists (Oglasi, Vazni linkovi). There is no form to submit, so a
 *      drop POSTs the new sequence of row ids to the ModelAdmin's reorder/
 *      endpoint and the change is live immediately.
 *
 *   2. Inline tables inside a change form (sections, items, gallery photos,
 *      announcement documents). These already have an `order` input per row, so
 *      a drop renumbers those inputs from the top and the new order is saved
 *      with the rest of the form — nothing is written until Sacuvaj is pressed,
 *      which is what the surrounding form leads people to expect.
 *
 * Built on pointer events rather than HTML5 drag-and-drop. Pointer events carry
 * touch and pen as well as mouse, so the same grip works on a tablet, and they
 * let the row follow the finger from the moment it moves instead of waiting for
 * the browser's drag threshold.
 *
 * The order inputs stay in the DOM and are only hidden with CSS, so a browser
 * with JS disabled still shows plain editable numbers.
 */
(function () {
  'use strict';

  var DRAG_THRESHOLD = 4; /* px before a press becomes a drag, so clicks survive */

  function csrfToken() {
    var match = document.cookie.match(/(^|;)\s*csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[2]) : '';
  }

  /* Django's "add another" row is a template, never a real position. */
  function isTemplateRow(row) {
    return /empty-form|add-row/.test(row.className);
  }

  function rowsOf(tbody) {
    return Array.prototype.filter.call(tbody.children, function (row) {
      return row.tagName === 'TR' && !isTemplateRow(row);
    });
  }

  /* The row the dragged one should sit in front of.
   *
   * A stacked table only needs the pointer's y. The photo gallery lays its rows
   * out as a grid, where several cards share a line, so there the card's
   * position on that line matters too — otherwise a photo dropped to the right
   * of another would land in front of it.
   */
  function rowAfterPoint(tbody, dragged, x, y) {
    var isGrid = window.getComputedStyle(tbody).display === 'grid';
    var others = rowsOf(tbody).filter(function (row) {
      return row !== dragged;
    });

    for (var i = 0; i < others.length; i++) {
      var box = others[i].getBoundingClientRect();
      var midY = box.top + box.height / 2;

      if (!isGrid) {
        if (y < midY) {
          return others[i];
        }
        continue;
      }

      /* Reading order: a card on a line below is always after; on the same
         line, the one further right is after. */
      var onLineBelow = y < box.top;
      var onSameLine = y >= box.top && y <= box.bottom;
      if (onLineBelow || (onSameLine && x < box.left + box.width / 2)) {
        return others[i];
      }
    }
    return null;
  }

  /* Fields you type into or toggle. A press that lands on one of these is
     someone editing, never someone reordering, so it is left alone. Links are
     deliberately NOT in this list: a row is dragged by grabbing anywhere on it,
     including its title link, and a drag that started on a link suppresses the
     click it would otherwise have fired. */
  function isEditable(target) {
    return !!target.closest('input, textarea, select, button, label');
  }

  /* Slide the other rows to their new places instead of letting them jump.
   *
   * FLIP: measure where every row sits before the move (First), do the move,
   * measure again (Last), then start each row from the difference (Invert) and
   * let a transition carry it to zero (Play). The rows are never actually
   * animated out of position — they are already correct, and the transform is
   * only the trip there — so nothing has to be undone if a drag is abandoned.
   */
  function animateReflow(tbody, mutate) {
    var moving = rowsOf(tbody);
    var before = moving.map(function (row) {
      return row.getBoundingClientRect().top;
    });

    mutate();

    moving.forEach(function (row, index) {
      var delta = before[index] - row.getBoundingClientRect().top;
      if (!delta || row.classList.contains('is-dragging')) {
        return;
      }
      row.style.transition = 'none';
      row.style.transform = 'translateY(' + delta + 'px)';
      /* Force the browser to accept the start position before transitioning. */
      void row.offsetHeight;
      row.style.transition = 'transform 160ms ease';
      row.style.transform = '';
    });
  }

  function clearReflow(tbody) {
    rowsOf(tbody).forEach(function (row) {
      row.style.transition = '';
      row.style.transform = '';
    });
  }

  /* Keep the list moving when the pointer is held near the top or bottom of the
     window, so a row can be dragged past the edge of a long list. */
  function edgeScroll(y) {
    var margin = 70;
    var speed = 14;
    if (y < margin) {
      window.scrollBy(0, -speed);
    } else if (y > window.innerHeight - margin) {
      window.scrollBy(0, speed);
    }
  }

  function enableDragging(tbody, onDrop) {
    /* Links and images are natively draggable. Pulling one starts the browser's
       own drag-and-drop, which cancels our pointer stream mid-gesture — the row
       then stops following the cursor while the drop still fires. Killing
       dragstart here keeps the whole row grabbable, title link included, and
       leaves ordinary clicks untouched. */
    tbody.addEventListener('dragstart', function (event) {
      event.preventDefault();
    });

    tbody.addEventListener('pointerdown', function (event) {
      if (event.button !== 0) {
        return;
      }
      var row = event.target.closest('tr');
      if (!row || !tbody.contains(row) || tbody.closest('.reorder-disabled')) {
        return;
      }
      if (isEditable(event.target)) {
        return;
      }
      if (isTemplateRow(row)) {
        return;
      }

      /* Not preventDefault() here: that would kill the click on the row's link
         before we know whether this is a click or a drag. Text selection is
         suppressed by the .is-reordering class once a drag actually starts. */

      var startY = event.clientY;
      var moved = false;
      var scroller = null;
      var lastY = startY;
      var lastX = event.clientX;

      function onMove(moveEvent) {
        lastY = moveEvent.clientY;
        lastX = moveEvent.clientX;
        if (!moved) {
          if (Math.abs(lastY - startY) < DRAG_THRESHOLD) {
            return;
          }
          moved = true;
          row.classList.add('is-dragging');
          document.body.classList.add('is-reordering');
          scroller = window.setInterval(function () {
            edgeScroll(lastY);
          }, 30);
        }
        var next = rowAfterPoint(tbody, row, lastX, lastY);
        if (next !== row.nextElementSibling) {
          animateReflow(tbody, function () {
            tbody.insertBefore(row, next);
          });
        }
      }

      function onUp() {
        document.removeEventListener('pointermove', onMove);
        document.removeEventListener('pointerup', onUp);
        document.removeEventListener('pointercancel', onUp);
        if (scroller) {
          window.clearInterval(scroller);
        }
        row.classList.remove('is-dragging');
        document.body.classList.remove('is-reordering');
        clearReflow(tbody);
        if (moved) {
          /* The press began on the row and may have begun on its link. Swallow
             the click that is about to follow, so reordering never navigates
             away from the list you are reordering. */
          window.addEventListener(
            'click',
            function (clickEvent) {
              clickEvent.preventDefault();
              clickEvent.stopPropagation();
            },
            { capture: true, once: true }
          );
          /* A short highlight on the row that just landed, so the eye can find
             where it ended up in a long list. */
          row.classList.add('just-dropped');
          window.setTimeout(function () {
            row.classList.remove('just-dropped');
          }, 700);
          onDrop(tbody);
        }
      }

      document.addEventListener('pointermove', onMove);
      document.addEventListener('pointerup', onUp);
      document.addEventListener('pointercancel', onUp);
    });
  }

  /* ---- 1. Changelist: save straight away ---- */

  var CHANGELIST_HINT =
    'Uhvatite bilo koji red i prevucite ga gore ili dolje da promijenite redoslijed prikaza na sajtu.';

  function initChangelist() {
    var table = document.getElementById('result_list');
    /* The marker is printed by the changelist template only for admins that
       expose a reorder endpoint. Without grips there is nothing in the table
       itself to detect, so this is what says "these rows can be dragged". */
    if (!table || !document.getElementById('uznr-reorder-list')) {
      return;
    }
    var tbody = table.tBodies[0];
    if (!tbody) {
      return;
    }
    table.classList.add('is-reorderable');

    var note = document.createElement('p');
    note.className = 'reorder-note';
    table.parentNode.insertBefore(note, table);

    /* Positions only mean something in the stored order. If the list has been
       sorted by a column, dragging would describe a sequence no visitor sees,
       so say that instead of silently saving something wrong. */
    if (/[?&]o=/.test(window.location.search)) {
      table.classList.add('reorder-disabled');
      note.className = 'reorder-note reorder-note--off';
      note.textContent =
        'Redoslijed se mijenja prevlačenjem samo u osnovnom prikazu. ' +
        'Poništite sortiranje po koloni da biste ponovo mogli prevlačiti.';
      return;
    }

    note.textContent = CHANGELIST_HINT;

    function idOf(row) {
      var box = row.querySelector('input[name="_selected_action"]');
      if (box) {
        return box.value;
      }
      /* No action checkboxes on this list: fall back to the edit link's pk. */
      var link = row.querySelector('a[href*="/change/"]');
      var match = link && link.getAttribute('href').match(/\/(\d+)\/change\//);
      return match ? match[1] : null;
    }

    function save() {
      var ids = rowsOf(tbody).map(idOf).filter(Boolean);
      if (!ids.length) {
        return;
      }

      note.className = 'reorder-note is-busy';
      note.textContent = 'Čuvanje…';

      fetch('reorder/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken()
        },
        credentials: 'same-origin',
        body: JSON.stringify({ ids: ids })
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error(response.status);
          }
          note.className = 'reorder-note is-saved';
          note.textContent = 'Redoslijed sačuvan.';
          window.setTimeout(function () {
            note.className = 'reorder-note';
            note.textContent = CHANGELIST_HINT;
          }, 2000);
        })
        .catch(function () {
          note.className = 'reorder-note is-error';
          note.textContent = 'Čuvanje nije uspjelo. Osvježite stranicu i pokušajte ponovo.';
        });
    }

    enableDragging(tbody, save);
  }

  /* ---- 2. Inlines: renumber, save with the form ---- */

  function renumber(tbody) {
    rowsOf(tbody).forEach(function (row, index) {
      var input = row.querySelector('input[name$="-order"]');
      if (input) {
        input.value = index;
      }
    });
  }

  function initInlines() {
    document.querySelectorAll('.reorderable table').forEach(function (table) {
      var tbody = table.tBodies[0];
      if (tbody && tbody.querySelector('input[name$="-order"]')) {
        table.classList.add('is-reorderable');
        enableDragging(tbody, renumber);
      }
    });
  }

  /* ---- 3. Show what ticking "Brisanje?" is about to remove ---- */

  /* The delete checkbox in an inline does nothing until the form is saved, and
     until then a ticked row looks exactly like a kept one. Marking the row lets
     you see the whole set of pending removals before pressing Sacuvaj. */
  function initInlineDeletes() {
    document.addEventListener('change', function (event) {
      var box = event.target;
      if (box.type !== 'checkbox' || !/-DELETE$/.test(box.name || '')) {
        return;
      }
      var row = box.closest('tr');
      if (row) {
        row.classList.toggle('marked-for-delete', box.checked);
      }
    });

    /* A form that failed validation comes back with boxes still ticked. */
    document.querySelectorAll('input[type="checkbox"][name$="-DELETE"]').forEach(
      function (box) {
        if (box.checked) {
          var row = box.closest('tr');
          if (row) {
            row.classList.add('marked-for-delete');
          }
        }
      }
    );
  }

  document.addEventListener('DOMContentLoaded', function () {
    initChangelist();
    initInlines();
    initInlineDeletes();
  });
})();
