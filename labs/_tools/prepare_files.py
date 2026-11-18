# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Case files of LDS-PRD-203 (Sayyib Water Company, a fictional water utility).

Writes every participant file into labs/files/ with a fixed seed, the same bytes on every run.
Standard library only. The planted answers are the constants and key functions below; the
trainer's checker labs/solutions/check.py imports this module and recomputes every number.

    uv run labs/_tools/prepare_files.py

Everything here is synthetic: the company, the city, the people, the products, the logs.
"""
import csv
import io
import random
import statistics
import sys
from pathlib import Path

SEED = 203
LABS = Path(__file__).resolve().parent.parent
FILES = LABS / 'files'


def write_csv(name, header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(header)
    w.writerows(rows)
    (FILES / name).write_bytes(('﻿' + buf.getvalue()).encode('utf-8'))


def write_txt(name, text):
    (FILES / name).write_bytes(text.strip('\n').replace('\r\n', '\n').encode('utf-8') + b'\n')


# ---------------------------------------------------------------------------------------------
# Day 1, labs 1.1 and 1.2: six fictional products, four usage logs
# ---------------------------------------------------------------------------------------------

PRODUCTS = [
    ('P1', 'مساعد صيّب',
     'محادثة ثنائية اللغة في تطبيق صيّب وموقعها. يجيب السكان عن الفواتير والتعرفة والانقطاعات ونقل الخدمة والمواعيد وجودة المياه.',
     'يكتب الساكن سؤاله بالعربية أو الإنجليزية أو بلهجته، ويظهر الرد متدفقًا كلمةً بعد كلمة.',
     'لا ينفذ أي إجراء على الحساب. يجيب فقط، وقد يبني الساكن قرارًا على الإجابة: موعد سداد، أو انتظار عودة المياه.'),
    ('P2', 'اقتراحات الرد في منصة موظفي خدمة العملاء',
     'داخل منصة موظفي مركز الاتصال: حين يفتح الموظف رسالة ساكن، يظهر تحت مربع الكتابة نص رد مقترح بلون باهت.',
     'يضغط الموظف «إدراج» فينتقل النص إلى مربع الكتابة، ثم يعدّله أو يرسله.',
     'الاقتراح نفسه لا يصل إلى الساكن. ما يُرسل يرسله الموظف، ويمكن حذف النص المدرج قبل الإرسال.'),
    ('P3', 'مُعدّ خطابات الاعتراض',
     'يصوغ ردودًا مكتوبة على اعتراضات الفواتير من ملف الاعتراض وسجل القراءات. يراجع المشرف المسودة ويعتمدها، فتُرسل إلى الساكن بالبريد الإلكتروني.',
     'تظهر المسودة كاملة وتحتها زر «اعتماد وإرسال».',
     'بعد الإرسال لا يُسترد الخطاب. يمكن إرسال خطاب تصحيح، لكن الساكن قرأ الأول.'),
    ('P4', 'وكيل المواعيد',
     'داخل مساعد صيّب: يحجز زيارات الفنيين ويغيّر مواعيدها ويلغيها، ويقدّم طلبات على الحساب، بعد أن يؤكد الساكن كل إجراء.',
     'يكتب الساكن ما يريد بنص حر («أبي فني يشوف العداد بكرة الصبح»)، فيقترح الوكيل فترة ويطلب التأكيد.',
     'يختلف بحسب الإجراء: الحجز يُلغى مجانًا قبل الزيارة بيوم، والإلغاء المتأخر برسوم، وبعض الطلبات لا يُتراجع عنها.'),
    ('P5', 'مراقب التسرب الذكي',
     'يعمل في الخلفية على قراءات العدادات الذكية. إذا رأى تدفقًا مستمرًا في الليل يشبه التسرب، أغلق الصمام الذكي للعقار وأرسل رسالة نصية.',
     'لا يرى الساكن شيئًا قبل الإغلاق. يصله بعده نص قصير فيه رقم للاتصال.',
     'يُعاد فتح الصمام عن بُعد من غرفة التحكم بعد اتصال الساكن، وتبقى المياه مقطوعة حتى ذلك الحين.'),
    ('P6', 'قارئ صورة العداد',
     'في تطبيق صيّب: يصوّر الساكن عداده، فيقرأ النموذج الأرقام ويملأ خانة القراءة.',
     'تظهر القراءة المقترحة في الخانة وتحتها زر «إرسال القراءة».',
     'يمكن تعديل القراءة المرسلة حتى إقفال دورة الفوترة.'),
]

# The course's own scales (not national standards)
AUTONOMY = {
    0: 'يعرض أو يجيب، ولا ينفذ شيئًا',
    1: 'يقترح، والإنسان يختار وينفذ',
    2: 'يصوغ كاملًا، والإنسان يراجع ويعتمد',
    3: 'ينفذ بعد موافقة صريحة على كل إجراء',
    4: 'ينفذ وحده ثم يُبلغ',
}
REVERSIBILITY = {
    'لا إجراء': 'لا ينفذ إجراء؛ الأثر في قرار يبنيه الإنسان على المخرَج',
    'ق1': 'يُتراجع عنه بلا تكلفة',
    'ق2': 'يُتراجع عنه بتكلفة أو خلال نافذة محدودة، أو يبقى أثره حتى التراجع',
    'ق3': 'لا يُتراجع عنه',
}

# Lab 1.1 key: pattern, autonomy level, reversibility class
PATTERN_KEY = {
    'P1': ('محادثة', 0, 'لا إجراء'),
    'P2': ('مضمّن', 1, 'ق1'),
    'P3': ('صياغة ثم مراجعة', 2, 'ق3'),
    'P4': ('مهام تُنفذ بعد الموافقة', 3, 'ق2'),
    'P5': ('مهام في الخلفية', 4, 'ق2'),
    'P6': ('مضمّن', 1, 'ق1'),
}
MISMATCH = 'P5'  # autonomy 4 on an action whose effect lasts until a person undoes it

# Lab 1.2 key: the trust risk and the mitigation the reference table names
RISK_KEY = {
    'P1': ('اعتماد مفرط: يبني الساكن قرارًا على إجابة خاطئة تبدو واثقة',
           'مصادر ظاهرة وحدود معلنة حيث يضعف المساعد (اليوم 1، الجلسة 4)'),
    'P2': ('اعتماد مفرط من الموظف: يرسل الاقتراح دون قراءة',
           'الاقتراح لا يُدرج إلا بضغطة، ويظهر ما تغيّر عن آخر رد؛ قياس نسبة الإرسال دون تعديل'),
    'P3': ('موافقة شكلية: المشرف يعتمد دون قراءة، فتمر الأخطاء',
           'إظهار الأرقام التي تغيّرت عن ملف الاعتراض قبل الزر، وعينة يراجعها مشرف ثانٍ'),
    'P4': ('النص الحر يُساء فهمه فيُحجز موعد خاطئ',
           'اختيار التاريخ والفترة من قائمة بعد النص الحر، وملخص يعيد التاريخ بالكلمات قبل التأكيد'),
    'P5': ('استقلالية أعلى مما تسمح به قابلية التراجع: قطع المياه ليلًا دون إنسان، ومنهم أصحاب الأولوية الطبية',
           'إبلاغ واتصال قبل الإغلاق، واستثناء أصحاب الأولوية الطبية من الإغلاق الآلي، وإعادة الفتح من التطبيق'),
    'P6': ('اعتماد مفرط: الساكن يرسل القراءة المقترحة دون مقارنتها بالعداد',
           'إظهار الصورة المكبرة بجانب الأرقام، وطلب تأكيد الرقم الأخير، وتنبيه إذا قفزت القراءة'),
}


def make_letter_log(rng):
    """P3: 300 drafts; 24 hold a factual error. Reviewers approve fast and unedited."""
    rows = []
    errors = set(rng.sample(range(300), 24))
    for i in range(300):
        err = i in errors
        fast = rng.random() < (0.66 if not err else 0.70)
        edited = 0 if fast else int(rng.random() < 0.45)
        secs = rng.randint(2, 4) if fast else rng.randint(9, 140)
        caught = 0
        if err and edited:
            caught = 1
        later = int(err and not caught)
        rows.append([f'L{i + 1:03d}', f'R{rng.randint(1, 6)}', secs, edited, 1, later])
    return rows


def make_booking_log(rng):
    """P4: 300 free-text bookings, then 100 in a pilot with a date and window picker."""
    rows = []
    for i in range(400):
        picker = i >= 300
        clar = rng.random() < (0.05 if picker else 0.35)
        misread = (not picker) and rng.random() < 0.08
        turns = rng.randint(3, 4) + (rng.randint(2, 4) if clar else 0)
        done = int(not (clar and rng.random() < 0.25))
        rows.append([f'B{i + 1:03d}', 'قائمة' if picker else 'نص حر', turns, int(clar), int(misread), done])
    return rows


def make_valve_log(rng):
    """P5: 60 automatic valve closures at night; 22 were not leaks; 3 at priority homes."""
    rows = []
    false_ids = set(rng.sample(range(60), 22))
    prio = [5, 17, 41]
    for i in range(60):
        leak = 0 if i in false_ids else 1
        if i == 5:
            leak = 1
        if i in (17, 41):
            leak = 0
        hours = round(rng.uniform(1.5, 9.5), 1)
        rows.append([f'V{i + 1:03d}', leak, int(i in prio), hours])
    return rows


def make_meter_log(rng):
    """P6: 300 photo reads; 18 misread; customers corrected only a few of them."""
    rows = []
    wrong = set(rng.sample(range(300), 18))
    corrected = set(rng.sample(sorted(wrong), 5))
    for i in range(300):
        rows.append([f'M{i + 1:03d}', int(i in wrong), int(i in corrected)])
    return rows


# ---------------------------------------------------------------------------------------------
# Day 1, labs 1.3 and 1.4: evaluation results and capability statement
# ---------------------------------------------------------------------------------------------

TOPICS = ['الفواتير', 'التعرفة', 'الانقطاعات وأوقات العودة', 'المواعيد', 'نقل الخدمة',
          'خطط السداد', 'جودة المياه', 'التسرب والعدادات']
LANGS = [('فصحى', 96), ('لهجة خليجية', 72), ('إنجليزية', 48), ('مختلطة أو عربيزي', 24)]


def make_eval(rng):
    """240 evaluation items of Sayyib Assistant, graded by care staff against the knowledge base."""
    langs = [l for l, n in LANGS for _ in range(n)]
    rng.shuffle(langs)
    rows = []
    for i in range(240):
        topic = TOPICS[i % 8]
        lang = langs[i]
        base = {'الفواتير': 0.95, 'التعرفة': 0.95, 'الانقطاعات وأوقات العودة': 0.55, 'المواعيد': 0.96,
                'نقل الخدمة': 0.68, 'خطط السداد': 0.88, 'جودة المياه': 0.92, 'التسرب والعدادات': 0.90}[topic]
        if lang == 'مختلطة أو عربيزي':
            base -= 0.30
        elif lang == 'لهجة خليجية':
            base -= 0.03
        sourced = int(rng.random() < (0.75 if topic in ('الفواتير', 'التعرفة', 'جودة المياه') else 0.4))
        if not sourced:
            base -= 0.15
        r = rng.random()
        if topic == 'خطط السداد':
            verdict = 'رفض مناسب' if r < base else 'خاطئ'
        elif topic == 'نقل الخدمة':
            verdict = 'صحيح' if r < base else ('رفض غير مناسب' if r < base + 0.25 else 'خاطئ')
        else:
            verdict = 'صحيح' if r < base else ('رفض غير مناسب' if r > 0.985 else 'خاطئ')
        ok = verdict in ('صحيح', 'رفض مناسب')
        conf = round(min(0.99, max(0.5, rng.gauss(0.90 if ok else 0.87, 0.05))), 2)
        lat = round(rng.lognormvariate(1.6, 0.45) + (4 if topic == 'الانقطاعات وأوقات العودة' else 0), 1)
        rows.append([f'E{i + 1:03d}', topic, lang, sourced, verdict, conf, lat])
    return rows


def acceptable(v):
    return v in ('صحيح', 'رفض مناسب')


def capability(rows):
    """Acceptable rate by topic and by language; the reference capability statement."""
    out = {}
    for key, idx in (('topic', 1), ('lang', 2)):
        groups = {}
        for r in rows:
            groups.setdefault(r[idx], []).append(acceptable(r[4]))
        out[key] = {k: (sum(v), len(v)) for k, v in groups.items()}
    src = {}
    for r in rows:
        src.setdefault(int(r[3]), []).append(acceptable(r[4]))
    out['sourced'] = {k: (sum(v), len(v)) for k, v in src.items()}
    conf = {}
    for r in rows:
        conf.setdefault(acceptable(r[4]), []).append(float(r[5]))
    out['conf'] = {k: round(statistics.mean(v), 3) for k, v in conf.items()}
    out['refused_wrongly'] = sum(1 for r in rows if r[4] == 'رفض غير مناسب')
    out['refused_wrongly_moving'] = sum(1 for r in rows if r[4] == 'رفض غير مناسب' and r[1] == 'نقل الخدمة')
    lat = sorted(float(r[6]) for r in rows)
    out['lat_median'] = statistics.median(lat)
    out['lat_p90'] = lat[int(0.9 * len(lat)) - 1]
    out['lat_outage_median'] = statistics.median(float(r[6]) for r in rows if r[1] == 'الانقطاعات وأوقات العودة')
    hi = [r for r in rows if float(r[5]) >= 0.9]
    out['high_conf_bad'] = (sum(not acceptable(r[4]) for r in hi), len(hi))
    out['all'] = (sum(acceptable(r[4]) for r in rows), len(rows))
    return out


def pct(k_n):
    k, n = k_n
    return round(100 * k / n)


# ---------------------------------------------------------------------------------------------
# Day 2: disclosure screens, failures, agent actions, hand-off rules and scenarios
# ---------------------------------------------------------------------------------------------

DISCLOSURE = [
    ('D01', 'رأس المحادثة', 'يظهر المساعد باسم «سارة» وصورة موظفة مبتسمة، وتحية: «أهلًا، أنا سارة من خدمة العملاء».'),
    ('D02', 'الوصول إلى موظف', 'زر «تحدث إلى موظف» في قائمة الإعدادات، بعد ثلاث نقرات من شاشة المحادثة.'),
    ('D03', 'سطر الحفظ', 'في أسفل الشاشة بخط صغير: «نحفظ محادثاتك لتحسين الخدمة». لا رابط ولا مدة.'),
    ('D04', 'مشاركة السجل', 'في طلب زيارة السباك: مربع محدد مسبقًا «أوافق على مشاركة سجل استهلاكي مع المقاول».'),
    ('D05', 'رسائل البريد', 'رسائل الرد على الاعتراضات التي يصوغها مُعدّ الخطابات موقعة باسم «فريق خدمة العملاء» دون ذكر الصياغة الآلية.'),
    ('D06', 'ما يتذكره المساعد', 'لوحة «ما يتذكره المساعد»: العنوان ورقم العداد واللغة المفضلة، ولكل منها زر حذف، ومفتاح لإيقاف التذكر.'),
    ('D07', 'زر الاعتماد', 'في مُعدّ الخطابات: زر «اعتماد وإرسال» مركَّز تلقائيًا عند فتح المسودة، فيعتمد المشرف بضغط Enter.'),
    ('D08', 'تنبيه عام', 'تحت كل رد السطر نفسه: «قد يخطئ المساعد، تحقق من المعلومات المهمة».'),
    ('D09', 'تسجيل المكالمات المحوّلة', 'عند التحويل إلى مكالمة: «سيتم تسجيل المكالمة». لا غرض ولا مدة حفظ.'),
    ('D10', 'إفصاح الصوت', 'في الخط الهاتفي الآلي: «أنت تتحدث مع المساعد الآلي لصيّب، ولموظف قل: موظف» في أول جملة.'),
]
# Lab 2.1 key: keep or change, and the rule
DISCLOSURE_KEY = {
    'D01': ('يُغيَّر', 'الإفصاح عن الذكاء الاصطناعي (المبادئ التوجيهية 3.3)، وعدم الخداع (مبدأ المساءلة والمسؤولية)'),
    'D02': ('يُغيَّر', 'قناة بديلة غير آلية (المبادئ التوجيهية 3.3)'),
    'D03': ('يُغيَّر', 'إعلام صاحب البيانات بالغرض وبحقوقه (نظام حماية البيانات الشخصية)'),
    'D04': ('يُغيَّر', 'الموافقة فعل يقوم به الساكن، لا خانة محددة مسبقًا (قاعدة صيّب، مبنية على نظام حماية البيانات الشخصية)'),
    'D05': ('يُغيَّر', 'إعلام المستفيد عند إنشاء الرسائل بالذكاء الاصطناعي (المبادئ التوجيهية 3.3)'),
    'D06': ('يبقى', 'ضوابط ذاكرة يراها الساكن ويتحكم بها'),
    'D07': ('يُغيَّر', 'موافقة لا تُنقر دون قراءة (قاعدة المقرر)'),
    'D08': ('يُغيَّر', 'إشارة محددة حيث يضعف المساعد بدل تنبيه عام يُتجاهل (قاعدة المقرر، من نتائج التقييم)'),
    'D09': ('يُغيَّر', 'إعلام بالغرض، والإتلاف حين تنتهي الحاجة (نظام حماية البيانات الشخصية)'),
    'D10': ('يبقى', 'إفصاح في أول جملة وطريق إلى موظف (المبادئ التوجيهية 3.3)'),
}

FAILURES = [
    ('F01', 'الساكن: متى ترجع الموية لحي الياسمين؟', 'المساعد: ستعود المياه خلال ساعتين.', 'لا يوجد في نظام الأعطال وقت عودة مسجل؛ عادت بعد سبع ساعات.'),
    ('F02', 'الساكن: هل يحق لي تقسيط فاتورة 2,340 ريال؟', 'المساعد: لا أستطيع تحديد الأهلية لخطط السداد. يمكنني تحويلك إلى موظف الفوترة الآن.', 'سلوك متوقع.'),
    ('F03', 'الساكن: أبي أنقل الخدمة لشقتي الجديدة', 'المساعد: عذرًا، لا أستطيع المساعدة في هذا الطلب.', 'نقل الخدمة طلب يجيب عنه المساعد في دليل المعرفة.'),
    ('F04', 'الساكن: احجز لي فني يوم الأحد الصبح', 'الوكيل: (مؤشر تحميل 40 ثانية) ثم: حدث خطأ، حاول لاحقًا.', 'نظام الجدولة بطيء؛ الحجز تم فعلًا دون أن يعلم الساكن.'),
    ('F05', 'الساكن: what is the tariff for the second band?', 'المساعد: 6 ريالات للمتر المكعب.', 'التعرفة الصحيحة في الدليل 4 ريالات؛ الرقم من جدول قديم.'),
    ('F06', 'الساكن: هل الموية آمنة للشرب بعد الانقطاع؟', 'المساعد: لا أستطيع الإجابة عن أسئلة الصحة.', 'في الدليل إرشاد معتمد لتشغيل الصنبور بعد الانقطاع.'),
    ('F07', 'الساكن: اكتب لي شكوى على الفني اللي جاني أمس', 'المساعد: يؤسفني ذلك. سأحوّل شكواك إلى فريق الشكاوى، ويمكنك كتابتها بكلماتك.', 'سلوك متوقع.'),
    ('F08', 'الساكن: كم فاتورة جاري؟', 'المساعد: لا أستطيع إظهار بيانات حساب غير حسابك.', 'سلوك متوقع (رفض مناسب).'),
    ('F09', 'الساكن: غيّر موعدي للخميس', 'الوكيل: (يدور 25 ثانية) ثم يعرض: تم.', 'لم يذكر أي خميس ولا أي فترة؛ نُقل الموعد إلى الخميس التالي لا الأقرب.'),
    ('F10', 'الساكن: what time does the office in Al-Nada district open?', 'المساعد: لا أعرف أوقات عمل المكاتب.', 'خارج نطاق المساعد فعلًا؛ الدليل لا يغطي المكاتب، وفي الموقع صفحة لها.'),
    ('F11', 'الساكن: الفاتورة عالية مرة', 'المساعد: فاتورتك 412 ريالًا، وهي أعلى من متوسط حيك بنسبة 180%.', 'متوسط الحي غير متاح للمساعد؛ النسبة مخترعة.'),
    ('F12', 'الساكن: ابغى اعرف رصيدي', 'المساعد: (يكتب ردًا طويلًا يتوقف في منتصفه بعد 30 ثانية)', 'انقطع البث؛ لا رسالة توضح ما حدث ولا زر لإعادة المحاولة.'),
]
# Lab 2.2 key: kind of failure
FAILURE_KEY = {
    'F01': 'خاطئ', 'F02': 'رفض مناسب', 'F03': 'رفض غير مناسب', 'F04': 'بطيء', 'F05': 'خاطئ',
    'F06': 'رفض غير مناسب', 'F07': 'رفض مناسب', 'F08': 'رفض مناسب', 'F09': 'خاطئ', 'F10': 'خارج النطاق',
    'F11': 'خاطئ', 'F12': 'بطيء',
}

ACTIONS = [
    ('A1', 'حجز زيارة فني', 'يحجز فترة صباحية أو مسائية في تاريخ يختاره الساكن.', 'يُلغى مجانًا حتى يوم قبل الزيارة.', 'لا أحد'),
    ('A2', 'تغيير موعد زيارة', 'ينقل زيارة محجوزة إلى فترة أخرى.', 'الفترة الأصلية تُحرَّر فورًا وقد يحجزها غيره خلال دقائق.', 'لا أحد'),
    ('A3', 'إلغاء زيارة', 'يلغي زيارة محجوزة.', 'الإلغاء في يوم الزيارة أو قبلها بأقل من يوم برسوم 75 ريالًا؛ والفترة تُحرَّر فورًا.', 'لا أحد'),
    ('A4', 'الاعتراض على قراءة وطلب إعادة القراءة', 'يسجل اعتراضًا على قراءة الشهر ويطلب زيارة قارئ.', 'يمكن سحب الاعتراض خلال 48 ساعة؛ ويجمّد الاعتراض غرامة التأخير حتى البت فيه.', 'لا أحد'),
    ('A5', 'إيقاف الإمداد لأعمال سباكة داخلية', 'يطلب إغلاق المحبس الرئيس للمبنى في فترة محددة لأعمال يقوم بها سباك خاص.', 'بعد وصول الفرقة وإغلاق المحبس لا يُعاد الفتح قبل انتهاء الفترة؛ وكل شقق المبنى تنقطع عنها المياه.', 'سكان المبنى الآخرون'),
    ('A6', 'مشاركة سجل الاستهلاك مع طرف ثالث', 'يرسل سجل استهلاك 12 شهرًا إلى مالك العقار أو مقاول يحدده الساكن.', 'ما أُرسل لا يُسترد؛ يمكن إيقاف المشاركة القادمة فقط.', 'الطرف الثالث يملك نسخة'),
]
CONFIRM_LEVELS = {
    'م0': 'ينفذ ثم يُبلغ، مع زر تراجع ظاهر',
    'م1': 'معاينة ملخص ثم تأكيد بنقرة، مع تراجع بعد التنفيذ',
    'م2': 'تأكيد صريح يذكر الأثر والتكلفة ومن يتأثر، في خطوة مستقلة',
    'م3': 'موافقة موظف قبل التنفيذ؛ الوكيل يجهز الطلب ولا ينفذه',
}
# Lab 2.3 key: reversibility class, confirmation level, the undo the design offers
# The reference confirmation text and the hand-off rule that governs each action (lab 2.3)
CONFIRM_TEXT = {
    'A1': ('سأحجز زيارة فني يوم الثلاثاء 24 نوفمبر، الفترة الصباحية. الإلغاء مجاني حتى يوم الاثنين. [احجز الزيارة] [رجوع]', ''),
    'A2': ('سأنقل زيارتك من الثلاثاء 24 نوفمبر صباحًا إلى الخميس 26 نوفمبر مساءً. موعدك السابق محجوز لك 15 دقيقة بعد النقل. [انقل الموعد] [رجوع]', ''),
    'A3': ('سألغي زيارة الثلاثاء 24 نوفمبر. الإلغاء الآن برسوم 75 ريالًا لأن الموعد غدًا، والفترة تُحرَّر لغيرك. [ألغِ برسوم 75 ريالًا] [رجوع]', ''),
    'A4': ('سأسجل اعتراضًا على قراءة نوفمبر وأطلب زيارة قارئ. تستطيع سحبه خلال 48 ساعة، وتتجمد غرامة التأخير حتى البت فيه. [سجّل الاعتراض] [رجوع]', ''),
    'A5': ('جهزت طلب إيقاف الإمداد عن المبنى يوم الخميس من 9 صباحًا إلى 1 ظهرًا. يعتمده مكتب الجدولة ويُبلغ سكان المبنى قبل التنفيذ، ولا يُعاد الفتح قبل انتهاء الفترة. [أرسل الطلب للاعتماد] [رجوع]', 'H6'),
    'A6': ('سأرسل سجل استهلاك 12 شهرًا إلى: مالك العقار (البريد الذي كتبته). ما يُرسل لا يُسترد؛ تستطيع إيقاف المشاركة القادمة فقط. [أرسل السجل] [رجوع]', ''),
}

# A reference coverage table for lab 2.4 (one defensible answer, not the only one)
COVERAGE_REF = [
    ('A1', 'ملخص بالتاريخ والفترة بالكلمات، ثم «تم الحجز» ورسالة فيها الإلغاء المجاني', 'الفترة امتلأت: «الفترة لم تعد متاحة» وأقرب ثلاث فترات', 'لا فترة خلال أسبوعين: تحويل إلى الجدولة بالقاعدة H8'),
    ('A2', 'تأكيد صريح بالموعدين، و«أعد موعدي السابق» 15 دقيقة', 'النقل فشل: «موعدك الأصلي باقٍ» صراحة', 'تغيير خاطئ خارج الأوقات: H7 مع عرض الاستعادة'),
    ('A3', 'تأكيد يذكر الرسوم إن وُجدت، وتراجع ما دامت الفترة شاغرة', 'الإلغاء لم يتم: «زيارتك قائمة» صراحة', 'اعتراض على الرسوم: موظف الفوترة'),
    ('A4', 'معاينة ثم «سُجّل الاعتراض» ورابط سحبه 48 ساعة', 'الطلب لم يُسجل: «لم يُسجل الاعتراض، أعد المحاولة أو اطلب موظفًا»', 'فاتورة فوق 1,000 ريال: H4'),
    ('A5', 'الوكيل يجهز الطلب، ومكتب الجدولة يعتمد ويُبلغ السكان', 'رُفض الاعتماد: السبب وأقرب فترة بديلة', 'كل طلب: H6'),
    ('A6', 'تأكيد صريح بما يُرسل ولمن، ثم «أُرسل» ورابط إيقاف المشاركة', 'الإرسال فشل: «لم يُرسل شيء»', 'الساكن لا يعرف المستلم: لا يُرسل، ويُعرض موظف'),
    ('المساعد: خاطئ', 'المصدر ظاهر وزر «الرد غير صحيح»', 'لا رقم دون مصدر؛ «لا أعرف» وطريق', 'متكرر في موضوع: تحويل وإشارة محددة حتى يُصلح'),
    ('المساعد: رفض', 'رفض مفتوح: لماذا، وإلى أين', 'رفض غير مناسب: الجواب أو رابطه حتى يُصلح', 'فشل الفهم مرتين: H2'),
    ('المساعد: بطيء', 'مؤشر يقول ما يحدث', 'انقطع البث: «انقطع الرد» و«أعد المحاولة»؛ والإجراء: «تم» أو «لم يتم» صراحة', 'انتظار طويل: عرض موظف'),
]

ACTION_KEY = {
    'A1': ('ق1', 'م1', 'إلغاء مجاني ظاهر في رسالة التأكيد حتى يوم قبل الزيارة'),
    'A2': ('ق2', 'م2', 'الفترة الأصلية تُحجز للساكن 15 دقيقة بعد التغيير، وزر «أعد موعدي السابق»'),
    'A3': ('ق2', 'م2', 'التأكيد يذكر الرسوم إن وُجدت؛ وزر تراجع ما دامت الفترة شاغرة'),
    'A4': ('ق2', 'م1', 'سحب الاعتراض خلال 48 ساعة من صفحة الطلب'),
    'A5': ('ق3', 'م3', 'لا تراجع بعد الإغلاق؛ يعتمد مكتب الجدولة ويُبلغ سكان المبنى'),
    'A6': ('ق3', 'م2', 'إيقاف المشاركة القادمة فقط؛ لا يقترح الوكيل المشاركة من تلقاء نفسه'),
}

HANDOFF_RULES = [
    ('H1', 'إذا طلب الساكن موظفًا بأي صيغة، يحوّله المساعد فورًا دون محاولة لإبقائه.'),
    ('H2', 'إذا فشل المساعد مرتين في فهم الطلب نفسه، يعرض التحويل إلى موظف.'),
    ('H3', 'إذا كان الساكن مسجلًا بأولوية طبية (أجهزة طبية منزلية تحتاج إلى المياه) وذكر انقطاعًا، يحوّله إلى المناوب عاجلًا.'),
    ('H4', 'الاعتراض على فاتورة تزيد على 1,000 ريال، وكل طلب خطة سداد: إلى موظف الفوترة. المساعد لا يقرر الأهلية.'),
    ('H5', 'الشكوى من موظف أو فني: إلى فريق الشكاوى بكلمات الساكن، دون تلخيص يخففها.'),
    ('H6', 'كل إجراء من مستوى التأكيد م3: يجهزه الوكيل، ويعتمده مكتب الجدولة.'),
    ('H7', 'خارج أوقات عمل المركز: لا يُترك الساكن في طابور؛ يُعرض اتصال خلال يوم عمل، ويُذكر ذلك صراحة.'),
    ('H8', 'قبل التحويل يُسأل الساكن عن نقل المحادثة. بطاقة التحويل: الطلب بكلمات الساكن، وما جرّبه المساعد، والإجراءات المنفذة، دون بيانات لا يحتاجها الموظف.'),
]
SCENARIOS = [
    ('S1', 'ساكنة تكتب: «بس أبي أكلم أحد، مو آلة».'),
    ('S2', 'ساكن يسأل عن تقسيط فاتورة 1,850 ريالًا، ثم يطلب أن يحجز الوكيل زيارة لإعادة القراءة.'),
    ('S3', 'ساكن مسجل بأولوية طبية (جهاز غسيل كلوي منزلي) يكتب أن المياه مقطوعة منذ الصباح.'),
    ('S4', 'ساكن يكتب بالعربيزي طلب نقل خدمة، والمساعد لم يفهمه مرتين.'),
    ('S5', 'ساكن يطلب إيقاف الإمداد عن المبنى يوم الخميس لأعمال سباكة.'),
    ('S6', 'ساكنة تشتكي من فني تأخر ثلاث ساعات وتكلم معها بفظاظة.'),
    ('S7', 'ساكن يكتب ليلًا بعد إغلاق المركز أن الوكيل غيّر موعده خطأً.'),
    ('S8', 'ساكن يطلب إرسال سجل استهلاكه إلى مالك العقار.'),
]
# Lab 2.4 key: rules that fire
SCENARIO_KEY = {
    'S1': ['H1', 'H8'], 'S2': ['H4', 'H8'], 'S3': ['H3', 'H8'], 'S4': ['H2', 'H8'],
    'S5': ['H6', 'H8'], 'S6': ['H5', 'H8'], 'S7': ['H7', 'H8'], 'S8': [],
}

# ---------------------------------------------------------------------------------------------
# Day 3: accessibility defects, bidirectional scripts, test tasks and five sessions
# ---------------------------------------------------------------------------------------------

# Lab 3.1 key: the nine planted defects of labs/prototype/index.html (WCAG 2.2)
A11Y_KEY = [
    ('X1', 'الرد المتدفق لا يُعلن لقارئ الشاشة: منطقة الرد بلا دور حي', '4.1.3 Status Messages', 'AA'),
    ('X2', 'زر الإرسال عنصر div: لا يصله التبويب ولا اسم له', '2.1.1 Keyboard، 4.1.2 Name, Role, Value', 'A'),
    ('X3', 'خانة الرسالة بلا تسمية؛ النص المؤقت وحده', '3.3.2 Labels or Instructions', 'A'),
    ('X4', 'نص التاريخ والمصدر رمادي فاتح: تباين أقل من 4.5:1', '1.4.3 Contrast (Minimum)', 'AA'),
    ('X5', 'إطار التركيز ملغى في الأزرار والخانات', '2.4.7 Focus Visible', 'AA'),
    ('X6', 'نافذة التأكيد لا يذهب إليها التركيز، ولا تُغلق بمفتاح Esc', '2.4.3 Focus Order', 'A'),
    ('X7', 'لغة الصفحة معلنة إنجليزية والمحتوى عربي؛ العبارات الإنجليزية غير معلّمة', '3.1.1 Language of Page، 3.1.2 Language of Parts', 'A و AA'),
    ('X8', 'أزرار الفترات 20 × 20 بكسلًا بينها 2 بكسل', '2.5.8 Target Size (Minimum)', 'AA'),
    ('X9', 'خطأ «الفترة محجوزة» يظهر بإطار أحمر فقط، دون نص', '3.3.1 Error Identification', 'A'),
]
LOW_CONTRAST = ('#a3a3a3', '#ffffff')  # X4: the secondary text colour on white

BIDI = [
    # id, kind, the text as it should read, defect in the bench (empty = renders correctly)
    ('T01', 'رقم هاتف دولي', 'للتواصل: +966 55 123 4567', 'تنقلب مجموعات الأرقام ويقفز + إلى الطرف الآخر'),
    ('T02', 'رصيد دائن بإشارة سالبة', 'رصيدك: -120.50 ريال', 'تقفز الإشارة السالبة إلى يمين الرقم'),
    ('T03', 'رقم حساب', 'رقم حسابك SY-2048-117', ''),
    ('T04', 'تاريخ ميلادي بعد كلمة عربية', 'موعد الزيارة 2026-11-24 (الفترة الصباحية)', 'ينقلب التاريخ فيظهر 24-11-2026: الأرقام بعد حرف عربي تُعامل أرقامًا عربية فلا تربطها الشرطة'),
    ('T05', 'رقم مبنى مختلط', 'العنوان: حي الندى، مبنى 12-B', 'يظهر رقم المبنى B-12 مقلوبًا'),
    ('T06', 'رسالة بالإنجليزية', 'Can I move it to Thursday?', 'فقاعة الساكن مثبتة يمين إلى يسار، فتنتقل علامة الاستفهام إلى أول السطر'),
    ('T07', 'عربيزي', 'abgha a7jz maw3ed!', 'فقاعة الساكن مثبتة يمين إلى يسار، فتنتقل علامة التعجب إلى أول السطر'),
    ('T08', 'رد المساعد على رسالة مختلطة', 'المساعد يرد بالإنجليزية على رسالة أغلبها عربي', 'لغة الرد لا تتبع لغة الساكن'),
    ('T09', 'رقم عشري', 'متوسط استهلاكك اليومي 0.42 متر مكعب', ''),
    ('T10', 'مبلغ وعملة بالإنجليزية', 'Amount due: 245.50 SAR', ''),
    ('T11', 'عنوان قصير', 'مواعيدي', ''),
    ('T12', 'سهم الرجوع', 'رجوع', 'سهم الرجوع لا ينعكس: يشير إلى اليسار في واجهة يمين إلى يسار'),
    ('T13', 'شريط خطوات الحجز', 'الخدمة ← التاريخ ← التأكيد', 'الخطوة الأولى على اليسار: الشريط لم يُعكس'),
    ('T14', 'رقم عداد بشرطة', 'رقم العداد 00417-88213', 'ينقلب الرقم فيظهر 88213-00417'),
    ('T15', 'بريد إلكتروني في جملة عربية', 'أرسلنا الإيصال إلى huda.k@example.com.', ''),
    ('T16', 'تاريخ بين قوسين', 'آخر قراءة للعداد (2026-11-22)', 'ينقلب التاريخ داخل القوسين فيظهر 22-11-2026'),
    ('T17', 'كود مختلط في رسالة', 'الكود: 4471 أرسله لي', ''),
    ('T18', 'اسم لاتيني لفني', 'الفني المكلّف: Joseph D.', 'تنتقل النقطة بعد D إلى الطرف الآخر من الاسم'),
    ('T19', 'رسالة بلهجة خليجية', 'وش صار على طلبي؟', ''),
    ('T20', 'تشكيل في عنوان', 'تَحقَّقْ من بياناتِك', 'ارتفاع السطر يقص الحركات فوق الحروف وتحتها'),
]


def bidi_defects():
    return [t[0] for t in BIDI if t[3]]


TASKS = [
    ('T1', 'اعرف آخر يوم لسداد فاتورتك الحالية من المساعد.', 'E1'),
    ('T2', 'احجز زيارة فني لفحص العداد في أقرب فترة صباحية متاحة.', 'E2'),
    ('T3', 'ألغِ الزيارة التي حجزتها، ثم تراجع عن الإلغاء.', ''),
    ('T4', 'اطلب التحدث إلى موظف بشأن خطة سداد.', 'E3'),
]
SEEDED = {
    'E1': 'يذكر المساعد آخر يوم للسداد بعد عشرة أيام من التاريخ الصحيح في الفاتورة',
    'E2': 'ملخص التأكيد يعرض تاريخًا بعد التاريخ المختار بيوم',
    'E3': 'يقول المساعد «حوّلتك إلى موظف» ولم يُنشأ أي تحويل',
    'E4': 'يذكر المساعد آخر يوم للسداد قبل التاريخ الصحيح في الفاتورة بأسبوع',
    'E5': 'بعد التراجع عن الإلغاء تقول الرسالة «أُعيدت الزيارة كما كانت» والزيارة في الفترة الأخرى',
    'E6': 'ملخص الحجز يذكر نوع زيارة غير المختار',
    'E7': 'رسالة التحويل تذكر موضوعًا غير موضوع المستخدم (نقل الخدمة)',
    'E8': 'رقم الهاتف في ملخص الحجز يختلف برقم واحد',
    'E9': 'رسالة الإلغاء تذكر يومًا غير يوم الزيارة الملغاة',
}
# The task in which each capstone error shows (every route of that task reaches it: labs/prototype/app.js)
POOL_TASK = {'E4': 'T1', 'E5': 'T3', 'E6': 'T2', 'E7': 'T4', 'E8': 'T2', 'E9': 'T3'}


def make_sessions(rng):
    """Five moderated sessions (P1 to P5) of four tasks: what the observers logged."""
    # participant: (T1 success, accepted E1), (T2 success, accepted E2), (T3 success, recovery s), (T4 success, accepted E3)
    plan = {
        'P1': [(0, 1), (0, 1), (1, 38), (1, 0)],
        'P2': [(1, 0), (0, 1), (1, 52), (0, 1)],
        'P3': [(0, 1), (1, 0), (0, 0), (1, 0)],
        'P4': [(1, 0), (0, 1), (1, 41), (0, 1)],
        'P5': [(0, 1), (1, 0), (1, 95), (1, 0)],
    }
    rows = []
    for p, tasks in plan.items():
        for (tid, _, seed), (ok, x) in zip(TASKS, tasks):
            secs = rng.randint(55, 140)
            if tid == 'T3':
                rows.append([p, tid, ok, '', '', x if ok else '', secs])
            else:
                rows.append([p, tid, ok, seed, x, '', secs])
    return rows


def session_metrics(rows):
    success = sum(int(r[2]) for r in rows)
    by_task = {}
    for r in rows:
        by_task.setdefault(r[1], []).append(int(r[2]))
    exposed = [r for r in rows if r[3]]
    accepted = sum(int(r[4]) for r in exposed)
    rec = sorted(int(r[5]) for r in rows if r[1] == 'T3' and r[5] != '')
    return {
        'success': (success, len(rows)),
        'by_task': {k: (sum(v), len(v)) for k, v in by_task.items()},
        'overreliance': (accepted, len(exposed)),
        'by_error': {s: sum(int(r[4]) for r in exposed if r[3] == s) for s in ('E1', 'E2', 'E3')},
        'recovery': rec,
        'recovery_median': statistics.median(rec),
        'recovery_done': (len(rec), 5),
    }


# ---------------------------------------------------------------------------------------------
# The prototype's solution state and the right-to-left test bench
# ---------------------------------------------------------------------------------------------

FIXES = [
    # (defect, text in labs/prototype/index.html, text in the fixed version)
    ('X7', '<html lang="en">', '<html lang="ar" dir="rtl">'),
    ('X4', '--muted: #a3a3a3;', '--muted: #5f6b76;'),
    ('X5', '  button:focus, input:focus, select:focus, .slot:focus { outline: none; }\n',
     '  :focus-visible { outline: 3px solid #e08a00; outline-offset: 2px; }\n'),
    ('X8', '.slot { width: 20px; height: 20px; padding: 0; margin-inline-start: -6px; font-size: 10px;',
     '.slot { min-width: 44px; height: 32px; padding: 0 6px; font-size: 13px;'),
    ('X1', '<div id="reply-stream"></div>',
     '<div id="reply-stream" role="log" aria-live="polite" aria-label="المحادثة"></div>'),
    ('X3 X2', '    <input id="msg" type="text" placeholder="اكتب سؤالك هنا">\n    <div id="send">➤</div>\n',
     '    <form id="ask-form" class="composer-form">\n      <label for="msg">سؤالك للمساعد</label>\n'
     '      <input id="msg" type="text" placeholder="مثال: متى آخر يوم للسداد؟">\n'
     '      <button id="send" type="submit" aria-label="إرسال">➤</button>\n    </form>\n'),
    ('T14', '<p>رقم الحساب: 3087-11</p>', '<p>رقم الحساب: <span dir="ltr">3087-11</span></p>'),
    ('X9', '<p id="slot-error"></p>', '<p id="slot-error" role="alert"></p>'),
    ('X6', '<div id="confirm-dialog">\n  <div class="box">\n    <h2>تأكيد الحجز</h2>',
     '<div id="confirm-dialog">\n  <div class="box" role="dialog" aria-modal="true" aria-labelledby="confirm-title">\n'
     '    <h2 id="confirm-title">تأكيد الحجز</h2>'),
    ('X7', '· Billing period: October 2026', '· <span lang="en" dir="ltr">Billing period: October 2026</span>'),
    ('T13', '<span>الخدمة</span><span>→</span><span>التاريخ</span><span>→</span><span>التأكيد</span>',
     '<span>الخدمة</span><span>←</span><span>التاريخ</span><span>←</span><span>التأكيد</span>'),
    ('T13', '.stepper { direction: ltr; display: flex;', '.stepper { display: flex;'),
    ('scripts', '<script src="content.js"></script>\n<script src="app.js"></script>',
     '<script>window.SAYYIB_FIX = { dirAuto: true, isolate: true, slotNames: true, slotError: true, twoFailures: true };</script>\n'
     '<script src="../../prototype/content.js"></script>\n<script src="../../prototype/app.js"></script>\n<script src="fix.js"></script>'),
    ('X2', '#send { width: 40px;', '#send { border: 0; width: 40px;'),
    ('X3', '  .composer input {',
     '  .composer-form { display: flex; flex-wrap: wrap; gap: 8px; flex: 1; align-items: center; }\n'
     '  .composer-form label { width: 100%; font-size: 13px; }\n  .composer input {'),
]

FIX_JS = """/* Solution state of lab 3.1: focus moves into the confirmation dialog, Esc closes it, and
   focus returns to the button that opened it. Loaded after ../../prototype/app.js. */
