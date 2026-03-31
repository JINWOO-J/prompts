/**
 * suggestions.js — AI suggestion panel module
 *
 * Interface:
 *   PromptSuggestions.loadSuggestion(promptId)  — request AI suggestion and show panel
 *   PromptSuggestions.close()                    — close the suggestion panel
 */
(function () {
  'use strict';

  // DOM refs
  var suggestionPanel = document.getElementById('suggestion-panel');
  var suggestionLoading = document.getElementById('suggestion-loading');
  var suggestionContent = document.getElementById('suggestion-content');
  var suggestionActions = document.getElementById('suggestion-actions');
  var acceptBtn = document.getElementById('suggestion-accept-btn');
  var rejectBtn = document.getElementById('suggestion-reject-btn');

  // State
  var currentPromptId = null;
  var currentSuggestion = null;

  // --- Helpers (use app.js exposed helpers) ---
  function apiGet(path) { return window._appHelpers.apiGet(path); }
  function apiPost(path, body) { return window._appHelpers.apiPost(path, body); }
  function showToast(msg, type) { window._appHelpers.showToast(msg, type); }
  function escapeHtml(str) { return window._appHelpers.escapeHtml(str); }

  /**
   * Show loading state in the suggestion panel
   */
  function showLoading() {
    suggestionLoading.style.display = '';
    suggestionContent.innerHTML = '';
    suggestionActions.style.display = 'none';
  }

  /**
   * Hide loading state
   */
  function hideLoading() {
    suggestionLoading.style.display = 'none';
  }

  /**
   * Request AI suggestion for a prompt and display in panel
   */
  async function loadSuggestion(promptId) {
    currentPromptId = promptId;
    currentSuggestion = null;
    suggestionPanel.classList.add('open');
    showLoading();

    try {
      // Fetch current prompt content for diff comparison
      var currentPrompt = await apiGet('/api/prompts/' + encodeURIComponent(promptId));

      // Request AI suggestion
      var suggestion = await apiPost('/api/prompts/' + encodeURIComponent(promptId) + '/suggest', {});
      currentSuggestion = suggestion;

      hideLoading();

      // Build content: reasoning + diff
      var html = '';

      // Show AI reasoning if available
      if (suggestion.reason) {
        html += '<div class="suggestion-reason">';
        html += '<strong>AI 분석:</strong>';
        html += '<p>' + escapeHtml(suggestion.reason) + '</p>';
        html += '</div>';
      }

      // Show diff using shared diff helper
      if (window._diffHelpers && suggestion.suggested_content) {
        html += '<div class="suggestion-diff-label">변경 사항:</div>';
        html += window._diffHelpers.renderDiff(currentPrompt.content, suggestion.suggested_content);
      } else if (suggestion.suggested_content) {
        html += '<pre>' + escapeHtml(suggestion.suggested_content) + '</pre>';
      }

      suggestionContent.innerHTML = html;
      suggestionActions.style.display = '';

    } catch (err) {
      hideLoading();
      if (err.status === 409) {
        suggestionContent.innerHTML = '<p class="suggestion-error">충돌이 발생했습니다. 다시 시도해 주세요.</p>';
        showToast('충돌이 발생했습니다. 다시 시도해 주세요.', 'error');
      } else if (err.message && err.message.includes('timeout')) {
        suggestionContent.innerHTML = '<p class="suggestion-error">요청 시간이 초과되었습니다.</p>';
        showToast('AI 분석 시간이 초과되었습니다.', 'error');
      } else {
        suggestionContent.innerHTML = '<p class="suggestion-error">제안을 불러올 수 없습니다.</p>';
        showToast(err.message || 'AI 제안 요청에 실패했습니다.', 'error');
      }
      suggestionActions.style.display = 'none';
    }
  }

  /**
   * Accept the current suggestion
   */
  async function acceptSuggestion() {
    if (!currentPromptId || !currentSuggestion) return;

    try {
      var result = await apiPost(
        '/api/prompts/' + encodeURIComponent(currentPromptId) + '/suggest/accept',
        { suggestion_id: currentSuggestion.id }
      );
      // Update prompt in the list
      window._appHelpers.updatePromptInList(currentPromptId, result);
      showToast('AI 제안이 적용되었습니다.');
      close();
      // Refresh the prompt view
      window._appHelpers.selectPrompt(currentPromptId, false);
    } catch (err) {
      showToast(err.message || '제안 적용에 실패했습니다.', 'error');
    }
  }

  /**
   * Reject the current suggestion
   */
  async function rejectSuggestion() {
    if (!currentPromptId || !currentSuggestion) return;

    try {
      await apiPost(
        '/api/prompts/' + encodeURIComponent(currentPromptId) + '/suggest/reject',
        { suggestion_id: currentSuggestion.id }
      );
      showToast('제안이 거부되었습니다.');
      close();
    } catch (err) {
      showToast(err.message || '제안 거부에 실패했습니다.', 'error');
    }
  }

  /**
   * Close the suggestion panel
   */
  function close() {
    suggestionPanel.classList.remove('open');
    suggestionContent.innerHTML = '';
    suggestionActions.style.display = 'none';
    hideLoading();
    currentSuggestion = null;
  }

  // --- Event listeners ---
  if (acceptBtn) {
    acceptBtn.addEventListener('click', acceptSuggestion);
  }
  if (rejectBtn) {
    rejectBtn.addEventListener('click', rejectSuggestion);
  }

  // Global exposure
  window.PromptSuggestions = {
    loadSuggestion: loadSuggestion,
    close: close
  };
})();
