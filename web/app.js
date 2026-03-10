/* ===== Prompt Library SPA ===== */

(function () {
  'use strict';

  // --- State ---
  let allPrompts = [];
  let meta = {};
  let activeCategory = 'all';
  let activePromptId = null;
  let filteredPrompts = [];
  let focusIndex = -1;
  let activeTags = [];
  let activeOrigins = [];

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
  const sidebar = $('#sidebar');
  const sidebarOverlay = $('#sidebar-overlay');
  const sidebarToggle = $('.sidebar-toggle');
  const tagSelect = $('#tag-select');
  const tagChips = $('#tag-chips');
  const originButtons = $('#origin-buttons');
  const matchCount = $('#match-count');

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
      const res = await fetch('data.json');
      const data = await res.json();
      meta = data._meta;
      allPrompts = data.prompts;
    } catch (e) {
      viewerContent.innerHTML = '<p style="color:#dc2626;">Failed to load data.json. Run <code>python3 scripts/rebuild-index.py</code> first.</p>';
      return;
    }

    renderCategories();
    renderTagFilter();
    renderOriginFilter();
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
  function renderCategories() {
    const cats = [{ key: 'all', label: 'All', count: meta.total }];
    for (const cat of meta.categories) {
      cats.push({ key: cat, label: cat, count: meta.stats[cat] || 0 });
    }

    categoriesEl.innerHTML = cats
      .map(
        (c) =>
          `<button class="category-btn${c.key === activeCategory ? ' active' : ''}" data-cat="${c.key}">${c.label}<span class="category-count">${c.count}</span></button>`
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
    const allTags = getAllTags();
    tagSelect.innerHTML = '<option value="">Filter by tag...</option>' +
      allTags.map((t) => `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`).join('');
    renderTagChips();
  }

  function renderTagChips() {
    tagChips.innerHTML = activeTags
      .map((t) => `<span class="tag-chip" data-tag="${escapeHtml(t)}">${escapeHtml(t)} <button aria-label="Remove tag">&times;</button></span>`)
      .join('');
  }

  tagSelect.addEventListener('change', () => {
    const tag = tagSelect.value;
    if (tag && !activeTags.includes(tag)) {
      activeTags.push(tag);
      renderTagChips();
      focusIndex = -1;
      applyFilter();
    }
    tagSelect.value = '';
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
    if (value && !activeTags.includes(value)) {
      activeTags.push(value);
      renderTagChips();
      applyFilter();
    }
  });

  // --- Origin Filter ---
  const ORIGINS = ['custom', 'scoutflo', 'voltagent', 'shawnewallace', 'extracted'];

  function renderOriginFilter() {
    originButtons.innerHTML = ORIGINS
      .map((o) => `<button class="origin-toggle ${o}${activeOrigins.includes(o) ? ' active' : ''}" data-origin="${o}">${o}</button>`)
      .join('');
  }

  originButtons.addEventListener('click', (e) => {
    const btn = e.target.closest('.origin-toggle');
    if (!btn) return;
    const origin = btn.dataset.origin;
    if (activeOrigins.includes(origin)) {
      activeOrigins = activeOrigins.filter((o) => o !== origin);
    } else {
      activeOrigins.push(origin);
    }
    renderOriginFilter();
    focusIndex = -1;
    applyFilter();
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
      if (activeTags.length > 0 && !activeTags.every((t) => p.tags.includes(t))) return false;
      if (activeOrigins.length > 0 && !activeOrigins.includes(p.origin)) return false;
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
            <span class="origin-badge ${p.origin}">${p.origin}</span>
            <span>${p.category}</span>
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

  // --- Select Prompt ---
  function selectPrompt(id, closeSidebar) {
    const prompt = allPrompts.find((p) => p.id === id);
    if (!prompt) return;

    activePromptId = id;
    location.hash = '#' + id;
    localStorage.setItem('pl-last-prompt', id);

    // Update list active state
    promptList.querySelectorAll('.prompt-item').forEach((el) => {
      el.classList.toggle('active', el.dataset.id === id);
    });

    // Render viewer
    viewerTitle.textContent = prompt.title;
    viewerTags.innerHTML = prompt.tags
      .map((t) => `<span class="viewer-tag" data-tag="${escapeHtml(t)}">${escapeHtml(t)}</span>`)
      .join('');
    viewerContent.innerHTML = marked.parse(prompt.content);

    // Re-highlight code blocks
    viewerContent.querySelectorAll('pre code').forEach((block) => {
      hljs.highlightElement(block);
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
      await navigator.clipboard.writeText(prompt.content);
      copyBtn.classList.add('copied');
      copyBtn.querySelector('span').textContent = 'Copied!';
      setTimeout(() => {
        copyBtn.classList.remove('copied');
        copyBtn.querySelector('span').textContent = 'Copy';
      }, 2000);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = prompt.content;
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
      if (document.activeElement === searchInput && searchInput.value) {
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

  // --- Start ---
  init();
})();
