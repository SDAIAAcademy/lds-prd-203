/* Solution state of lab 3.1: focus moves into the confirmation dialog, Esc closes it, and
   focus returns to the button that opened it. Loaded after ../../prototype/app.js. */
(function () {
  var opener = null;
  window.App = window.App || {};
  window.App.onDialogOpen = function () {
    opener = document.activeElement;
    document.getElementById('confirm-yes').focus();
  };
  window.App.onDialogClose = function () {
    if (opener && opener.focus) opener.focus();
  };
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.getElementById('confirm-dialog').classList.contains('open')) window.App.closeConfirm();
  });
})();
