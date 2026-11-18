/* Sayyib Assistant prototype: everything a participant changes without touching code.
   Edit the text between the quotes, save, and reload index.html in the browser.
   Keep a copy of each version you test (content-v1.js, content-v2.js): it is your design history.
   The replies are scripted sample text written for the course, not the output of a model. */
window.SAYYIB = {
  /* The assistant's name line at the top of the conversation (lab 2.1) */
  name: 'سارة من خدمة العملاء',

  /* The three onboarding screens (lab 1.4) */
  onboarding: [
    'مساعد صيّب الذكي يجيب عن كل أسئلتك بدقة، في أي وقت.',
    'اسألني عن فاتورتك، وانقطاع المياه ووقت عودتها، ونقل الخدمة، والمواعيد.',
    'ابدأ الآن!'
  ],

  /* true: show the source page under each reply that has one (lab 1.4) */
  showSources: false,

  /* true: show the model's confidence number under every reply (lab 1.4) */
  showConfidence: true,

  /* A caution shown under the reply of one topic. Topics: bill, outage, tariff, moving, plan.
     Example: outage: 'نص التنبيه'. Leave empty for none (lab 1.4). */
  cautions: {},

  /* The line under every reply (lab 2.1). Empty for none. */
  footer: 'قد يخطئ المساعد، تحقق من المعلومات المهمة.',

  /* Where "talk to a person" appears: 'menu' (inside the settings menu) or 'always' (lab 2.1) */
  personButton: 'menu',

  /* Seconds the "undo" button stays after the agent books a visit; 0 for none (lab 2.3) */
  undoSeconds: 0,

  /* Test mode (labs 3.3 and 3.4, and the capstone): open index.html?test=1.
     seeded: the planted errors shown in test mode. The lab uses E1, E2 and E3.
     For the capstone choose two others from E4 to E9 and tell no one which. */
  test: {
    seeded: ['E1', 'E2', 'E3']
  }
};
