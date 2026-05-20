(function () {

  var events = [];
  var MAX_EVENTS = 50;
  var panelOpen = false;

  // ── Capture ──────────────────────────────────────────────────────────────

  function captureEvent(type, args) {
    var name, properties;
    if (type === 'track') {
      name = args[0] || '(unnamed)';
      properties = args[1] || {};
    } else if (type === 'page') {
      name = args[0] || '(page)';
      properties = args[1] || {};
    } else if (type === 'identify') {
      name = args[0] || '(anonymous)';
      properties = args[1] || {};
    }
    events.unshift({ type: type, name: name, properties: properties, timestamp: new Date() });
    if (events.length > MAX_EVENTS) { events.pop(); }
    updateBadge();
    if (panelOpen) { renderEventList(); }
  }

  function wrapAnalytics() {
    if (!window.analytics) { return; }
    ['track', 'page', 'identify'].forEach(function (method) {
      var original = analytics[method].bind(analytics);
      analytics[method] = function () {
        captureEvent(method, Array.prototype.slice.call(arguments));
        return original.apply(analytics, arguments);
      };
    });
  }

  // ── Relative time ─────────────────────────────────────────────────────────

  function relativeTime(date) {
    var diff = Math.floor((new Date() - date) / 1000);
    if (diff < 5) { return 'just now'; }
    if (diff < 60) { return diff + 's ago'; }
    return Math.floor(diff / 60) + 'm ago';
  }

  // ── Badge ─────────────────────────────────────────────────────────────────

  function updateBadge() {
    var badge = document.getElementById('evd-badge');
    if (!badge) { return; }
    badge.textContent = events.length;
    badge.style.display = events.length === 0 ? 'none' : 'inline-block';
  }

  // ── Event list rendering ──────────────────────────────────────────────────

  function renderEventList() {
    var list = document.getElementById('evd-list');
    if (!list) { return; }

    if (events.length === 0) {
      list.innerHTML = '<div class="evd-empty">No events captured yet.<br>Navigate the site to fire events.</div>';
      return;
    }

    // Remember which indices are currently expanded before re-render
    var openIndices = {};
    list.querySelectorAll('.evd-event').forEach(function (el) {
      var idx = el.getAttribute('data-index');
      if (el.querySelector('.evd-event-body').style.display !== 'none') {
        openIndices[idx] = true;
      }
    });

    list.innerHTML = events.map(function (ev, i) {
      var typeClass = 'evd-badge-' + ev.type;
      var typeLabel = ev.type.toUpperCase();
      var isOpen = openIndices[String(i)];
      return (
        '<div class="evd-event" data-index="' + i + '">' +
          '<div class="evd-event-header">' +
            '<span class="evd-type-badge ' + typeClass + '">' + typeLabel + '</span>' +
            '<span class="evd-event-name">' + escapeHtml(ev.name) + '</span>' +
            '<span class="evd-timestamp">' + relativeTime(ev.timestamp) + '</span>' +
            '<span class="evd-chevron">' + (isOpen ? '&#9660;' : '&#9654;') + '</span>' +
          '</div>' +
          '<div class="evd-event-body" style="display:' + (isOpen ? 'block' : 'none') + '">' +
            '<pre class="evd-json">' + escapeHtml(JSON.stringify(ev.properties, null, 2)) + '</pre>' +
          '</div>' +
        '</div>'
      );
    }).join('');

    list.querySelectorAll('.evd-event').forEach(function (el) {
      el.querySelector('.evd-event-header').addEventListener('click', function () {
        var body = el.querySelector('.evd-event-body');
        var chevron = el.querySelector('.evd-chevron');
        var isOpen = body.style.display !== 'none';
        body.style.display = isOpen ? 'none' : 'block';
        chevron.innerHTML = isOpen ? '&#9654;' : '&#9660;';
      });
    });
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ── Styles ────────────────────────────────────────────────────────────────

  function injectStyles() {
    var style = document.createElement('style');
    style.textContent = `
      #evd-btn {
        position: fixed;
        bottom: 24px;
        left: 24px;
        z-index: 9000;
        background: #1a1a1a;
        color: #ccc;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
        transition: border-color 0.2s, color 0.2s;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      #evd-btn:hover { border-color: #52BD95; color: #fff; }
      #evd-btn .evd-dot {
        width: 8px; height: 8px;
        background: #52BD95;
        border-radius: 50%;
        animation: evd-pulse 2s infinite;
        flex-shrink: 0;
      }
      @keyframes evd-pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
      #evd-badge {
        display: none;
        background: #fff;
        color: #000;
        font-size: 10px;
        font-weight: 900;
        padding: 1px 6px;
        border-radius: 10px;
        min-width: 16px;
        text-align: center;
        line-height: 16px;
      }
      #evd-panel {
        position: fixed;
        bottom: 72px;
        left: 24px;
        width: 320px;
        max-height: 400px;
        background: #0f0f0f;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        z-index: 9001;
        display: flex;
        flex-direction: column;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        transform: translateY(16px);
        opacity: 0;
        pointer-events: none;
        transition: transform 0.2s ease, opacity 0.2s ease;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      #evd-panel.open {
        transform: translateY(0);
        opacity: 1;
        pointer-events: all;
      }
      #evd-panel-header {
        padding: 12px 16px;
        border-bottom: 1px solid #2a2a2a;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-shrink: 0;
        background: #0a0a0a;
        border-radius: 8px 8px 0 0;
      }
      #evd-panel-header .evd-title {
        font-size: 12px;
        font-weight: 700;
        color: #fff;
        letter-spacing: 0.5px;
      }
      #evd-clear-btn {
        background: none;
        border: 1px solid #2a2a2a;
        color: #555;
        font-size: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 3px 8px;
        cursor: pointer;
        border-radius: 4px;
        font-weight: 600;
        transition: border-color 0.2s, color 0.2s;
      }
      #evd-clear-btn:hover { border-color: #666; color: #ccc; }
      #evd-list {
        flex: 1;
        overflow-y: auto;
        min-height: 0;
      }
      #evd-list::-webkit-scrollbar { width: 4px; }
      #evd-list::-webkit-scrollbar-track { background: #111; }
      #evd-list::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
      .evd-empty {
        padding: 32px 16px;
        text-align: center;
        color: #444;
        font-size: 12px;
        line-height: 1.8;
      }
      .evd-event {
        border-bottom: 1px solid #1a1a1a;
      }
      .evd-event:last-child { border-bottom: none; }
      .evd-event-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        cursor: pointer;
        transition: background 0.15s;
      }
      .evd-event-header:hover { background: #151515; }
      .evd-type-badge {
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
        flex-shrink: 0;
      }
      .evd-badge-track   { background: rgba(75,139,245,0.15); color: #4B8BF5; }
      .evd-badge-page    { background: rgba(155,89,182,0.15); color: #9B59B6; }
      .evd-badge-identify { background: rgba(82,189,149,0.15); color: #52BD95; }
      .evd-event-name {
        font-size: 12px;
        color: #fff;
        font-weight: 600;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .evd-timestamp {
        font-size: 10px;
        color: #444;
        flex-shrink: 0;
        white-space: nowrap;
      }
      .evd-chevron {
        font-size: 8px;
        color: #333;
        flex-shrink: 0;
        transition: color 0.15s;
      }
      .evd-event-header:hover .evd-chevron { color: #666; }
      .evd-event-body { background: #080808; }
      .evd-json {
        margin: 0;
        padding: 10px 12px;
        font-size: 11px;
        color: #7aa2f7;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        overflow-x: auto;
        white-space: pre;
        line-height: 1.6;
      }
    `;
    document.head.appendChild(style);
  }

  // ── UI ────────────────────────────────────────────────────────────────────

  function buildUI() {
    var btn = document.createElement('button');
    btn.id = 'evd-btn';
    btn.innerHTML =
      '<span class="evd-dot"></span>' +
      'Events' +
      '<span id="evd-badge"></span>';

    var panel = document.createElement('div');
    panel.id = 'evd-panel';
    panel.innerHTML =
      '<div id="evd-panel-header">' +
        '<span class="evd-title">Segment Events</span>' +
        '<button id="evd-clear-btn">Clear</button>' +
      '</div>' +
      '<div id="evd-list"></div>';

    document.body.appendChild(btn);
    document.body.appendChild(panel);

    btn.addEventListener('click', function () {
      panelOpen = !panelOpen;
      panel.classList.toggle('open', panelOpen);
      if (panelOpen) { renderEventList(); }
    });

    document.getElementById('evd-clear-btn').addEventListener('click', function () {
      events = [];
      updateBadge();
      renderEventList();
    });

    // Close panel when clicking outside
    document.addEventListener('click', function (e) {
      if (panelOpen && !panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
        panelOpen = false;
        panel.classList.remove('open');
      }
    });
  }

  // ── Init ──────────────────────────────────────────────────────────────────

  injectStyles();
  buildUI();
  wrapAnalytics();

})();
