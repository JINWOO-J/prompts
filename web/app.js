/* ===== Prompt Library SPA ===== */

(function () {
  'use strict';

  // --- Constants ---
  const CATEGORIES = ['rca', 'incident-response', 'application', 'infrastructure', 'security', 'data-ai', 'shared', 'techniques', 'coding'];

  // --- State ---
  let allPrompts = [];
  let meta = {};
  let activeCategory = 'all';
  let activePromptId = null;
  let filteredPrompts = [];
  let focusIndex = -1;
  let activeTags = [];
  let isEditMode = false;

  // --- DOM refs ---
  const $ = (sel) => document.querySelector(sel);
  const searchInput = $('#search-input');
  const categoriesEl = $('#categories');
  const promptList = $('#prompt-list');
  const emptyState = $('#empty-state');
  const viewerTitle = $('#viewer-title');
  const viewerTags = $('#viewer-tags');
  const viewerContent = $('#viewer-content');
  const copyBtn = $('#copy-btn');
  const copyMdBtn = $('#copy-md-btn');
  const sidebar = $('#sidebar');
  const sidebarOverlay = $('#sidebar-overlay');
  const sidebarToggle = $('.sidebar-toggle');
  const tagInput = $('#tag-input');
  const tagDropdown = $('#tag-dropdown');
  const tagChips = $('#tag-chips');
  const matchCount = $('#match-count');
  const newPromptBtn = $('#new-prompt-btn');
  const editBtn = $('#edit-btn');
  const deleteBtn = $('#delete-btn');
  const historyBtn = $('#history-btn');
  const editPanel = $('#edit-panel');
  const editForm = $('#edit-form');
  const placeholderForm = $('#placeholder-form');
  const editCancelBtn = $('#edit-cancel-btn');
  const editTitle = $('#edit-title');
  const editCategory = $('#edit-category');
  const editTags = $('#edit-tags');
  const editRole = $('#edit-role');
  const editContent = $('#edit-content');
  const editChangeSummary = $('#edit-change-summary');
  const editPanelTitle = $('#edit-panel-title');
  const toastContainer = $('#toast-container');
  const versionPanel = $('#version-panel');
  const versionList = $('#version-list');
  const versionCloseBtn = $('#version-close-btn');

  // --- Toast Notifications ---
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // --- API Helpers ---
  async function apiGet(path) {
    const res = await fetch(path);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }
    return res.json();
  }

  async function apiPost(path, body) {
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        const error = new Error(typeof err.detail === 'string' ? err.detail : res.statusText);
        error.status = res.status;
        error.body = err;
        throw error;
      }
      return res.json();
    }

  async function apiPut(path, body) {
      const res = await fetch(path, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        const error = new Error(typeof err.detail === 'string' ? err.detail : res.statusText);
        error.status = res.status;
        error.body = err;
        throw error;
      }
      return res.json();
    }

  async function apiDelete(path) {
    const res = await fetch(path, { method: 'DELETE' });
    if (!res.ok && res.status !== 204) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }
    return true;
  }

  // --- Init ---
  async function init() {
    marked.setOptions({
      highlight: (code, lang) => {
        if (lang && hljs.getLanguage(lang)) {
          return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
      },
      breaks: false,
      gfm: true,
    });

    try {
      // Try API first, fallback to data.json
      try {
        const data = await apiGet('/api/prompts?page_size=10000');
        allPrompts = data.prompts.map((p) => ({
          ...p,
          content: '', // list endpoint doesn't include content
        }));
        // Construct meta from API response
        const stats = {};
        for (const cat of CATEGORIES) {
          stats[cat] = allPrompts.filter((p) => p.category === cat).length;
        }
        meta = {
          total: data.total,
          categories: CATEGORIES,
          stats,
        };
      } catch {
        // Fallback to data.json
        const res = await fetch('data.json');
        const data = await res.json();
        meta = data._meta;
        allPrompts = data.prompts;
      }
    } catch (e) {
      viewerContent.innerHTML = '<p style="color:#dc2626;">Failed to load prompts. Ensure the API server is running or run <code>python3 scripts/rebuild-index.py</code> for data.json.</p>';
      return;
    }

    renderCategories();
    renderTagFilter();
    restoreState();
    applyFilter();

    // Restore active prompt from hash or localStorage
    const hashId = location.hash.slice(1);
    const savedId = localStorage.getItem('pl-last-prompt');
    const targetId = hashId || savedId;
    if (targetId) {
      const prompt = allPrompts.find((p) => p.id === targetId);
      if (prompt) {
        selectPrompt(prompt.id, false);
        return;
      }
    }
  }

  // --- Categories ---
  // Lucide-style SVG icons (14x14, stroke-width 2)
  const _i = (d) => `<svg class="cat-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  const CAT_ICONS = {
    all:                 _i('<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>'),
    rca:                 _i('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'),
    'incident-response': _i('<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
    application:         _i('<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>'),
    infrastructure:      _i('<rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>'),
    security:            _i('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'),
    'data-ai':           _i('<path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-4.96.44A2.5 2.5 0 012 17.5v-.5a2.5 2.5 0 015 0V7.5A2.5 2.5 0 019.5 5h5A2.5 2.5 0 0117 7.5v9a2.5 2.5 0 004.96.44A2.5 2.5 0 0022 14.5V12a2.5 2.5 0 00-5 0v4.5a2.5 2.5 0 01-2.5 2.5h-5A2.5 2.5 0 017 16.5v-9A2.5 2.5 0 019.5 5"/>'),
    shared:              _i('<path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>'),
    techniques:          _i('<line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0018 8 6 6 0 006 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 018.91 14"/>'),
    coding:              _i('<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>'),
  };

  const CATEGORY_LABELS = {
    all: '전체',
    rca: 'RCA',
    'incident-response': '인시던트',
    application: '애플리케이션',
    infrastructure: '인프라',
    security: '보안',
    'data-ai': '데이터/AI',
    shared: '공용',
    techniques: '기법',
    coding: '코딩',
  };

  function renderCategories() {
    const cats = [{ key: 'all', label: CATEGORY_LABELS.all, count: meta.total }];
    for (const cat of meta.categories) {
      cats.push({ key: cat, label: CATEGORY_LABELS[cat] || cat, count: meta.stats[cat] || 0 });
    }

    categoriesEl.innerHTML = cats
      .map(
        (c) =>
          `<button class="category-btn${c.key === activeCategory ? ' active' : ''}" data-cat="${c.key}">${CAT_ICONS[c.key] || ''}${c.label}<span class="category-count">${c.count}</span></button>`
      )
      .join('');

    categoriesEl.addEventListener('click', (e) => {
      const btn = e.target.closest('.category-btn');
      if (!btn) return;
      activeCategory = btn.dataset.cat;
      localStorage.setItem('pl-last-category', activeCategory);
      categoriesEl.querySelectorAll('.category-btn').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      focusIndex = -1;
      applyFilter();
    });
  }

  // --- Tag Filter ---
  function getAllTags() {
    const tagSet = new Set();
    allPrompts.forEach((p) => p.tags.forEach((t) => tagSet.add(t)));
    return [...tagSet].sort();
  }

  function renderTagFilter() {
    renderTagChips();
  }

  function renderTagChips() {
    tagChips.innerHTML = activeTags
      .map((t) => `<span class="tag-chip" data-tag="${escapeHtml(t)}">${escapeHtml(t)} <button aria-label="Remove tag">&times;</button></span>`)
      .join('');
  }

  // --- Tag Autocomplete ---
  let tagHighlightIdx = -1;

  function showTagDropdown(query) {
    const allTags = getAllTags();
    const q = query.toLowerCase();
    const filtered = allTags.filter((t) => t.toLowerCase().includes(q) && !activeTags.some((at) => at.toLowerCase() === t.toLowerCase()));

    if (!filtered.length) {
      tagDropdown.innerHTML = '<div class="tag-dropdown-empty">일치하는 태그 없음</div>';
      tagDropdown.classList.toggle('open', !!q);
      tagHighlightIdx = -1;
      return;
    }

    tagHighlightIdx = -1;
    tagDropdown.innerHTML = filtered.slice(0, 30)
      .map((t, i) => `<div class="tag-dropdown-item" data-tag="${escapeHtml(t)}" data-index="${i}">${escapeHtml(t)}</div>`)
      .join('');
    tagDropdown.classList.add('open');
  }

  function closeTagDropdown() {
    tagDropdown.classList.remove('open');
    tagDropdown.innerHTML = '';
    tagHighlightIdx = -1;
  }

  function addTag(tag) {
    if (tag && !activeTags.some((at) => at.toLowerCase() === tag.toLowerCase())) {
      activeTags.push(tag);
      renderTagChips();
      focusIndex = -1;
      applyFilter();
    }
    tagInput.value = '';
    closeTagDropdown();
  }

  tagInput.addEventListener('input', () => {
    showTagDropdown(tagInput.value.trim());
  });

  tagInput.addEventListener('focus', () => {
    showTagDropdown(tagInput.value.trim());
  });

  tagInput.addEventListener('keydown', (e) => {
    const items = tagDropdown.querySelectorAll('.tag-dropdown-item');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      tagHighlightIdx = Math.min(tagHighlightIdx + 1, items.length - 1);
      items.forEach((el, i) => el.classList.toggle('highlighted', i === tagHighlightIdx));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      tagHighlightIdx = Math.max(tagHighlightIdx - 1, 0);
      items.forEach((el, i) => el.classList.toggle('highlighted', i === tagHighlightIdx));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (tagHighlightIdx >= 0 && items[tagHighlightIdx]) {
        addTag(items[tagHighlightIdx].dataset.tag);
      } else if (tagInput.value.trim()) {
        // 정확히 매칭되는 태그가 있으면 추가
        const exact = getAllTags().find((t) => t.toLowerCase() === tagInput.value.trim().toLowerCase());
        if (exact) addTag(exact);
      }
    } else if (e.key === 'Escape') {
      closeTagDropdown();
    }
  });

  tagDropdown.addEventListener('click', (e) => {
    const item = e.target.closest('.tag-dropdown-item');
    if (item) addTag(item.dataset.tag);
  });

  // 외부 클릭 시 드롭다운 닫기
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.tag-autocomplete-wrapper')) closeTagDropdown();
  });

  tagChips.addEventListener('click', (e) => {
    const chip = e.target.closest('.tag-chip');
    if (!chip) return;
    activeTags = activeTags.filter((t) => t !== chip.dataset.tag);
    renderTagChips();
    focusIndex = -1;
    applyFilter();
  });

  viewerTags.addEventListener('click', (e) => {
    const tag = e.target.closest('.viewer-tag');
    if (!tag) return;
    const value = tag.dataset.tag;
    if (value && !activeTags.some((at) => at.toLowerCase() === value.toLowerCase())) {
      activeTags.push(value);
      renderTagChips();
      applyFilter();
    }
  });

  // --- Filter & Search ---
  let debounceTimer;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      focusIndex = -1;
      applyFilter();
    }, 200);
  });

  function applyFilter() {
    const query = searchInput.value.trim().toLowerCase();

    filteredPrompts = allPrompts.filter((p) => {
      if (activeCategory !== 'all' && p.category !== activeCategory) return false;
      if (activeTags.length > 0 && !activeTags.every((at) => p.tags.some((pt) => pt.toLowerCase() === at.toLowerCase()))) return false;
      if (!query) return true;
      return (
        p.title.toLowerCase().includes(query) ||
        p.content.toLowerCase().includes(query) ||
        p.tags.some((t) => t.toLowerCase().includes(query))
      );
    });

    renderPromptList(query);
  }

  function renderPromptList(query) {
    const total = allPrompts.length;
    const matched = filteredPrompts.length;
    matchCount.textContent = matched === total
      ? `${total} prompts`
      : `${matched} / ${total} prompts`;

    if (filteredPrompts.length === 0) {
      promptList.innerHTML = '';
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;

    promptList.innerHTML = filteredPrompts
      .map((p, i) => {
        const title = query ? highlightText(p.title, query) : escapeHtml(p.title);
        const isActive = p.id === activePromptId;
        const isFocused = i === focusIndex;
        return `<li class="prompt-item${isActive ? ' active' : ''}${isFocused ? ' focused' : ''}" data-id="${p.id}" data-index="${i}">
          <div class="prompt-item-title">${title}</div>
          <div class="prompt-item-meta">
            <span class="category-badge ${p.category}">${CATEGORY_LABELS[p.category] || p.category}</span>
          </div>
        </li>`;
      })
      .join('');

    promptList.addEventListener('click', (e) => {
      const item = e.target.closest('.prompt-item');
      if (!item) return;
      selectPrompt(item.dataset.id, true);
    });
  }

  // --- Placeholder Detection & Dynamic Form ---
  // 코드블록 내부의 [...]는 제외하고, 체크박스/출처 참조도 제외
  const PH_SKIP = /^\s*$|^[Xx ]$|^STEP\s*\d|^Step\s*\d|^Scoutflo|^VoltAgent|^shawnewallace/;

  function extractPlaceholders(content) {
    // 인라인 코드만 제거 (코드블록 안의 플레이스홀더는 유지 — RCA 프롬프트 등에서 필요)
    let text = content.replace(/`[^`\n]+`/g, '');
    // 마크다운 링크 [text](url) 제거
    text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '');
    // <OutputFormat> 블록 제거 — LLM 출력 형식 안의 [설명]은 플레이스홀더가 아님
    text = text.replace(/<OutputFormat>[\s\S]*?<\/OutputFormat>/gi, '');
    const matches = text.match(/\[([^\[\]]{2,80})\]/g) || [];
    const seen = new Set();
    const result = [];
    for (const m of matches) {
      const inner = m.slice(1, -1);
      if (PH_SKIP.test(inner)) continue;
      if (!seen.has(inner)) {
        seen.add(inner);
        result.push(inner);
      }
    }
    return result;
  }

  let currentPlaceholderValues = {};

  function renderPlaceholderForm(placeholders) {
    if (!placeholders.length) {
      placeholderForm.style.display = 'none';
      placeholderForm.innerHTML = '';
      return;
    }
    currentPlaceholderValues = {};
    placeholderForm.style.display = '';
    placeholderForm.innerHTML =
      '<div class="ph-form-header"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg> 변수 입력 <span class="ph-count">' + placeholders.length + '개</span></div>' +
      '<div class="ph-fields">' +
      placeholders.map((ph, i) =>
        '<div class="ph-field">' +
          '<label for="ph-input-' + i + '">' + escapeHtml(ph) + '</label>' +
          (ph.length > 40
            ? '<textarea id="ph-input-' + i + '" data-ph="' + escapeHtml(ph) + '" placeholder="값을 입력하세요" rows="2"></textarea>'
            : '<input id="ph-input-' + i + '" data-ph="' + escapeHtml(ph) + '" placeholder="값을 입력하세요" />') +
        '</div>'
      ).join('') +
      '</div>';

    placeholderForm.addEventListener('input', (e) => {
      const ph = e.target.dataset.ph;
      if (!ph) return;
      currentPlaceholderValues[ph] = e.target.value;
      rerenderContent();
    });
  }

  function applyPlaceholders(content) {
    let result = content;
    for (const [ph, val] of Object.entries(currentPlaceholderValues)) {
      if (!val) continue;
      // 전역 치환 — 대괄호 포함하여 값으로 교체
      const escaped = ph.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      result = result.replace(new RegExp('\\[' + escaped + '\\]', 'g'), val);
    }
    return result;
  }

  function rerenderContent() {
    const prompt = allPrompts.find((p) => p.id === activePromptId);
    if (!prompt || !prompt.content) return;
    const replaced = applyPlaceholders(prompt.content);
    viewerContent.innerHTML = marked.parse(replaced);
    // 코드 하이라이트 + 복사 버튼 재적용
    viewerContent.querySelectorAll('pre').forEach((pre) => {
      const code = pre.querySelector('code');
      if (code) hljs.highlightElement(code);
      const btn = document.createElement('button');
      btn.className = 'code-copy-btn';
      btn.textContent = 'Copy';
      btn.addEventListener('click', async () => {
        const text = pre.querySelector('code')?.textContent || pre.textContent;
        try { await navigator.clipboard.writeText(text); } catch { /* fallback omitted for brevity */ }
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
      });
      pre.style.position = 'relative';
      pre.appendChild(btn);
    });
  }

  // --- Select Prompt ---
  async function selectPrompt(id, closeSidebar) {
    const prompt = allPrompts.find((p) => p.id === id);
    if (!prompt) return;

    activePromptId = id;
    location.hash = '#' + id;
    localStorage.setItem('pl-last-prompt', id);

    // Update list active state
    promptList.querySelectorAll('.prompt-item').forEach((el) => {
      el.classList.toggle('active', el.dataset.id === id);
    });

    // Fetch full content if not loaded yet
    if (!prompt.content) {
      try {
        const full = await apiGet(`/api/prompts/${encodeURIComponent(id)}`);
        prompt.content = full.content;
      } catch {
        // If API fails, show what we have
      }
    }

    // Show action buttons
    editBtn.style.display = '';
    deleteBtn.style.display = '';
    historyBtn.style.display = '';

    // Render viewer
    viewerTitle.textContent = prompt.title;
    viewerTags.innerHTML = prompt.tags
      .map((t) => `<span class="viewer-tag" data-tag="${escapeHtml(t)}">${escapeHtml(t)}</span>`)
      .join('');
    viewerContent.innerHTML = marked.parse(prompt.content);

    // 플레이스홀더 감지 및 폼 생성
    const placeholders = extractPlaceholders(prompt.content);
    renderPlaceholderForm(placeholders);

    // Re-highlight code blocks + add copy buttons
    viewerContent.querySelectorAll('pre').forEach((pre) => {
      const code = pre.querySelector('code');
      if (code) hljs.highlightElement(code);

      const btn = document.createElement('button');
      btn.className = 'code-copy-btn';
      btn.textContent = 'Copy';
      btn.addEventListener('click', async () => {
        const text = pre.querySelector('code')?.textContent || pre.textContent;
        try {
          await navigator.clipboard.writeText(text);
        } catch {
          const ta = document.createElement('textarea');
          ta.value = text;
          ta.style.cssText = 'position:fixed;opacity:0';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
        }
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
      });

      pre.style.position = 'relative';
      pre.appendChild(btn);
    });

    // Mobile: close sidebar
    if (closeSidebar && window.innerWidth <= 768) {
      toggleSidebar(false);
    }
  }

  // --- Copy ---
  copyBtn.addEventListener('click', async () => {
    if (!activePromptId) return;
    const prompt = allPrompts.find((p) => p.id === activePromptId);
    if (!prompt) return;

    try {
      const text = applyPlaceholders(prompt.content);
      await navigator.clipboard.writeText(text);
      copyBtn.classList.add('copied');
      copyBtn.querySelector('span').textContent = 'Copied!';
      setTimeout(() => {
        copyBtn.classList.remove('copied');
        copyBtn.querySelector('span').textContent = 'Copy';
      }, 2000);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = applyPlaceholders(prompt.content);
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      copyBtn.querySelector('span').textContent = 'Copied!';
      setTimeout(() => { copyBtn.querySelector('span').textContent = 'Copy'; }, 2000);
    }
  });

  // --- Copy as .md ---
  copyMdBtn.addEventListener('click', async () => {
    if (!activePromptId) return;
    const prompt = allPrompts.find((p) => p.id === activePromptId);
    if (!prompt) return;

    // Build frontmatter YAML
    const fm = ['---'];
    fm.push(`category: ${prompt.category}`);
    if (prompt.tags && prompt.tags.length) {
      fm.push('tags:');
      prompt.tags.forEach((t) => fm.push(`- ${t}`));
    }
    if (prompt.role) fm.push(`role: ${prompt.role}`);
    if (prompt.origin) fm.push(`origin: ${prompt.origin}`);
    fm.push('---');

    const content = applyPlaceholders(prompt.content);
    const md = fm.join('\n') + '\n' + content;

    try {
      await navigator.clipboard.writeText(md);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = md;
      ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    copyMdBtn.classList.add('copied');
    copyMdBtn.querySelector('span').textContent = 'Copied!';
    setTimeout(() => {
      copyMdBtn.classList.remove('copied');
      copyMdBtn.querySelector('span').textContent = '.md';
    }, 2000);
  });

  // --- Hash routing ---
  window.addEventListener('hashchange', () => {
    const id = location.hash.slice(1);
    if (id && id !== activePromptId) {
      selectPrompt(id, false);
    }
  });

  // --- Keyboard shortcuts ---
  document.addEventListener('keydown', (e) => {
    // Cmd/Ctrl + K → focus search
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
      if (window.innerWidth <= 768) toggleSidebar(true);
      return;
    }

    // Escape
    if (e.key === 'Escape') {
      if (editPanel && editPanel.classList.contains('open')) {
        closeEditPanel();
      } else if (versionPanel && versionPanel.classList.contains('open')) {
        if (window.PromptVersions) window.PromptVersions.close();
      } else if (document.activeElement === searchInput && searchInput.value) {
        searchInput.value = '';
        applyFilter();
      } else if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
        toggleSidebar(false);
      } else {
        searchInput.blur();
      }
      return;
    }

    // Arrow navigation in list (only when search is focused)
    if (document.activeElement === searchInput || document.activeElement === document.body) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        focusIndex = Math.min(focusIndex + 1, filteredPrompts.length - 1);
        updateFocus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        focusIndex = Math.max(focusIndex - 1, 0);
        updateFocus();
      } else if (e.key === 'Enter' && focusIndex >= 0 && focusIndex < filteredPrompts.length) {
        e.preventDefault();
        selectPrompt(filteredPrompts[focusIndex].id, true);
      }
    }
  });

  function updateFocus() {
    promptList.querySelectorAll('.prompt-item').forEach((el) => {
      el.classList.toggle('focused', parseInt(el.dataset.index) === focusIndex);
    });
    // Scroll into view
    const focused = promptList.querySelector('.prompt-item.focused');
    if (focused) focused.scrollIntoView({ block: 'nearest' });
  }

  // --- Mobile sidebar toggle ---
  function toggleSidebar(open) {
    sidebar.classList.toggle('open', open);
    sidebarOverlay.classList.toggle('open', open);
  }

  sidebarToggle.addEventListener('click', () => {
    toggleSidebar(!sidebar.classList.contains('open'));
  });
  sidebarOverlay.addEventListener('click', () => toggleSidebar(false));

  // --- Restore state ---
  function restoreState() {
    const savedCat = localStorage.getItem('pl-last-category');
    if (savedCat && (savedCat === 'all' || meta.categories.includes(savedCat))) {
      activeCategory = savedCat;
      categoriesEl.querySelectorAll('.category-btn').forEach((b) => {
        b.classList.toggle('active', b.dataset.cat === activeCategory);
      });
    }
  }

  // --- Utilities ---
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function highlightText(text, query) {
    const escaped = escapeHtml(text);
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escaped.replace(regex, '<mark>$1</mark>');
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // --- Focused item style ---
  const style = document.createElement('style');
  style.textContent = '.prompt-item.focused { background: var(--bg-hover); outline: 1px solid var(--accent); }';
  document.head.appendChild(style);

  // --- Edit Panel ---
  function openEditPanel(mode, prompt) {
    isEditMode = true;
    editPanelTitle.textContent = mode === 'create' ? '새 프롬프트' : '프롬프트 편집';
    editTitle.value = prompt ? prompt.title : '';
    editCategory.value = prompt ? prompt.category : CATEGORIES[0];
    editTags.value = prompt ? prompt.tags.join(', ') : '';
    editRole.value = prompt ? (prompt.role || '') : '';
    editContent.value = prompt ? prompt.content : '';
    editChangeSummary.value = '';
    // Show/hide change summary (only for edit mode)
    editChangeSummary.closest('.form-group').style.display = mode === 'edit' ? '' : 'none';
    editPanel.dataset.mode = mode;
    editPanel.dataset.promptId = prompt ? prompt.id : '';
    editPanel.classList.add('open');
    // CodeMirror 에디터 초기화
    if (window.PromptEditor) {
      var container = document.getElementById('editor-container');
      if (container) {
        window.PromptEditor.init(container);
        window.PromptEditor.setContent(prompt ? prompt.content : '');
      }
    }
  }

  function closeEditPanel() {
    isEditMode = false;
    if (window.PromptEditor) window.PromptEditor.destroy();
    editPanel.classList.remove('open');
  }

  // --- Form Field Error Handling ---
  function clearFormErrors() {
    editPanel.querySelectorAll('.form-error').forEach((el) => el.remove());
    editPanel.querySelectorAll('.form-input-error').forEach((el) => el.classList.remove('form-input-error'));
  }

  function showFieldErrors(detail) {
    if (!Array.isArray(detail)) return false;
    const fieldMap = { title: 'edit-title', content: 'edit-content', category: 'edit-category', tags: 'edit-tags', role: 'edit-role' };
    let shown = false;
    for (const err of detail) {
      // loc is like ["body", "title"] — grab the last element as the field name
      const fieldName = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : null;
      const inputId = fieldMap[fieldName];
      const input = inputId ? document.getElementById(inputId) : null;
      if (input) {
        input.classList.add('form-input-error');
        const msg = document.createElement('span');
        msg.className = 'form-error';
        msg.textContent = err.msg;
        input.parentNode.appendChild(msg);
        shown = true;
      }
    }
    return shown;
  }

  if (newPromptBtn) {
    newPromptBtn.addEventListener('click', () => openEditPanel('create', null));
  }

  if (editBtn) {
    editBtn.addEventListener('click', () => {
      const prompt = allPrompts.find((p) => p.id === activePromptId);
      if (prompt) openEditPanel('edit', prompt);
    });
  }

  if (editCancelBtn) {
    editCancelBtn.addEventListener('click', closeEditPanel);
  }
  const editCancelBtnFooter = $('#edit-cancel-btn-footer');
  if (editCancelBtnFooter) {
    editCancelBtnFooter.addEventListener('click', closeEditPanel);
  }

  if (editForm) {
    editForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearFormErrors();
      const mode = editPanel.dataset.mode;
      const tags = editTags.value.split(',').map((t) => t.trim()).filter(Boolean);
      const body = {
        title: editTitle.value.trim(),
        category: editCategory.value,
        content: window.PromptEditor ? window.PromptEditor.getContent() : editContent.value,
        tags,
        role: editRole.value.trim(),
      };

      try {
        if (mode === 'create') {
          const created = await apiPost('/api/prompts', body);
          allPrompts.unshift({ ...created, content: created.content });
          // Update meta counts
          meta.total = allPrompts.length;
          if (meta.stats[created.category] !== undefined) meta.stats[created.category]++;
          renderCategories();
          renderTagFilter();
          applyFilter();
          selectPrompt(created.id, false);
          showToast('프롬프트가 생성되었습니다.');
        } else {
          const promptId = editPanel.dataset.promptId;
          body.change_summary = editChangeSummary.value.trim();
          const updated = await apiPut(`/api/prompts/${encodeURIComponent(promptId)}`, body);
          const idx = allPrompts.findIndex((p) => p.id === promptId);
          if (idx >= 0) {
            allPrompts[idx] = { ...allPrompts[idx], ...updated };
          }
          renderTagFilter();
          applyFilter();
          selectPrompt(promptId, false);
          showToast('프롬프트가 수정되었습니다.');
        }
        closeEditPanel();
      } catch (err) {
        if (err.status === 422 && err.body && showFieldErrors(err.body.detail)) {
          showToast('입력값을 확인해주세요.', 'error');
        } else {
          showToast(err.message || '저장에 실패했습니다.', 'error');
        }
      }
    });
  }

  // --- Delete ---
  if (deleteBtn) {
    deleteBtn.addEventListener('click', async () => {
      if (!activePromptId) return;
      const prompt = allPrompts.find((p) => p.id === activePromptId);
      if (!prompt) return;
      if (!confirm(`"${prompt.title}" 프롬프트를 삭제하시겠습니까?`)) return;

      try {
        await apiDelete(`/api/prompts/${encodeURIComponent(activePromptId)}`);
        const cat = prompt.category;
        allPrompts = allPrompts.filter((p) => p.id !== activePromptId);
        meta.total = allPrompts.length;
        if (meta.stats[cat] !== undefined) meta.stats[cat]--;
        activePromptId = null;
        renderCategories();
        renderTagFilter();
        applyFilter();
        viewerTitle.textContent = 'Select a prompt';
        viewerTags.innerHTML = '';
        viewerContent.innerHTML = '<div class="welcome-message"><h2>Welcome to Prompt Library</h2><p>Select a prompt from the sidebar to view its content.</p></div>';
        editBtn.style.display = 'none';
        deleteBtn.style.display = 'none';
        historyBtn.style.display = 'none';
        showToast('프롬프트가 삭제되었습니다.');
      } catch (err) {
        showToast(err.message || '삭제에 실패했습니다.', 'error');
      }
    });
  }

  // --- Version History Panel (delegated to versions.js) ---
  if (historyBtn) {
    historyBtn.addEventListener('click', () => {
      if (!activePromptId || !window.PromptVersions) return;
      window.PromptVersions.loadVersions(activePromptId);
    });
  }

  if (versionCloseBtn) {
    versionCloseBtn.addEventListener('click', () => {
      if (window.PromptVersions) window.PromptVersions.close();
    });
  }

  // --- Expose helpers for versions.js ---
  function updatePromptInList(promptId, data) {
    const idx = allPrompts.findIndex((p) => p.id === promptId);
    if (idx >= 0) allPrompts[idx] = { ...allPrompts[idx], ...data };
  }

  window._appHelpers = {
    apiGet,
    apiPost,
    showToast,
    escapeHtml,
    selectPrompt,
    updatePromptInList,
  };

  // --- Start ---
  init();
})();
