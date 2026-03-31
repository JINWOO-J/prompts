/**
 * diff-helpers.js — Shared diff rendering module
 *
 * Interface:
 *   window._diffHelpers.renderDiff(oldText, newText) — returns diff HTML string
 */
(function () {
  'use strict';

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /**
   * Render a unified diff between two texts using jsdiff.
   * @param {string} oldText — original text
   * @param {string} newText — new text
   * @returns {string} HTML string with .diff-added, .diff-removed, .diff-unchanged classes
   */
  function renderDiff(oldText, newText) {
    if (typeof Diff === 'undefined') {
      return '<pre>' + escapeHtml(newText) + '</pre>';
    }

    var diff = Diff.diffLines(oldText || '', newText || '');
    var html = '<div class="diff-container">';

    diff.forEach(function (part) {
      var cls = part.added ? 'diff-added' : part.removed ? 'diff-removed' : 'diff-unchanged';
      html += '<div class="' + cls + '">' + escapeHtml(part.value) + '</div>';
    });

    html += '</div>';
    return html;
  }

  // Global exposure
  window._diffHelpers = {
    renderDiff: renderDiff
  };
})();
