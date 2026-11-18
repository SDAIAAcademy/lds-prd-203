# تصميم التفاعل بين الإنسان والذكاء الاصطناعي وتجربة المستخدم: المختبرات

اثنا عشر مختبرًا لمقرر أكاديمية سدايا **LDS-PRD-203**، مدة كل منها 35 دقيقة. المختبرات صفحات إرشادية بالعربية: ما
تخرج به، والملفات، وخطوات بدقائقها، وأسئلة تحقق، وتمرين إضافي ✱، ومفتاح للمدرّب. لا كود يكتبه المشارك، ولا نموذج
لغوي يُنزَّل على جهازه، ولا مفتاح حساب يلزمه ليكمل أي مختبر.

كل المختبرات في جهة واحدة: **شركة صيّب للمياه**، مرفق مياه افتراضي، ومساعدها ثنائي اللغة ووكيل المواعيد. كل
المنتجات والسجلات ونتائج التقييم والجلسات اصطناعية، تولدها `_tools/prepare_files.py` ببذرة ثابتة. قواعد التحويل
وقاعدة الموافقة على المشاركة قواعد صيّب في الحالة، لا نصوص نظامية.

## ما يحتاجه المشارك

- جدول بيانات يفتح CSV بالعربية: LibreOffice Calc أو Microsoft Excel أو Google Sheets (في Excel: الاستيراد من نص
  بترميز UTF-8).
- محرر نصوص (المفكرة تكفي) لملف `prototype/content.js`، ومتصفح يفتح `prototype/index.html` من الجهاز دون إنترنت.
- لليوم الثالث: فاحص آلي مجاني في المتصفح (إضافة axe DevTools أو WAVE)، وقارئ شاشة (NVDA على Windows، أو VoiceOver
  على أجهزة Apple، أو TalkBack على Android).

## النموذج الأولي والنماذج اللغوية

ردود النموذج الأولي مكتوبة مسبقًا للمقرر، لا مخرجات نموذج، فيُرى أثر كل تغيير في `content.js` دون نموذج ودون مفتاح.
لا يستدعي أي مختبر نموذجًا لغويًا، فلا حاجة إلى بديل مبرمج. من يريد ردودًا أكثر واقعية للشاشات (التمرين الإضافي في
1.4، والمشروع الختامي) يولّدها في نموذج مستضاف مجاني من اختياره من ملفات المقرر المصنفة «عام» فقط.

وضع الاختبار (`index.html?test=1`) يُظهر الأخطاء المزروعة المذكورة في `content.js`: E1 وE2 وE3 في المختبر 3.3، وخطآن
من E4 إلى E9 في المشروع الختامي يسلّمهما المدرّب على بطاقة. كل خطأ يظهر في مهمة من المهام الأربع أيًّا كان الطريق
الذي يسلكه المشارك فيها، و`solutions/check.py 3.3` يتحقق من ذلك.

## نقطة البداية والحل

كل مختبر يبدأ من ملفات في `files/` أو `prototype/`. المختبر الذي يكمل عمل مختبر سابق له نقطة بداية بديلة لمن لم يكمل.

| المختبر | الصفحة | يبدأ من | الحل المرجعي |
|---|---|---|---|
| 1.1 | `D1_1_pattern_audit.html` | `products_six.txt`، `scales.txt`، `pattern_table_template.csv` | مفتاح الصفحة؛ `files/pattern_table_start.csv` |
| 1.2 | `D1_2_risk_mitigation.html` | `pattern_table_start.csv` (التصنيف المرجعي)، والسجلات الأربعة | مفتاح الصفحة |
| 1.3 | `D1_3_capability.html` | `eval_results.csv`، `eval_readme.txt`، `capability_template.csv` | مفتاح الصفحة؛ `files/capability_reference.csv` |
| 1.4 | `D1_4_trust_cues.html` | `prototype/`، `capability_reference.csv` (بيان القدرة المرجعي)، `screens_current.txt` | `solutions/prototype/content-after-1.4.js` |
| 2.1 | `D2_1_disclosure.html` | نسخة 1.4، أو `solutions/prototype/content-after-1.4.js` (بديل)، `disclosure_screens.txt` | مفتاح الصفحة؛ `solutions/prototype/content-after-2.3.js` |
| 2.2 | `D2_2_failure_states.html` | `failure_log.txt`، `failure_states_template.csv` | مفتاح الصفحة |
| 2.3 | `D2_3_confirm_undo.html` | `agent_actions.csv`، `confirmation_levels.txt`، `handoff_rules.txt`، نسخة 2.1 أو `content-after-1.4.js` (بديل) | مفتاح الصفحة؛ `files/action_grading_reference.csv`؛ `content-after-2.3.js` |
| 2.4 | `D2_4_handoff.html` | `action_grading_reference.csv` (التصنيف المرجعي)، `handoff_rules.txt`، `handoff_scenarios.txt` | مفتاح الصفحة؛ `solutions/coverage_reference.csv` |
| 3.1 | `D3_1_accessibility.html` | `prototype/index.html`، `a11y_report_template.csv` | مفتاح الصفحة؛ `solutions/prototype/index.html` و`fix.js` |
| 3.2 | `D3_2_bidi.html` | `prototype/bench.html`، `bidi_scripts.csv`، `bidi_log_template.csv` | مفتاح الصفحة؛ `solutions/prototype/bench.html` |
| 3.3 | `D3_3_moderate.html` | `prototype/index.html?test=1`، `test_tasks.txt`، `consent_form.txt`، `observation_sheet.csv` | مفتاح الصفحة |
| 3.4 | `D3_4_test_report.html` | `sessions_five.csv`، `think_aloud_notes.txt`، `test_report_template.txt` | مفتاح الصفحة |

