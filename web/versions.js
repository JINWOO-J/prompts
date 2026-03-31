/**
 * versions.js — 버전 히스토리 UI 모듈
 *
 * 인터페이스:
 *   PromptVersions.loadVersions(promptId)              — 버전 목록 로드 및 패널 열기
 *   PromptVersions.showVersion(promptId, versionNumber) — 특정 버전 내용을 뷰어에 표시
 *   PromptVersions.restoreVersion(promptId, versionNumber) — 버전 복원
 *   PromptVersions.close()                              — 패널 닫기
 */
(function () {
  'use strict';

  // DOM refs
  var versionPanel = document.getElementById('version-panel');
  var versionList = document.getElementById('version-list');
  var viewerContent = document.getElementById('viewer-content');

  // State: currently viewed historical version
  var viewingHistorical = false;
  var currentPromptId = null;

  // --- Helpers (use app.js exposed helpers) ---
  function apiGet(path) { return window._appHelpers.apiGet(path); }
  function apiPost(path, body) { return window._appHelpers.apiPost(path, body); }
  function showToast(msg, type) { window._appHelpers.showToast(msg, type); }
  function escapeHtml(str) { return window._appHelpers.escapeHtml(str); }

  /** Render markdown using marked.js + highlight code blocks (DOMPurify sanitized) */
  function renderMarkdown(md) {
    if (typeof marked === 'undefined') return md;
    var html = marked.parse(md);
    if (typeof DOMPurify !== 'undefined') html = DOMPurify.sanitize(html);
    return html;
  }

  function highlightCodeBlocks(container) {
    if (typeof hljs !== 'undefined') {
      container.querySelectorAll('pre code').forEach(function (block) {
        hljs.highlightElement(block);
      });
    }
  }

  /**
   * Load and display version list for a prompt
   */
  async function loadVersions(promptId) {
    currentPromptId = promptId;
    versionPanel.classList.add('open');
    versionList.innerHTML = '<p class="version-loading">로딩 중...</p>';

    try {
      var versions = await apiGet('/api/prompts/' + encodeURIComponent(promptId) + '/versions');
      if (versions.length === 0) {
        versionList.innerHTML = '<p class="version-empty">버전 히스토리가 없습니다.</p>';
        return;
      }
      versionList.innerHTML = versions.map(function (v) {
        return '<div class="version-item" data-version="' + v.version_number + '">' +
          '<div class="version-item-header">' +
            '<span class="version-number">v' + v.version_number + '</span>' +
            '<span class="version-date">' + new Date(v.created_at).toLocaleString('ko-KR') + '</span>' +
          '</div>' +
          (v.change_summary ? '<div class="version-summary">' + escapeHtml(v.change_summary) + '</div>' : '') +
          '<button class="version-diff-btn" data-version="' + v.version_number + '">Diff</button>' +
          '<button class="version-restore-btn" data-version="' + v.version_number + '">복원</button>' +
        '</div>';
      }).join('');
    } catch (err) {
      versionList.innerHTML = '<p class="version-empty">버전을 불러올 수 없습니다.</p>';
    }
  }

  /**
   * Show diff between a version and the current prompt content
   */
  async function showDiff(promptId, versionNumber) {
    try {
      var version = await apiGet('/api/prompts/' + encodeURIComponent(promptId) + '/versions/' + versionNumber);
      var current = await apiGet('/api/prompts/' + encodeURIComponent(promptId));
      viewingHistorical = true;
      currentPromptId = promptId;

      var diffHtml;
      if (window._diffHelpers) {
        diffHtml = window._diffHelpers.renderDiff(version.content, current.content);
      } else {
        var diff = Diff.diffLines(version.content, current.content);
        diffHtml = '<div class="diff-container">';
        diff.forEach(function (part) {
          var cls = part.added ? 'diff-added' : part.removed ? 'diff-removed' : 'diff-unchanged';
          diffHtml += '<div class="' + cls + '">' + escapeHtml(part.value) + '</div>';
        });
        diffHtml += '</div>';
      }

      var bannerHtml = '<div class="version-preview-banner">' +
        '<span>v' + version.version_number + ' → 현재 버전 Diff</span>' +
        '<button class="version-back-btn" id="version-back-btn">돌아가기</button>' +
      '</div>';

      viewerContent.innerHTML = bannerHtml + diffHtml;

      // Highlight active version
      versionList.querySelectorAll('.version-item').forEach(function (el) {
        el.classList.toggle('version-item-active', el.dataset.version === String(versionNumber));
      });

      var backBtn = document.getElementById('version-back-btn');
      if (backBtn) {
        backBtn.addEventListener('click', function () {
          viewingHistorical = false;
          window._appHelpers.selectPrompt(currentPromptId, false);
        });
      }
    } catch (err) {
      showToast('Diff를 불러올 수 없습니다.', 'error');
    }
  }

  /**
   * Show a specific version's content in the viewer panel
   */
  async function showVersion(promptId, versionNumber) {
    try {
      var version = await apiGet('/api/prompts/' + encodeURIComponent(promptId) + '/versions/' + versionNumber);
      viewingHistorical = true;
      currentPromptId = promptId;

      // Render version content with a banner
      var bannerHtml = '<div class="version-preview-banner">' +
        '<span>v' + version.version_number + ' 버전을 보고 있습니다</span>' +
        '<button class="version-back-btn" id="version-back-btn">돌아가기</button>' +
      '</div>';

      viewerContent.innerHTML = bannerHtml + renderMarkdown(version.content);
      highlightCodeBlocks(viewerContent);

      // Highlight active version in the list
      versionList.querySelectorAll('.version-item').forEach(function (el) {
        el.classList.toggle('version-item-active', el.dataset.version === String(versionNumber));
      });

      // Back button handler
      var backBtn = document.getElementById('version-back-btn');
      if (backBtn) {
        backBtn.addEventListener('click', function () {
          viewingHistorical = false;
          window._appHelpers.selectPrompt(currentPromptId, false);
        });
      }
    } catch (err) {
      showToast('버전 내용을 불러올 수 없습니다.', 'error');
    }
  }

  /**
   * Restore a specific version
   */
  async function restoreVersion(promptId, versionNumber) {
    if (!confirm('v' + versionNumber + ' 버전으로 복원하시겠습니까?')) return;

    try {
      var restored = await apiPost(
        '/api/prompts/' + encodeURIComponent(promptId) + '/versions/' + versionNumber + '/restore',
        {}
      );
      // Update the prompt in allPrompts via app.js helper
      window._appHelpers.updatePromptInList(promptId, restored);
      viewingHistorical = false;
      window._appHelpers.selectPrompt(promptId, false);
      close();
      showToast('버전이 복원되었습니다.');
    } catch (err) {
      showToast(err.message || '복원에 실패했습니다.', 'error');
    }
  }

  /**
   * Close the version panel
   */
  function close() {
    versionPanel.classList.remove('open');
    // Clear active version highlight
    versionList.querySelectorAll('.version-item').forEach(function (el) {
      el.classList.remove('version-item-active');
    });
    // If viewing historical, go back to current
    if (viewingHistorical && currentPromptId) {
      viewingHistorical = false;
      window._appHelpers.selectPrompt(currentPromptId, false);
    }
  }

  // --- Event delegation on version list ---
  versionList.addEventListener('click', function (e) {
    // Diff button click
    var diffBtn = e.target.closest('.version-diff-btn');
    if (diffBtn && currentPromptId) {
      e.stopPropagation();
      showDiff(currentPromptId, parseInt(diffBtn.dataset.version, 10));
      return;
    }

    // Restore button click
    var restoreBtn = e.target.closest('.version-restore-btn');
    if (restoreBtn && currentPromptId) {
      e.stopPropagation();
      var ver = restoreBtn.dataset.version;
      restoreVersion(currentPromptId, parseInt(ver, 10));
      return;
    }

    // Version item click (show version content)
    var item = e.target.closest('.version-item');
    if (item && currentPromptId) {
      var versionNumber = parseInt(item.dataset.version, 10);
      showVersion(currentPromptId, versionNumber);
    }
  });

  // Global exposure
  window.PromptVersions = {
    loadVersions: loadVersions,
    showVersion: showVersion,
    restoreVersion: restoreVersion,
    close: close
  };
})();
