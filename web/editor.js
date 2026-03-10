/**
 * editor.js — CodeMirror 5 기반 마크다운 에디터 모듈
 *
 * 인터페이스:
 *   PromptEditor.init(container)       — 에디터 초기화
 *   PromptEditor.getContent()          — 현재 내용 반환
 *   PromptEditor.setContent(text)      — 내용 설정
 *   PromptEditor.destroy()             — 에디터 정리
 */
(function () {
  'use strict';

  let cmInstance = null;
  let previewEl = null;
  let debounceTimer = null;

  const DEBOUNCE_MS = 200;

  /** marked.js + highlight.js 로 마크다운 → HTML 변환 */
  function renderMarkdown(md) {
    if (typeof marked === 'undefined') return md;
    return marked.parse(md);
  }

  /** 미리보기 패널 업데이트 (200ms 디바운스) */
  function schedulePreview() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      if (!previewEl || !cmInstance) return;
      const html = renderMarkdown(cmInstance.getValue());
      previewEl.innerHTML = html;
      // highlight.js 로 코드 블록 하이라이팅
      if (typeof hljs !== 'undefined') {
        previewEl.querySelectorAll('pre code').forEach(function (block) {
          hljs.highlightElement(block);
        });
      }
    }, DEBOUNCE_MS);
  }

  /**
   * 에디터 초기화
   * @param {HTMLElement} container — #editor-container
   */
  function init(container) {
    if (cmInstance) destroy();

    var textarea = container.querySelector('textarea');
    if (!textarea) return;

    // 미리보기 패널 생성 (아직 없으면)
    previewEl = container.querySelector('.editor-preview');
    if (!previewEl) {
      previewEl = document.createElement('div');
      previewEl.className = 'editor-preview viewer-content';
      container.appendChild(previewEl);
    }

    // textarea 숨기고 CodeMirror 생성
    textarea.style.display = 'none';
    container.classList.add('editor-split');

    cmInstance = CodeMirror(function (editorEl) {
      editorEl.className = 'editor-cm-wrapper';
      container.insertBefore(editorEl, previewEl);
    }, {
      value: textarea.value || '',
      mode: 'markdown',
      theme: 'default',
      lineNumbers: true,
      lineWrapping: true,
      tabSize: 2,
      indentWithTabs: false,
      placeholder: '마크다운 내용을 입력하세요...',
      viewportMargin: Infinity
    });

    // 실시간 미리보기
    cmInstance.on('change', schedulePreview);

    // 초기 미리보기 렌더링
    schedulePreview();

    // CodeMirror 가 레이아웃 잡힌 뒤 리프레시
    setTimeout(function () {
      if (cmInstance) cmInstance.refresh();
    }, 50);
  }

  /** 현재 에디터 내용 반환 */
  function getContent() {
    if (cmInstance) return cmInstance.getValue();
    var ta = document.getElementById('edit-content');
    return ta ? ta.value : '';
  }

  /** 에디터 내용 설정 */
  function setContent(text) {
    if (cmInstance) {
      cmInstance.setValue(text || '');
      schedulePreview();
    } else {
      var ta = document.getElementById('edit-content');
      if (ta) ta.value = text || '';
    }
  }

  /** 에디터 정리 */
  function destroy() {
    clearTimeout(debounceTimer);
    if (cmInstance) {
      // CodeMirror wrapper 제거
      var wrapper = cmInstance.getWrapperElement();
      if (wrapper && wrapper.parentNode) {
        wrapper.parentNode.removeChild(wrapper);
      }
      cmInstance = null;
    }
    if (previewEl && previewEl.parentNode) {
      previewEl.parentNode.removeChild(previewEl);
      previewEl = null;
    }
    // textarea 복원
    var ta = document.getElementById('edit-content');
    if (ta) ta.style.display = '';
    var container = document.getElementById('editor-container');
    if (container) container.classList.remove('editor-split');
  }

  // 글로벌 노출
  window.PromptEditor = {
    init: init,
    getContent: getContent,
    setContent: setContent,
    destroy: destroy
  };
})();