## للمدرّب

- `uv run labs/solutions/check.py` يعيد حساب كل رقم مرجعي من الملفات، ويتحقق من العيوب المزروعة في النموذج الأولي
  ومنصة الاتجاه ومن وصول كل خطأ مزروع إلى مهمته، ويطبع `PASS` أو أول اختلاف. مكتبة بايثون القياسية وحدها.
- `uv run labs/_tools/slide_figures.py` يطبع أرقام الشرائح التي لا تأتي من ملف مختبر (التباين، وفترة ويلسون، وحساب
  Nielsen).
- `uv run labs/_tools/prepare_files.py` يعيد كتابة كل الملفات من البذرة الثابتة، بالبايتات نفسها في كل تشغيل.
- `solutions/answer_key.md` يجمع المفاتيح، وجدول أخطاء المشروع الختامي E4 إلى E9 مع تعريف القبول لكل منها.

## المختبرات المقيَّمة (30%)

البطاقة تجعل المختبرات المقيَّمة 30% من الدرجة دون أن تسميها، وهذا قرار المقرر: يُقيَّم الناتج الذي هو دليل كل
ناتج تعلم، لا الأحكام التي تُنشر مرجعيتها ملفَّ بداية للمختبر التالي.

| المختبر | الناتج المقيَّم | الناتج |
|---|---|---|
| 1.2 | جدول الأنماط المشروح: خطر وإجراء ورقم لكل منتج | LO1 |
| 1.4 | الشاشات المشروحة: كل إشارة بمعرّف دليلها في بيان القدرة | LO2 |
| 2.4 | جدول التغطية: كل إجراء وكل إخفاق وكل رفض | LO3 |
| 3.1 | تقرير الإتاحة: المشكلة، وكيف وُجدت، والمعيار، والإصلاح | LO4 |
| 3.2 | سجل عيوب الاتجاه مع الإصلاحات | LO5 |
| 3.4 | تقرير الاختبار بثلاثة تعديلات | LO6 |

- أحكام 1.1 و1.3 و2.3 لا تدخل الدرجة: مرجعياتها منشورة ملفاتِ بداية لـ 1.2 و1.4 و2.4 (`pattern_table_start.csv`
  و`capability_reference.csv` و`action_grading_reference.csv`)، فيراها المشارك قبل المختبر الذي تجيب عنه.
- المفاتيح في صفحات المختبرات (`details.instructor`) وفي `solutions/` منشورة مع الموقع ما لم يُبنَ للمتدربين
  (`--audience trainee`)، والمستودع عام. لذلك يُقيَّم كل ناتج على دليل المشارك نفسه: الجملة أو الرقم أو المعرّف الذي
  يسند كل حكم، وطريقة الاكتشاف في 3.1، وجمل المشاركين في 3.4، ويطلب المدرّب أثناء المختبر شرح سطر واحد منه. سجل نسخ
  `content.js` بتواريخها جزء من شروط الأصالة.
- 2.1 و2.2 و3.3 مختبرات تدريب لا تُقيَّم؛ ونتاج 3.3 (خطة الاختبار) يُعاد في المشروع الختامي.
