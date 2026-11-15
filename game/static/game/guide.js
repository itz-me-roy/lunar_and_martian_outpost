/* Hover guides: one floating bubble that glides between things, a character per topic.
   Works with mouse (hover), touch (tap), and keyboard (focus). */
(function () {
  'use strict';
  var root = document.body;
  var dataEl = document.getElementById('guide-data');
  if (!dataEl) return;
  var D = JSON.parse(dataEl.textContent);
  var TIPS = D.tips, CHARS = D.characters;
  var novaUrl = root.getAttribute('data-nova') || '';

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---- characters (Beep and Sunny are drawn here; Nova is the picture) ---- */
  var SVG = {
    beep: '<svg viewBox="0 0 64 64" aria-hidden="true"><line x1="32" y1="6" x2="32" y2="15" stroke="#9fb4ff" stroke-width="3" stroke-linecap="round"/><circle cx="32" cy="6" r="4" fill="#ffd166"/><rect x="10" y="15" width="44" height="36" rx="12" fill="#c9d6ff"/><rect x="16" y="22" width="32" height="20" rx="8" fill="#1d2650"/><circle class="eye" cx="25" cy="32" r="4.5" fill="#3ddc97"/><circle class="eye" cx="39" cy="32" r="4.5" fill="#3ddc97"/><rect class="mouth" x="27" y="45" width="10" height="3" rx="1.5" fill="#1d2650"/><rect x="4" y="27" width="6" height="12" rx="3" fill="#9fb4ff"/><rect x="54" y="27" width="6" height="12" rx="3" fill="#9fb4ff"/></svg>',
    sunny: '<svg viewBox="0 0 64 64" aria-hidden="true"><g class="rays" stroke="#ffb347" stroke-width="4" stroke-linecap="round"><line x1="32" y1="2" x2="32" y2="10"/><line x1="32" y1="54" x2="32" y2="62"/><line x1="2" y1="32" x2="10" y2="32"/><line x1="54" y1="32" x2="62" y2="32"/><line x1="11" y1="11" x2="17" y2="17"/><line x1="47" y1="47" x2="53" y2="53"/><line x1="11" y1="53" x2="17" y2="47"/><line x1="47" y1="17" x2="53" y2="11"/></g><circle cx="32" cy="32" r="18" fill="#ffd34d"/><circle cx="26" cy="29" r="2.8" fill="#5a3300"/><circle cx="38" cy="29" r="2.8" fill="#5a3300"/><path class="mouth" d="M24 37 Q32 45 40 37" stroke="#5a3300" stroke-width="3" fill="none" stroke-linecap="round"/><circle cx="22" cy="36" r="3" fill="#ff9a6b" opacity=".6"/><circle cx="42" cy="36" r="3" fill="#ff9a6b" opacity=".6"/></svg>'
  };
  function avatar(who) {
    if (who === 'nova') return '<img src="' + novaUrl + '" alt="">';
    return SVG[who] || '';
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-av]'), function (n) { n.innerHTML = avatar(n.getAttribute('data-av')); });
  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  /* ---- the bubble ---- */
  var bubble = document.createElement('div');
  bubble.className = 'tipbubble';
  bubble.setAttribute('role', 'tooltip');
  bubble.id = 'tipbubble';
  bubble.innerHTML = '<div class="tb-arrow"></div><div class="tb-av"></div><div class="tb-body"><div class="tb-name"></div>' +
    '<div class="tb-title"></div><div class="tb-say"></div><div class="tb-like"></div></div>';
  document.body.appendChild(bubble);
  var el = {
    av: bubble.querySelector('.tb-av'), name: bubble.querySelector('.tb-name'),
    title: bubble.querySelector('.tb-title'), say: bubble.querySelector('.tb-say'),
    like: bubble.querySelector('.tb-like'), arrow: bubble.querySelector('.tb-arrow')
  };

  var current = null, showTimer = 0, hideTimer = 0, visible = false, placedOnce = false;
  var enabled = store.get('guideOff') !== '1';

  function fill(tip) {
    var c = CHARS[tip.who] || CHARS.nova;
    bubble.setAttribute('data-who', tip.who);
    el.av.innerHTML = avatar(tip.who);
    el.name.textContent = c.name + ' · ' + c.role;
    el.title.textContent = tip.title;
    el.say.textContent = tip.say;
    el.like.innerHTML = tip.like ? '💡 <em>' + esc(tip.like) + '</em>' : '';
  }

  function place(target) {
    var gap = 14, margin = 12;
    var vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var r = target.getBoundingClientRect();
    var bw = bubble.offsetWidth, bh = bubble.offsetHeight;
    var below = r.bottom + gap + bh <= vh - margin;
    var above = r.top - gap - bh >= margin;
    var top, side;
    if (below || !above) { top = r.bottom + gap; side = 'below'; }
    else { top = r.top - gap - bh; side = 'above'; }
    if (top + bh > vh - margin) top = Math.max(margin, vh - margin - bh);
    var left = r.left + r.width / 2 - bw / 2;
    left = Math.max(margin, Math.min(left, vw - bw - margin));
    var ax = r.left + r.width / 2 - left;
    ax = Math.max(24, Math.min(ax, bw - 24));
    el.arrow.style.left = ax + 'px';
    bubble.setAttribute('data-side', side);
    bubble.style.transform = 'translate3d(' + Math.round(left) + 'px,' + Math.round(top) + 'px,0)';
  }

  function show(target) {
    var key = target.getAttribute('data-tip');
    var tip = TIPS[key];
    if (!tip || !enabled) return;
    clearTimeout(hideTimer);
    var changed = current !== target;
    current = target;
    if (changed) {
      fill(tip);
      target.setAttribute('aria-describedby', 'tipbubble');
    }
    if (!placedOnce) {                       // first time: appear in place, then glide afterwards
      bubble.classList.add('notrans');
      place(target);
      void bubble.offsetWidth;
      bubble.classList.remove('notrans');
      placedOnce = true;
    } else {
      place(target);
    }
    if (changed && visible) {                // pop the character when the speaker changes
      bubble.classList.remove('swap'); void bubble.offsetWidth; bubble.classList.add('swap');
    }
    visible = true;
    bubble.classList.add('on');
  }
  function hide() {
    clearTimeout(showTimer);
    hideTimer = setTimeout(function () {
      visible = false; placedOnce = false;
      bubble.classList.remove('on');
      if (current) current.removeAttribute('aria-describedby');
      current = null;
    }, 140);
  }

  function tipTarget(node) { return node && node.closest ? node.closest('[data-tip]') : null; }

  /* mouse / pen hover with a short intent delay so it doesn't flicker */
  document.addEventListener('pointerover', function (e) {
    if (e.pointerType === 'touch') return;
    var t = tipTarget(e.target);
    if (!t) return;
    clearTimeout(hideTimer); clearTimeout(showTimer);
    showTimer = setTimeout(function () { show(t); }, visible ? 0 : 90);
  });
  document.addEventListener('pointerout', function (e) {
    if (e.pointerType === 'touch') return;
    var t = tipTarget(e.target);
    if (!t) return;
    var to = e.relatedTarget;
    if (to && (t.contains(to) || bubble.contains(to))) return;
    if (to && tipTarget(to)) return;         // moving to another thing: it will take over
    hide();
  });
  bubble.addEventListener('pointerenter', function () { clearTimeout(hideTimer); });
  bubble.addEventListener('pointerleave', hide);

  /* touch: tap a thing to hear about it, tap elsewhere to close */
  document.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'touch') return;
    var t = tipTarget(e.target);
    if (t) { show(t); }
    else if (!bubble.contains(e.target)) { hide(); }
  });

  /* keyboard */
  document.addEventListener('focusin', function (e) { var t = tipTarget(e.target); if (t) show(t); });
  document.addEventListener('focusout', function (e) { if (tipTarget(e.target)) hide(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
  window.addEventListener('scroll', function () { if (visible && current) place(current); }, { passive: true });
  window.addEventListener('resize', function () { if (visible && current) place(current); });

  /* ---- the helper button (bottom-left): turn guides on/off, replay greeting ---- */
  var helper = document.createElement('button');
  helper.type = 'button';
  helper.className = 'helper';
  helper.innerHTML = '<span class="h-av">' + avatar('nova') + '</span><span class="h-txt"></span>';
  document.body.appendChild(helper);
  var hTxt = helper.querySelector('.h-txt');
  function syncHelper() {
    helper.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    helper.classList.toggle('off', !enabled);
    hTxt.textContent = enabled ? 'Helpers on' : 'Helpers off';
    helper.title = enabled ? 'Hover or tap anything with a dotted line. Click to turn helpers off.' : 'Click to turn helpers on';
  }
  helper.addEventListener('click', function () {
    enabled = !enabled; store.set('guideOff', enabled ? '0' : '1'); syncHelper();
    if (!enabled) hide(); else greet();
  });
  syncHelper();

  function greet() {
    if (!enabled) return;
    fill(D.greeting);
    placedOnce = false;
    bubble.classList.add('notrans');
    var r = helper.getBoundingClientRect();
    current = helper;
    place(helper);
    void bubble.offsetWidth;
    bubble.classList.remove('notrans');
    placedOnce = true; visible = true;
    bubble.classList.add('on');
    clearTimeout(hideTimer);
    hideTimer = setTimeout(hide, 7000);
  }
  if (store.get('guideSeen') !== '1') {
    store.set('guideSeen', '1');
    setTimeout(function () { if (!visible) greet(); }, 700);
  }
})();
