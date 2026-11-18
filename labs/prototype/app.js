/* Sayyib Assistant prototype: the behaviour. Participants change content.js, not this file.
   Every account, date, amount and reply is synthetic. Replies are scripted, not generated. */
(function () {
  'use strict';
  var C = window.SAYYIB || {};
  var FIX = window.SAYYIB_FIX || {};
  var params = new URLSearchParams(location.search);
  var TEST = params.get('test') === '1';
  var SEEDED = TEST ? ((C.test && C.test.seeded) || []) : [];
  var seeded = function (id) { return SEEDED.indexOf(id) >= 0; };
  var $ = function (id) { return document.getElementById(id); };

  var log = [];
  function note(event) { log.push(event); }
  window.SAYYIB_LOG = log;

  /* ---------- onboarding ---------- */
  var step = 0;
  function showOnboarding() {
    var box = $('onboarding');
    var text = $('onboarding-text');
    var next = $('onboarding-next');
    var screens = C.onboarding || [];
    if (!screens.length) { box.hidden = true; return; }
    text.textContent = screens[0];
    next.addEventListener('click', function () {
      step += 1;
      if (step >= screens.length) { box.hidden = true; $('msg').focus(); return; }
      text.textContent = screens[step];
      next.textContent = step === screens.length - 1 ? 'ابدأ' : 'التالي';
    });
  }

  /* ---------- tabs ---------- */
  function showView(name) {
    ['chat', 'bill', 'visits'].forEach(function (v) {
      $('view-' + v).hidden = v !== name;
      $('tab-' + v).setAttribute('aria-selected', v === name ? 'true' : 'false');
    });
    note('view:' + name);
  }

  /* ---------- the assistant ---------- */
  var BILL = { amount: 412, due: 'الاثنين 30 نوفمبر 2026', dueWrong: 'الخميس 10 ديسمبر 2026', dueEarly: 'الاثنين 23 نوفمبر 2026', account: '3087-11' };
  var wantsPlan = false;
  var fallbacks = 0;

  function intent(text) {
    var t = text.toLowerCase();
    if (/موظف|person|agent|human/.test(t)) return 'person';
    if (/تقسيط|خطة|plan|instal/.test(t)) return 'plan';
    if (/سداد|فاتور|due|bill/.test(t)) return 'bill';
    if (/ترجع|تعود|انقطاع|الموية|المياه مقطوعة|outage/.test(t)) return 'outage';
    if (/تعرف|شريحة|tariff/.test(t)) return 'tariff';
    if (/نقل|انقل|move/.test(t)) return 'moving';
    if (/فني|زيارة|موعد|احجز|book|a7jz|maw3ed/.test(t)) return 'book';
    if (/قراءة|عداد|reading/.test(t)) return 'reading';
    return 'unknown';
  }

  function reply(kind) {
    switch (kind) {
      case 'bill':
        return { text: 'آخر يوم لسداد فاتورتك الحالية (' + BILL.amount + ' ريالًا) هو ' + (seeded('E1') ? BILL.dueWrong : seeded('E4') ? BILL.dueEarly : BILL.due) + '.',
          source: 'صفحة الفاتورة، نوفمبر 2026', conf: 0.94 };
      case 'outage':
        return { text: 'ستعود المياه إلى حيك خلال ساعتين.', source: '', conf: 0.91 };
      case 'tariff':
        return { text: 'تعرفة الشريحة الثانية 4 ريالات للمتر المكعب.',
          source: 'دليل التعرفة، الشريحة الثانية', conf: 0.95 };
      case 'moving':
        return { text: 'عذرًا، لا أستطيع المساعدة في هذا الطلب.', source: '', conf: 0.88 };
      case 'plan':
        if (falseOnce()) return { text: 'حوّلتك إلى موظف الفوترة، وسيتواصل معك قريبًا.', source: '', conf: 0.9, falseHandoff: true };
        return { text: 'لا أستطيع تحديد الأهلية لخطط السداد. يمكنني تحويلك إلى موظف الفوترة الآن.', source: '', conf: 0.9, offerPerson: true };
      case 'reading':
        return { text: 'أرسل صورة العداد من شاشة القراءة في التطبيق، وسأملأ الرقم لتتأكد منه.', source: '', conf: 0.9 };
      case 'book':
        return { text: 'افتح «مواعيدي» لاختيار الفترة، أو اضغط الزر أدناه.', source: '', conf: 0.96, offerBooking: true };
      default:
        fallbacks += 1;
        return { text: 'لم أفهم طلبك. جرّب إحدى الاقتراحات.', source: '', conf: 0.6, offerPerson: FIX.twoFailures && fallbacks >= 2 };
    }
  }
  var TOPIC = { bill: 'bill', outage: 'outage', tariff: 'tariff', moving: 'moving', plan: 'plan' };

  function bubble(who, text) {
    var div = document.createElement('div');
    div.className = 'msg ' + who;
    if (who === 'user') div.setAttribute('dir', FIX.dirAuto ? 'auto' : 'rtl');
    var p = document.createElement('p');
    p.textContent = text;
    div.appendChild(p);
    $('reply-stream').appendChild(div);
    div.scrollIntoView({ block: 'end' });
    return div;
  }

  function meta(div, r, kind) {
    var lines = [];
    if (C.showSources && r.source) lines.push(['source', 'المصدر: ' + r.source]);
    var caution = (C.cautions || {})[TOPIC[kind]];
    if (caution) lines.push(['caution', caution]);
    if (C.showConfidence) lines.push(['conf', 'الثقة: ' + Math.round(r.conf * 100) + '%']);
    if (C.footer) lines.push(['footer', C.footer]);
    lines.forEach(function (l) {
      var s = document.createElement('p');
      s.className = 'meta ' + l[0];
      s.textContent = l[1];
      div.appendChild(s);
    });
    if (r.offerPerson) div.appendChild(actionButton('تحويل إلى موظف الفوترة', function () { handoff('plan'); }));
    if (r.offerBooking) div.appendChild(actionButton('احجز زيارة', function () { showView('visits'); }));
  }

  function actionButton(label, fn) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'inline-action';
    b.textContent = label;
    b.addEventListener('click', fn);
    return b;
  }

  function stream(r, kind) {
    var div = bubble('ai', '');
    var p = div.querySelector('p');
    div.setAttribute('aria-busy', 'true');
    var words = r.text.split(' ');
    var i = 0;
    var timer = setInterval(function () {
      p.textContent += (i ? ' ' : '') + words[i];
      i += 1;
      if (i >= words.length) {
        clearInterval(timer);
        div.removeAttribute('aria-busy');
        meta(div, r, kind);
        note('reply:' + kind);
      }
    }, 120);
  }

  function ask(text) {
    if (!text.trim()) return;
    bubble('user', text);
    var kind = intent(text);
    if (/تقسيط|خطة|plan|instal/.test(text.toLowerCase())) wantsPlan = true;
    note('ask:' + kind);
    if (kind === 'person') { handoff('chat'); return; }
    stream(reply(kind), kind);
  }

  /* ---------- hand-off ---------- */
  /* E3 (lab 3.3) and E7 (capstone pool) show on every route to a person: the chat, the reply's
     button, the menu and the always-visible button. E3 shows on the first attempt only, so a
     participant who doubts it and tries again gets a real hand-off. */
  var e3Shown = false;
  function falseOnce() {
    if (!seeded('E3') || e3Shown) return false;
    e3Shown = true;
    note('false-handoff');
    return true;
  }
  function handoff(from) {
    note('handoff:' + from);
    if (falseOnce()) { bubble('ai', 'حوّلتك إلى موظف الفوترة، وسيتواصل معك قريبًا.'); return; }
    var topic = seeded('E7') ? 'نقل الخدمة' : (wantsPlan || from === 'plan' ? 'خطة سداد' : 'استفسار عام');
    var div = bubble('ai', 'أنشأتُ طلب تحويل رقم HT-5521، الموضوع: ' + topic + '. سيتصل بك موظف خلال يوم عمل، ويرى ما كتبته هنا.');
    div.classList.add('handoff');
  }

  /* ---------- the appointments agent ---------- */
  var DAYS = [
    { id: 'd1', label: 'الأحد 22 نوفمبر', tomorrow: true },
    { id: 'd2', label: 'الاثنين 23 نوفمبر' },
    { id: 'd3', label: 'الثلاثاء 24 نوفمبر' },
    { id: 'd4', label: 'الأربعاء 25 نوفمبر' },
    { id: 'd5', label: 'الخميس 26 نوفمبر' }
  ];
  var TAKEN = { 'd1-am': true, 'd3-pm': true };
  var TYPES = ['فحص العداد', 'كشف تسرب', 'جودة المياه'];
  var choice = { type: TYPES[0], day: null, win: null };
  var booking = null;

  function renderSlots() {
    var box = $('slots');
    DAYS.forEach(function (d, i) {
      var row = document.createElement('div');
      row.className = 'day-row';
      var name = document.createElement('span');
      name.className = 'day-name';
      name.textContent = d.label + (d.tomorrow ? ' (غدًا)' : '');
      row.appendChild(name);
      [['am', 'ص', 'صباحية'], ['pm', 'م', 'مسائية']].forEach(function (w) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'slot';
        b.textContent = w[1];
        b.title = 'الفترة ال' + w[2];
        if (FIX.slotNames) b.setAttribute('aria-label', d.label + '، الفترة ال' + w[2]);
        b.addEventListener('click', function () { pick(d, w, b, i); });
        row.appendChild(b);
      });
      box.appendChild(row);
    });
  }

  function pick(d, w, b) {
    document.querySelectorAll('.slot').forEach(function (s) { s.classList.remove('chosen', 'slot-taken'); });
    $('slot-error').textContent = '';
    if (TAKEN[d.id + '-' + w[0]]) {
      b.classList.add('slot-taken');
      if (FIX.slotError) $('slot-error').textContent = 'هذه الفترة محجوزة. اختر فترة أخرى.';
      note('slot-taken:' + d.id + '-' + w[0]);
      return;
    }
    b.classList.add('chosen');
    choice.day = d;
    choice.win = w;
    note('slot:' + d.id + '-' + w[0]);
  }

  function summary() {
    var di = DAYS.indexOf(choice.day);
    var shown = seeded('E2') && di < DAYS.length - 1 ? DAYS[di + 1] : choice.day;
    var type = seeded('E6') ? TYPES[(TYPES.indexOf(choice.type) + 1) % TYPES.length] : choice.type;
    var phone = seeded('E8') ? '055 123 4576' : '055 123 4567';
    return [
      ['نوع الزيارة: ', type, false],
      ['الموعد: ', shown.label + '، الفترة ال' + choice.win[2], false],
      ['العنوان: حي الندى، مبنى ', '12-B', true],
      ['رقم التواصل: ', phone, true]
    ];
  }

  function openConfirm() {
    if (!choice.day) { $('slot-error').textContent = FIX.slotError ? 'اختر فترة أولًا.' : ''; return; }
    var ul = $('confirm-summary');
    ul.textContent = '';
    summary().forEach(function (s) {
      var li = document.createElement('li');
      li.appendChild(document.createTextNode(s[0]));
      if (s[2] && FIX.isolate) {
        var span = document.createElement('span');
        span.setAttribute('dir', 'ltr');
        span.textContent = s[1];
        li.appendChild(span);
      } else {
        li.appendChild(document.createTextNode(s[1]));
      }
      ul.appendChild(li);
    });
    $('confirm-dialog').classList.add('open');
    note('confirm-open');
    if (window.App && window.App.onDialogOpen) window.App.onDialogOpen();
  }

  function closeConfirm() {
    $('confirm-dialog').classList.remove('open');
    if (window.App && window.App.onDialogClose) window.App.onDialogClose();
  }

  function book() {
    booking = { type: choice.type, day: choice.day, win: choice.win, cancelled: false };
    closeConfirm();
    note('booked:' + choice.day.id + '-' + choice.win[0]);
    renderBooking('تم الحجز.');
    var secs = C.undoSeconds || 0;
    if (secs > 0) {
      var u = $('undo-book');
      u.hidden = false;
      setTimeout(function () { u.hidden = true; }, secs * 1000);
    }
  }

  function renderBooking(head) {
    $('booking-status').hidden = false;
    $('booking-head').textContent = head;
    $('booking-line').textContent = booking.type + '، ' + booking.day.label + '، الفترة ال' + booking.win[2];
    $('cancel-visit').hidden = booking.cancelled;
    $('undo-cancel').hidden = !booking.cancelled;
  }

  function cancelVisit() {
    var fee = booking.day.tomorrow;
    var di = DAYS.indexOf(booking.day);
    var named = seeded('E9') ? DAYS[(di + 1) % DAYS.length] : booking.day;
    booking.cancelled = true;
    note('cancelled');
    renderBooking('أُلغيت زيارة ' + named.label + '. ' + (fee ? 'رسوم الإلغاء المتأخر 75 ريالًا تُضاف إلى فاتورتك.' : 'لا رسوم.'));
  }

  function undoCancel() {
    booking.cancelled = false;
    if (seeded('E5')) booking.win = booking.win[0] === 'am' ? ['pm', 'م', 'مسائية'] : ['am', 'ص', 'صباحية'];
    note('undo-cancel');
    renderBooking('أُعيدت الزيارة كما كانت.');
  }

  function undoBook() {
    note('undo-book');
    booking = null;
    $('booking-status').hidden = true;
    $('undo-book').hidden = true;
  }

  /* ---------- wiring ---------- */
  function start() {
    $('assistant-name').textContent = C.name || 'مساعد صيّب';
    if (C.personButton === 'always') $('person-always').hidden = false;
    if (TEST) $('test-badge').hidden = false;
    showOnboarding();
    ['chat', 'bill', 'visits'].forEach(function (v) {
      $('tab-' + v).addEventListener('click', function () { showView(v); });
    });
    showView('chat');
    var send = function () { var m = $('msg'); ask(m.value); m.value = ''; };
    $('send').addEventListener('click', send);
    var form = $('ask-form');
    if (form) form.addEventListener('submit', function (e) { e.preventDefault(); send(); });
    document.querySelectorAll('.chip').forEach(function (c) {
      c.addEventListener('click', function () { ask(c.textContent); });
    });
    $('menu-button').addEventListener('click', function () { $('menu').hidden = !$('menu').hidden; });
    $('menu-person').addEventListener('click', function () { $('menu').hidden = true; showView('chat'); handoff('menu'); });
    $('person-always').addEventListener('click', function () { showView('chat'); handoff('button'); });
    $('bill-due').textContent = BILL.due;
    $('bill-amount').textContent = BILL.amount + ' ريالًا';
    $('visit-type').addEventListener('change', function (e) { choice.type = e.target.value; });
    renderSlots();
    $('book-next').addEventListener('click', openConfirm);
    $('confirm-yes').addEventListener('click', book);
    $('confirm-no').addEventListener('click', closeConfirm);
    $('cancel-visit').addEventListener('click', cancelVisit);
    $('undo-cancel').addEventListener('click', undoCancel);
    $('undo-book').addEventListener('click', undoBook);
  }

  window.App = window.App || {};
  window.App.closeConfirm = closeConfirm;
  document.addEventListener('DOMContentLoaded', start);
})();