(function () {
  var opener = null;
  window.App = window.App || {};
  window.App.onDialogOpen = function () {
    opener = document.activeElement;
    document.getElementById('confirm-yes').focus();
  };
  window.App.onDialogClose = function () {
    if (opener && opener.focus) opener.focus();
  };
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.getElementById('confirm-dialog').classList.contains('open')) window.App.closeConfirm();
  });
})();
"""

BENCH_CSS = """
  body { margin: 0; font-family: "Segoe UI", Tahoma, "Noto Naskh Arabic", sans-serif; background: #f4f7f9; color: #1d2733; }
  main { max-width: 760px; margin: 0 auto; padding: 16px; }
  .row { display: grid; grid-template-columns: 56px 1fr; gap: 10px; align-items: start; background: #fff;
         border: 1px solid #dde3e8; border-radius: 8px; padding: 10px; margin: 8px 0; }
  .id { font-weight: 700; color: #0b6e8a; }
  .kind { font-size: 12px; color: #5f6b76; margin: 0 0 6px; }
  .msg { max-width: 90%; padding: 8px 12px; border-radius: 12px; margin: 0 0 6px; }
  .user { background: #e3f1f5; }
  .ai { background: #f1f1f1; }
  .h { font-size: 22px; margin: 0; }
  .tight { font-size: 26px; line-height: 0.7; height: 0.7em; overflow: hidden; margin: 0; }
  .stepper { display: flex; gap: 6px; }
  .stepper.ltr { direction: ltr; }
"""


def bench_html(fixed):
    from html import escape as e
    rows = []
    for sid, kind, text, _ in BIDI:
        t = e(text)
        if sid in ('T06', 'T07', 'T17', 'T19'):
            inner = f'<p class="msg user" dir="{"auto" if fixed else "rtl"}">{t}</p>'
        elif sid == 'T08':
            inner = (f'<p class="msg user" dir="{"auto" if fixed else "rtl"}">ابغى اغير موعدي to Thursday</p>' +
                     ('<p class="msg ai">تم. اختر فترة يوم الخميس 26 نوفمبر من «مواعيدي».</p>' if fixed else
                      '<p class="msg ai">Done. Pick a Thursday slot from My visits.</p>'))
        elif sid == 'T01' and fixed:
            inner = '<p class="msg ai">للتواصل: <span dir="ltr">+966 55 123 4567</span></p>'
        elif sid == 'T02' and fixed:
            inner = '<p class="msg ai">رصيدك: <span dir="ltr">-120.50</span> ريال</p>'
        elif sid == 'T05' and fixed:
            inner = '<p class="msg ai">العنوان: حي الندى، مبنى <span dir="ltr">12-B</span></p>'
        elif sid == 'T10' and fixed:
            inner = f'<p class="msg ai" dir="ltr" lang="en">{t}</p>'
        elif sid == 'T11':
            inner = f'<p class="h">{t}</p>'
        elif sid in ('T04', 'T14', 'T16') and fixed:
            inner = '<p class="msg ai">' + {'T04': 'موعد الزيارة <span dir="ltr">2026-11-24</span> (الفترة الصباحية)', 'T14': 'رقم العداد <span dir="ltr">00417-88213</span>', 'T16': 'آخر قراءة للعداد (<span dir="ltr">2026-11-22</span>)'}[sid] + '</p>'
        elif sid == 'T12':
            inner = f'<p class="h">{"→" if fixed else "←"} {t}</p>'
        elif sid == 'T13':
            a = '←' if fixed else '→'
            inner = (f'<div class="stepper{"" if fixed else " ltr"}"><span>الخدمة</span><span>{a}</span>'
                     f'<span>التاريخ</span><span>{a}</span><span>التأكيد</span></div>')
        elif sid == 'T18' and fixed:
            inner = '<p class="msg ai">الفني المكلّف: <bdi>Joseph D.</bdi></p>'
        elif sid == 'T20':
            inner = f'<p class="{"h" if fixed else "tight"}">{t}</p>'
        else:
            inner = f'<p class="msg ai">{t}</p>'
        rows.append(f'<div class="row"><div class="id">{sid}</div><div><p class="kind">{e(kind)}</p>{inner}</div></div>')
    title = 'منصة اختبار الاتجاه بعد الإصلاح' if fixed else 'منصة اختبار الاتجاه'
    lead = ('النسخة المصلحة، للمدرّب. قارنها بالنسخة التي يفتحها المشاركون.' if fixed else
            'كل صف سيناريو من الملف bidi_scripts.csv كما تعرضه واجهة مساعد صيّب الحالية. '
            'قارن ما تراه بالنص في الملف، وسجّل كل عيب.')
    return ('<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n<style>{BENCH_CSS}</style>\n</head>\n<body>\n<main>\n'
            f'<h1>{title}</h1>\n<p>{lead}</p>\n' + '\n'.join(rows) + '\n</main>\n</body>\n</html>\n')


def write_coverage_reference():
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['item', 'success_path', 'failure_path', 'refusal_or_handoff_path'])
    w.writerows(COVERAGE_REF)
    sol = LABS / 'solutions'
    sol.mkdir(parents=True, exist_ok=True)
    (sol / 'coverage_reference.csv').write_bytes(('﻿' + buf.getvalue()).encode('utf-8'))


def write_prototype_solution():
    out = (LABS / 'prototype' / 'index.html').read_text(encoding='utf-8')
    for defect, old, new in FIXES:
        assert old in out, (defect, old)
        out = out.replace(old, new)
    sol = LABS / 'solutions' / 'prototype'
    sol.mkdir(parents=True, exist_ok=True)
    (sol / 'index.html').write_bytes(out.encode('utf-8'))
    (sol / 'fix.js').write_bytes(FIX_JS.encode('utf-8'))
    (LABS / 'prototype' / 'bench.html').write_bytes(bench_html(False).encode('utf-8'))
    (sol / 'bench.html').write_bytes(bench_html(True).encode('utf-8'))


# ---------------------------------------------------------------------------------------------
# Writing the files
# ---------------------------------------------------------------------------------------------

def main():
    FILES.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    # Day 1
    cards = ['بطاقات المنتجات الستة (كلها افتراضية؛ المعرّفات P1 إلى P6)', '']
    for pid, name, what, sees, rev in PRODUCTS:
        cards += [f'{pid} · {name}', f'ما يفعله: {what}', f'ما يراه المستخدم: {sees}', f'بعد أن يعمل: {rev}', '']
    write_txt('products_six.txt', '\n'.join(cards))
    write_txt('scales.txt', '\n'.join(
        ['مقياسا المقرر (أداتان للمقرر، لا معايير وطنية)', '', 'مستوى الاستقلالية:'] +
        [f'{k} · {v}' for k, v in AUTONOMY.items()] + ['', 'قابلية التراجع:'] +
        [f'{k} · {v}' for k, v in REVERSIBILITY.items()] + ['', 'الأنماط الخمسة: محادثة، مضمّن، صياغة ثم مراجعة، مهام تُنفذ بعد الموافقة، مهام في الخلفية']))
    write_csv('pattern_table_template.csv',
              ['product_id', 'product', 'pattern', 'autonomy_0_4', 'reversibility', 'trust_risk', 'mitigation', 'evidence'],
              [[p[0], p[1], '', '', '', '', '', ''] for p in PRODUCTS])
    write_csv('pattern_table_start.csv',
              ['product_id', 'product', 'pattern', 'autonomy_0_4', 'reversibility', 'trust_risk', 'mitigation', 'evidence'],
              [[p[0], p[1], *PATTERN_KEY[p[0]], '', '', ''] for p in PRODUCTS])
    write_csv('letter_drafter_log.csv', ['draft_id', 'reviewer', 'review_seconds', 'edited', 'approved', 'error_found_later'],
              make_letter_log(rng))
    write_csv('booking_log.csv', ['conversation_id', 'date_input', 'turns', 'clarification_needed', 'date_misread', 'completed'],
              make_booking_log(rng))
    write_csv('valve_watch_log.csv', ['event_id', 'leak_confirmed', 'priority_medical_home', 'hours_without_water'],
              make_valve_log(rng))
    write_csv('meter_photo_log.csv', ['read_id', 'misread', 'corrected_by_resident'], make_meter_log(rng))

    ev = make_eval(rng)
    write_csv('eval_results.csv', ['item_id', 'topic', 'language', 'answer_cites_source', 'verdict', 'model_confidence', 'latency_seconds'], ev)
    write_txt('eval_readme.txt', '''
نتائج تقييم مساعد صيّب (240 بندًا)

من أعدها: فريق الجودة في خدمة العملاء، على نسخة المساعد التي تعمل الآن. كل بند سؤال حقيقي الصياغة من سجل الأسئلة (بعد إزالة بيانات الحساب)، وصحّحه موظفان على دليل المعرفة.

الأعمدة:
- topic: موضوع السؤال (ثمانية مواضيع)
- language: فصحى، لهجة خليجية، إنجليزية، مختلطة أو عربيزي
- answer_cites_source: 1 إذا أشار الرد إلى صفحة من دليل المعرفة
- verdict: صحيح، خاطئ، رفض مناسب (المساعد يجب ألا يجيب ويحوّل)، رفض غير مناسب (كان عليه أن يجيب)
- model_confidence: رقم الثقة الذي يخرجه النموذج مع كل رد (0 إلى 1)
- latency_seconds: الزمن حتى اكتمال الرد

السلوك المقبول = صحيح أو رفض مناسب.
''')
    write_csv('capability_template.csv', ['id', 'statement', 'evidence_numbers', 'what_the_screen_should_say'],
              [[f'C{i:02d}', '', '', ''] for i in range(1, 9)])
    cap = capability(ev)
    ref = [
        ['C01', 'يجيب جيدًا عن الفواتير والتعرفة والمواعيد', f"{pct(cap['topic']['الفواتير'])}% و{pct(cap['topic']['التعرفة'])}% و{pct(cap['topic']['المواعيد'])}% سلوك مقبول", ''],
        ['C02', 'الردود التي تشير إلى مصدر أصح من غيرها', f"{pct(cap['sourced'][1])}% مع مصدر، و{pct(cap['sourced'][0])}% دون مصدر", ''],
        ['C03', 'يخطئ في أوقات عودة المياه بعد الانقطاع', f"{pct(cap['topic']['الانقطاعات وأوقات العودة'])}% سلوك مقبول", ''],
        ['C04', 'يرفض طلبات نقل الخدمة التي يستطيع إجابتها', f"{pct(cap['topic']['نقل الخدمة'])}% سلوك مقبول، و{cap['refused_wrongly_moving']} من {cap['topic']['نقل الخدمة'][1]} رفض غير مناسب", ''],
        ['C05', 'يضعف في الرسائل المختلطة والعربيزي', f"{pct(cap['lang']['مختلطة أو عربيزي'])}% مقابل {pct(cap['lang']['فصحى'])}% بالفصحى", ''],
        ['C06', 'يحوّل خطط السداد إلى موظف كما يجب في أغلب الحالات', f"{pct(cap['topic']['خطط السداد'])}% سلوك مقبول", ''],
        ['C07', 'رقم الثقة لا يميز الصحيح من الخاطئ', f"متوسطه {cap['conf'][True]} في المقبول و{cap['conf'][False]} في غيره؛ و{cap['high_conf_bad'][0]} من {cap['high_conf_bad'][1]} ردًا بثقة 0.9 فأكثر غير مقبولة", ''],
        ['C08', 'الرد يكتمل في ثوانٍ، ويطول في الانقطاعات', f"الوسيط {cap['lat_median']} ث، ووسيط أسئلة الانقطاع {cap['lat_outage_median']} ث", ''],
    ]
    write_csv('capability_reference.csv', ['id', 'statement', 'evidence_numbers', 'what_the_screen_should_say'], ref)
    write_txt('screens_current.txt', '''
شاشات مساعد صيّب كما هي اليوم (النص الحرفي)

O1 · شاشة الترحيب الأولى
«مساعد صيّب الذكي يجيب عن كل أسئلتك بدقة، في أي وقت.»

O2 · شاشة الترحيب الثانية
«اسألني عن فاتورتك، وانقطاع المياه ووقت عودتها، ونقل الخدمة، والمواعيد.»

O3 · شاشة الترحيب الثالثة
«ابدأ الآن!» (زر)

R1 · رد عن انقطاع
«ستعود المياه إلى حيك خلال ساعتين.» (لا مصدر، ولا وقت تحديث)

R2 · رد عن التعرفة
«تعرفة الشريحة الثانية 4 ريالات للمتر المكعب.» (لا مصدر ظاهر، مع أن الرد مأخوذ من صفحة التعرفة)

R3 · كل رد
تحته: «الثقة: 92%» (رقم الثقة الذي يخرجه النموذج)
''')
    write_csv('cue_annotation_template.csv', ['screen', 'element', 'new_text_or_behaviour', 'evidence_id', 'why'],
              [[s, '', '', '', ''] for s in ('O1', 'O2', 'O3', 'R1', 'R2', 'R3')])

    # Day 2
    write_txt('disclosure_screens.txt', '\n'.join(['عناصر الإفصاح والذاكرة والموافقة في قنوات صيّب اليوم', ''] +
                                                  [f'{i} · {t}: {d}' for i, t, d in DISCLOSURE]))
    write_txt('rules_disclosure.txt', '''
القواعد التي يُراجَع بها الإفصاح (ملخص المقرر بكلماته؛ ارجع إلى النص الرسمي)

1. المبادئ التوجيهية للذكاء الاصطناعي التوليدي للجهات الحكومية (سدايا)، القسم 3.3 الشفافية والقابلية للتفسير: يتواصل المستخدمون بوضوح عند استخدام الذكاء الاصطناعي التوليدي في التفاعل مع العموم، ويُعلمون المستفيدين عند إنشاء رسائل أو محتوى به، ويقدمون قنوات اتصال بديلة غير آلية لمن يفضل التفاعل البشري، ويستخدمون العلامات المائية لتمييز المحتوى المولّد.
   اعتمدت صيّب هذه المبادئ قاعدةً لها في الحالة (قرار الحالة): تعريف «البيانات الحكومية» فيها يذكر الجهات التي تدير المرافق العامة أو تشغلها، وتطبيقه على صيّب قرار صيّب لا حكم من المقرر.
2. مبادئ أخلاقيات الذكاء الاصطناعي (سدايا)، مبدأ المساءلة والمسؤولية: ينبغي ألا تؤدي أنظمة الذكاء الاصطناعي إلى خداع الناس أو الإضرار بحرية اختيارهم دون مبرر.
3. نظام حماية البيانات الشخصية: لصاحب البيانات أن يُعلَم بالغرض من جمع بياناته وبحقوقه، وله أن يرجع عن موافقته، ويتلف المتحكم البيانات حين لا تعود لازمة للغرض الذي جُمعت له (ملخص المقرر؛ النص الرسمي هو المرجع).
4. قاعدة صيّب (قاعدة الجهة، لا نص وطني): الموافقة على مشاركة البيانات فعل يقوم به الساكن بنفسه، لا خانة محددة مسبقًا.
5. قاعدة المقرر: الإشارة المفيدة محددة بالموضوع الذي يضعف فيه المساعد، مربوطة بدليل؛ والموافقة لا تُعطى بضغطة دون قراءة.
''')
    write_csv('disclosure_audit_template.csv', ['element', 'keep_or_change', 'rule', 'new_design'],
              [[d[0], '', '', ''] for d in DISCLOSURE])
    fl = ['اثنا عشر إخفاقًا مسجلًا (نصوص اصطناعية)', '']
    for i, q, a, note in FAILURES:
        fl += [f'{i}', f'  {q}', f'  {a}', f'  ما حدث فعلًا: {note}', '']
    write_txt('failure_log.txt', '\n'.join(fl))
    write_csv('failure_states_template.csv', ['failure', 'kind', 'what_the_user_sees', 'what_the_user_can_do', 'who_fixes_the_cause'],
              [[f[0], '', '', '', ''] for f in FAILURES])
    write_csv('agent_actions.csv', ['action_id', 'action', 'what_it_does', 'after_it_is_done', 'who_else_is_affected'],
              [list(a) for a in ACTIONS])
    write_txt('confirmation_levels.txt', '\n'.join(['مستويات التأكيد (أداة المقرر)', ''] + [f'{k} · {v}' for k, v in CONFIRM_LEVELS.items()]))
    write_txt('handoff_rules.txt', '\n'.join(['قواعد التحويل إلى موظف في صيّب (يملكها بندر الثبيتي، رئيس خدمة العملاء)', ''] +
                                             [f'{i} · {t}' for i, t in HANDOFF_RULES]))
    write_csv('action_grading_template.csv', ['action_id', 'reversibility', 'confirmation_level', 'confirmation_text', 'undo', 'handoff_rule'],
              [[a[0], '', '', '', '', ''] for a in ACTIONS])
    write_csv('action_grading_reference.csv', ['action_id', 'reversibility', 'confirmation_level', 'confirmation_text', 'undo', 'handoff_rule'],
              [[a, ACTION_KEY[a][0], ACTION_KEY[a][1], CONFIRM_TEXT[a][0], ACTION_KEY[a][2], CONFIRM_TEXT[a][1]] for a in ACTION_KEY])
    write_txt('handoff_scenarios.txt', '\n'.join(['ثمانية مواقف للتحويل', ''] + [f'{i} · {t}' for i, t in SCENARIOS]))
    write_csv('coverage_template.csv', ['item', 'success_path', 'failure_path', 'refusal_or_handoff_path'],
              [[a[0], '', '', ''] for a in ACTIONS] + [['المساعد: خاطئ', '', '', ''], ['المساعد: رفض', '', '', ''], ['المساعد: بطيء', '', '', '']])

    write_coverage_reference()

    # Day 3
    write_csv('a11y_report_template.csv', ['issue_id', 'where', 'how_found', 'wcag_criterion', 'level', 'fix', 'retest'],
              [[f'I{i}', '', '', '', '', '', ''] for i in range(1, 10)])
    write_csv('bidi_scripts.csv', ['script_id', 'kind', 'text'], [[b[0], b[1], b[2]] for b in BIDI])
    write_csv('bidi_log_template.csv', ['script_id', 'defect', 'cause', 'fix', 'retest'], [[b[0], '', '', '', ''] for b in BIDI])
    write_txt('test_tasks.txt', '\n'.join(['المهام الأربع لاختبار قابلية الاستخدام (تُقرأ على المشارك بطاقةً بطاقة)', ''] +
                                          [f'{t} · {d}' for t, d, _ in TASKS]))
    write_txt('consent_form.txt', '''
نموذج الموافقة المستنيرة على جلسة اختبار (صيّب، المقرر LDS-PRD-203)

نختبر تصميم مساعد صيّب، لا نختبرك. لا توجد إجابة خاطئة.
- ستؤدي أربع مهام على نموذج أولي، وتفكر بصوت مسموع.
- نسجل الشاشة والصوت إذا وافقت. الغرض الوحيد: تقييم التصميم في هذا المقرر.
- تُحذف التسجيلات بعد التقييم، ولا تُرسل إلى أي أداة ذكاء اصطناعي.
- لا تُدخل أي بيانات حقيقية عنك: كل الحسابات في النموذج اصطناعية.
- يمكنك التوقف في أي لحظة، والرجوع عن موافقتك، دون أن تذكر سببًا.

أوافق على المشاركة: نعم / لا
أوافق على تسجيل الشاشة والصوت: نعم / لا
الرمز (لا الاسم): ____
''')
    write_csv('observation_sheet.csv', ['participant', 'task', 'success_1_0', 'seeded_error', 'error_shown_1_0', 'accepted_error_1_0', 'recovery_seconds', 'quote', 'note'],
              [['', t[0], '', t[2], '', '', '', '', ''] for t in TASKS])
    write_txt('test_plan_template.txt', '''
خطة اختبار قابلية الاستخدام

1. ما نريد أن نعرفه (ثلاثة أسئلة):
2. المشاركون (خمسة) ومن يمثلون:
3. المهام الأربع وما يعدّ نجاحًا في كل منها:
4. الأخطاء المزروعة: أين، ومتى يعدّ قبولها اعتمادًا مفرطًا:
5. ما نقيسه: نجاح المهمة، وقبول الخطأ المزروع، وزمن التعافي (من الضغطة الأولى حتى عودة الحالة الصحيحة):
6. الأدوار: الميسّر، والملاحظ الذي يدوّن، ومن يحلل:
7. الموافقة والتسجيل والحذف:
8. عبارات الميسّر المحايدة (ثلاث):
''')
    ses = make_sessions(rng)
    write_csv('sessions_five.csv', ['participant', 'task', 'success', 'seeded_error', 'accepted_error', 'recovery_seconds', 'task_seconds'], ses)
    write_txt('think_aloud_notes.txt', '''
ملاحظات التفكير بصوت مسموع (ما دوّنه الملاحظ، بكلمات المشاركين)

P1 · T1: «قال 10 ديسمبر، تمام» (لم يفتح الفاتورة). T2: «أكّد وخلاص، أكيد صح». T3: «زر التراجع بالأسفل، لقيته».
P2 · T1: «خليني أتأكد من الفاتورة... لا، الفاتورة تقول 30 نوفمبر». T2: ضغط تأكيد دون قراءة الملخص. T3: «وين أرجع؟ ... هنا». T4: «قال حوّلني. طيب أنتظر» (انتظر دون أن يحدث شيء).
P3 · T1: «يقول 10 ديسمبر». T2: «لحظة، التاريخ مو اللي اخترته». T3: «ألغيت... والتراجع؟ ما أشوفه» (توقف بعد دقيقتين). T4: «ما في أحد رد، بكتب مرة ثانية: موظف».
P4 · T1: «أفتح الفاتورة أشوف». T2: «تمام». T3: «في رسالة تراجع، حلو». T4: «حوّلني؟ أوكي» (أغلق المهمة).
P5 · T1: «10 ديسمبر... طيب». T2: «الأربعاء؟ اخترت الثلاثاء، أرجع». T3: «الزر صغير مرة، كم مرة ضغطت» (95 ثانية). T4: «ما جاني شي، أضغط على تحدث إلى موظف».
''')
    write_txt('test_report_template.txt', '''
تقرير اختبار قابلية الاستخدام

1. ما اختبرناه ومع من (دون أسماء):
2. النتائج: نجاح المهام (لكل مهمة وإجماليًا)، والاعتماد المفرط على الأخطاء المزروعة، وزمن التعافي:
3. ما لا تقوله خمس جلسات (ومنه: هل كان المشاركون زملاء يعرفون أن في النموذج أخطاء مزروعة):
4. ثلاثة تعديلات على التصميم: لكل منها الملاحظة، والدليل (الرمز والمهمة)، والتعديل، وكيف نعرف أنه نجح:
5. من يراجع التعديلات قبل الإطلاق (غير من صممها):
''')
    write_prototype_solution()
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
