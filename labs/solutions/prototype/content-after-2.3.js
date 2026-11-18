/* Reference state after labs 1.4, 2.1 and 2.3 (trust cues, disclosure, undo). Copy over labs/prototype/content.js to show it.
   Sayyib Assistant prototype: everything a participant changes without touching code.
   Edit the text between the quotes, save, and reload index.html in the browser.
   Keep a copy of each version you test (content-v1.js, content-v2.js): it is your design history.
   The replies are scripted sample text written for the course, not the output of a model. */
window.SAYYIB = {
  /* The assistant's name line at the top of the conversation (lab 2.1) */
  name: 'مساعد صيّب (ذكاء اصطناعي)',

  /* The three onboarding screens (lab 1.4) */
  onboarding: [
    'مساعد صيّب برنامج ذكاء اصطناعي. يجيب عن الفواتير والتعرفة والمواعيد، ويحجز زيارات الفنيين بعد أن تؤكد.',
    'لا يعرف بعد متى تعود المياه بعد الانقطاع، ولا يقرر خطط السداد. لنقل الخدمة استخدم صفحتها أو اطلب موظفًا.',
    'اكتب بالعربية أو الإنجليزية. يفهم الرسائل المختلطة والعربيزي أقل. اطلب موظفًا في أي وقت.'
  ],

  /* true: show the source page under each reply that has one (lab 1.4) */
  showSources: true,

  /* true: show the model's confidence number under every reply (lab 1.4) */
  showConfidence: false,

  /* A caution shown under the reply of one topic. Topics: bill, outage, tariff, moving, plan.
     Example: outage: 'نص التنبيه'. Leave empty for none (lab 1.4). */
  cautions: {
    outage: 'وقت العودة غير مؤكد. تابع صفحة الانقطاعات أو اطلب موظفًا.',
    moving: 'لنقل الخدمة: صفحة نقل الخدمة في التطبيق، أو موظف.'
  },

  /* The line under every reply (lab 2.1). Empty for none. */
  footer: '',

  /* Where "talk to a person" appears: 'menu' (inside the settings menu) or 'always' (lab 2.1) */
  personButton: 'always',

  /* Seconds the "undo" button stays after the agent books a visit; 0 for none (lab 2.3) */
  undoSeconds: 30,

  /* Test mode (labs 3.3 and 3.4, and the capstone): open index.html?test=1.
     seeded: the planted errors shown in test mode. The lab uses E1, E2 and E3.
     For the capstone choose two others from E4 to E9 and tell no one which. */
  test: {
    seeded: ['E1', 'E2', 'E3']
  }
};
