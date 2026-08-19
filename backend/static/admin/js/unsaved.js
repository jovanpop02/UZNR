/* Warns before leaving a form with unsaved edits.
 *
 * Django's admin lets a half-filled form vanish without a word: click a link in
 * the sidebar, press Back, close the tab, and the work is gone. This watches
 * the change form and speaks up only when something has actually been typed.
 *
 * Deliberately quiet in three cases, because each is a save rather than a loss:
 * submitting the form, following a link that Django itself marks as part of the
 * editing flow, and the browser's own reload after a validation error.
 */
(function () {
  'use strict';

  function init() {
    var form = document.querySelector('#content-main form');
    if (!form) {
      return;
    }

    var dirty = false;
    var submitting = false;

    /* Both events, and every field: `change` alone misses a paragraph typed
       into a textarea that never loses focus, which is the loss most worth
       preventing. Neither event fires from merely tabbing through a form. */
    function markDirty() {
      dirty = true;
    }

    form.addEventListener('input', markDirty);
    form.addEventListener('change', markDirty);

    form.addEventListener('submit', function () {
      submitting = true;
    });

    /* Deleting is its own confirmed flow and must not be nagged at. */
    document.querySelectorAll('.deletelink, .row-delete').forEach(function (link) {
      link.addEventListener('click', function () {
        submitting = true;
      });
    });

    window.addEventListener('beforeunload', function (event) {
      if (!dirty || submitting) {
        return;
      }
      /* Browsers show their own wording and ignore ours; returning any value is
         what triggers the prompt. */
      event.preventDefault();
      event.returnValue = '';
      return '';
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
