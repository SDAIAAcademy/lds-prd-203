# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reference solution checker of LDS-PRD-203. Recomputes every key number of the labs from the
files in labs/files/ and the prototype in labs/prototype/, and asserts it. Standard library only.

    uv run labs/solutions/check.py          # every lab
    uv run labs/solutions/check.py 3.1      # one lab
"""
import csv
import re
import statistics
import sys
from html.parser import HTMLParser
from math import sqrt
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent
FILES = LABS / 'files'
PROTO = LABS / 'prototype'
sys.path.insert(0, str(LABS / '_tools'))
import prepare_files as P  # noqa: E402  the generator holds the planted answers

sys.stdout.reconfigure(encoding='utf-8')


def rows(name):
    with open(FILES / name, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def share(k, n):
    return f'{k}/{n} ({round(100 * k / n)}%)'


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(100 * (c - h)), round(100 * (c + h))


def lab_1_1():
    ids = [r['product_id'] for r in rows('pattern_table_template.csv')]
    assert ids == ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']
    patterns = {p: k[0] for p, k in P.PATTERN_KEY.items()}
    assert len(set(patterns.values())) == 5, 'the six products cover the five patterns'
    start = rows('pattern_table_start.csv')
    assert all(r['trust_risk'] == '' and r['mitigation'] == '' for r in start), 'lab 1.2 start must not show its answers'
    mism = [p for p, (_, a, rv) in P.PATTERN_KEY.items() if a >= 3 and rv in ('ق2', 'ق3') and p != 'P4']
    assert mism == [P.MISMATCH], mism
    print('1.1 key:', {p: (k[0], k[1], k[2]) for p, k in P.PATTERN_KEY.items()})
    print('1.1 mismatch of autonomy and reversibility:', P.MISMATCH)


def lab_1_2():
    letters = rows('letter_drafter_log.csv')
    fast = [r for r in letters if int(r['review_seconds']) < 5 and r['edited'] == '0']
    err = [r for r in letters if r['error_found_later'] == '1']
    with_error = 24
    assert len(letters) == 300
    print('1.2 P3 approved in under 5 s without edits:', share(len(fast), len(letters)))
    print('1.2 P3 drafts with an error that reached residents:', share(len(err), with_error), 'of drafts with an error')
    book = rows('booking_log.csv')
    free = [r for r in book if r['date_input'] == 'نص حر']
    pick = [r for r in book if r['date_input'] == 'قائمة']
    assert len(free) == 300 and len(pick) == 100
    cf = sum(int(r['clarification_needed']) for r in free)
    cp = sum(int(r['clarification_needed']) for r in pick)
    mf = sum(int(r['date_misread']) for r in free)
    mp = sum(int(r['date_misread']) for r in pick)
    assert cf / 300 > 3 * cp / 100 and mp == 0
    print('1.2 P4 clarification: free text', share(cf, 300), '| picker', share(cp, 100))
    print('1.2 P4 date misread: free text', share(mf, 300), '| picker', share(mp, 100))
    tf = statistics.mean(int(r['turns']) for r in free)
    tp = statistics.mean(int(r['turns']) for r in pick)
    print(f'1.2 P4 mean turns: free text {tf:.1f} | picker {tp:.1f}')
    valve = rows('valve_watch_log.csv')
    false = [r for r in valve if r['leak_confirmed'] == '0']
    prio = [r for r in valve if r['priority_medical_home'] == '1']
    prio_false = [r for r in prio if r['leak_confirmed'] == '0']
    assert len(valve) == 60 and len(false) == 22 and len(prio) == 3 and len(prio_false) == 2
    hrs = statistics.median(float(r['hours_without_water']) for r in valve)
    print('1.2 P5 closures that were not leaks:', share(len(false), 60), '| at priority medical homes:', len(prio), f'({len(prio_false)} not leaks)', '| median hours without water:', hrs)
    meter = rows('meter_photo_log.csv')
    mis = sum(int(r['misread']) for r in meter)
    cor = sum(int(r['corrected_by_resident']) for r in meter)
    assert (mis, cor) == (18, 5)
    print('1.2 P6 misreads:', share(mis, 300), '| corrected by the resident:', share(cor, mis))


def lab_1_3():
    ev = [[r['item_id'], r['topic'], r['language'], int(r['answer_cites_source']), r['verdict'], r['model_confidence'], r['latency_seconds']]
          for r in rows('eval_results.csv')]
    assert len(ev) == 240
    cap = P.capability(ev)
    print('1.3 acceptable overall:', share(*cap['all']))
    print('1.3 by topic:', {k: f'{P.pct(v)}%' for k, v in cap['topic'].items()})
    print('1.3 by language:', {k: f'{P.pct(v)}%' for k, v in cap['lang'].items()})
    print('1.3 cites a source:', f"{P.pct(cap['sourced'][1])}% vs {P.pct(cap['sourced'][0])}% without")
    print('1.3 mean confidence acceptable vs not:', cap['conf'][True], cap['conf'][False], '| not acceptable at 0.9 or more:', share(*cap['high_conf_bad']))
    print('1.3 refused wrongly:', cap['refused_wrongly'], 'of which moving service:', cap['refused_wrongly_moving'])
    print('1.3 latency median', cap['lat_median'], 's, outage median', cap['lat_outage_median'], 's')
    two = sorted(cap['topic'], key=lambda k: P.pct(cap['topic'][k]))[:2]
    assert set(two) == {'الانقطاعات وأوقات العودة', 'نقل الخدمة'}, two
    assert P.pct(cap['lang']['مختلطة أو عربيزي']) < P.pct(cap['lang']['فصحى']) - 10
    assert abs(cap['conf'][True] - cap['conf'][False]) < 0.06


def lab_1_4():
    ref = rows('capability_reference.csv')
    assert [r['id'] for r in ref] == [f'C{i:02d}' for i in range(1, 9)]
    assert all(r['what_the_screen_should_say'] == '' for r in ref), 'lab 1.4 start must not show its answers'
    cues = {'O1': 'C03 C05', 'O2': 'C03 C04', 'R1': 'C03', 'R2': 'C02', 'R3': 'C07'}
    print('1.4 reference cues and their evidence:', cues)
    js = (PROTO / 'content.js').read_text(encoding='utf-8')
    assert 'يجيب عن كل أسئلتك بدقة' in js, 'the shipped prototype starts from the current overclaiming onboarding'


def lab_2_1():
    els = [r['element'] for r in rows('disclosure_audit_template.csv')]
    assert els == [d[0] for d in P.DISCLOSURE]
    keep = [k for k, v in P.DISCLOSURE_KEY.items() if v[0] == 'يبقى']
    print('2.1 keep:', keep, '| change:', [k for k in P.DISCLOSURE_KEY if k not in keep])


def lab_2_2():
    kinds = {}
    for f, k in P.FAILURE_KEY.items():
        kinds.setdefault(k, []).append(f)
    assert len(P.FAILURE_KEY) == 12
    print('2.2 failures by kind:', kinds)


def lab_2_3():
    assert [r['action_id'] for r in rows('agent_actions.csv')] == list(P.ACTION_KEY)
    print('2.3 key:', {a: (k[0], k[1]) for a, k in P.ACTION_KEY.items()})
    order = {'ق1': 1, 'ق2': 2, 'ق3': 3}
    lvl = {'م0': 0, 'م1': 1, 'م2': 2, 'م3': 3}
    for a, (rv, cl, _) in P.ACTION_KEY.items():
        assert lvl[cl] >= order[rv] - 1, (a, rv, cl)


def lab_2_4():
    assert [r['action_id'] for r in rows('action_grading_reference.csv')] == list(P.ACTION_KEY)
    print('2.4 rules per scenario:', P.SCENARIO_KEY)
    assert P.SCENARIO_KEY['S8'] == [], 'S8 is an action with confirmation (A6), not a hand-off'
    ref = rows('action_grading_reference.csv')
    assert all(r['confirmation_text'] for r in ref), 'every action has a reference confirmation text'
    assert [r['action_id'] for r in ref if r['handoff_rule']] == ['A5'], 'only A5 is governed by a hand-off rule (H6)'
    import csv as _csv
    cov = list(_csv.DictReader((LABS / 'solutions' / 'coverage_reference.csv').open(encoding='utf-8-sig')))
    tmpl = rows('coverage_template.csv')
    assert [r['item'] for r in cov] == [r['item'] for r in tmpl], 'the reference covers every row of the template'
    assert all(r['success_path'] and r['failure_path'] and r['refusal_or_handoff_path'] for r in cov), 'no empty cell'
    print('2.4 coverage reference:', len(cov), 'rows, no empty cell')


class Proto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def lum(hex_colour):
    c = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def lab_3_1():
    html = (PROTO / 'index.html').read_text(encoding='utf-8')
    p = Proto()
    p.feed(html)
    tags = p.tags
    html_tag = [a for t, a in tags if t == 'html'][0]
    assert html_tag.get('lang') == 'en', 'X7'
    reply = [a for t, a in tags if a.get('id') == 'reply-stream'][0]
    assert 'aria-live' not in reply and 'role' not in reply, 'X1'
    send = [(t, a) for t, a in tags if a.get('id') == 'send'][0]
    assert send[0] == 'div' and 'tabindex' not in send[1] and 'aria-label' not in send[1], 'X2'
    msg = [a for t, a in tags if a.get('id') == 'msg'][0]
    assert 'aria-label' not in msg and not re.search(r'<label[^>]*for="msg"', html), 'X3'
    ratio = contrast(*P.LOW_CONTRAST)
    assert P.LOW_CONTRAST[0] in html and ratio < 4.5, 'X4'
    assert 'outline: none' in html, 'X5'
    assert 'id="confirm-dialog"' in html and 'Escape' not in html, 'X6'
    assert re.search(r'\.slot\s*{[^}]*width:\s*20px;\s*height:\s*20px', html), 'X8'
    assert 'slot-taken' in html and 'border-color: #d33' in html, 'X9'
    print(f'3.1 nine planted defects present; X4 contrast {ratio:.2f}:1 (needs 4.5:1)')
    fixed = (LABS / 'solutions' / 'prototype' / 'index.html').read_text(encoding='utf-8')
    fixjs = (LABS / 'solutions' / 'prototype' / 'fix.js').read_text(encoding='utf-8')
    assert 'lang="ar"' in fixed and 'role="log"' in fixed and 'Escape' in fixjs and 'outline: none' not in fixed
    assert '<label for="msg">' in fixed and '<button id="send" type="submit" aria-label=' in fixed and 'role="alert"' in fixed
    fixed_colour = re.search(r'--muted:\s*(#[0-9a-f]{6})', fixed).group(1)
    print(f'3.1 fixed version: muted text {fixed_colour} at {contrast(fixed_colour, "#ffffff"):.2f}:1')
    assert contrast(fixed_colour, '#ffffff') >= 4.5


def lab_3_2():
    scripts = rows('bidi_scripts.csv')
    assert len(scripts) == 20
    d = P.bidi_defects()
    print('3.2 scripts with a defect in the bench:', len(d), d)
    print('3.2 scripts that render correctly:', [b[0] for b in P.BIDI if not b[3]])
    bench = (PROTO / 'bench.html').read_text(encoding='utf-8')
    for sid in [b[0] for b in P.BIDI]:
        assert sid in bench, sid


def lab_3_3():
    tasks = [t[0] for t in P.TASKS]
    assert tasks == ['T1', 'T2', 'T3', 'T4']
    js = (PROTO / 'content.js').read_text(encoding='utf-8')
    assert re.search(r"seeded:\s*\['E1', 'E2', 'E3'\]", js), 'the lab runs with E1 to E3'
    print('3.3 seeded errors in the lab:', {k: P.SEEDED[k] for k in ('E1', 'E2', 'E3')})
    app = (PROTO / 'app.js').read_text(encoding='utf-8')

    def body(name):
        m = re.search(r'\n  function ' + name + r'\(.*?(?=\n  function |\n  /\* -)', app, re.S)
        assert m, name
        return m.group(0)
    where = {'T1': re.search(r"case 'bill':.*?case 'outage'", app, re.S).group(0),
             'T2': body('summary'),
             'T3': body('cancelVisit') + body('undoCancel'),
             'T4': body('handoff')}
    pool = sorted(k for k in P.SEEDED if k not in ('E1', 'E2', 'E3'))
    assert sorted(P.POOL_TASK) == pool
    for e, t in sorted(P.POOL_TASK.items()):
        assert f"seeded('{e}')" in where[t], f'{e} is not reached in {t}'
        assert app.count(f"seeded('{e}')") == 1, f'{e} also shows outside {t}'
    assert "seeded('E3')" in where['T4'], 'E3 shows on every route to a person'
    tasks_per_error = {e: P.POOL_TASK[e] for e in pool}
    print('3.3 pool for the capstone, each reached in its task:', tasks_per_error)
    print('3.3 pool tasks covered:', sorted(set(tasks_per_error.values())))


def lab_3_4():
    ses = [[r['participant'], r['task'], r['success'], r['seeded_error'], r['accepted_error'], r['recovery_seconds'], r['task_seconds']]
           for r in rows('sessions_five.csv')]
    m = P.session_metrics(ses)
    assert m['success'] == (11, 20), m['success']
    assert m['overreliance'] == (8, 15), m['overreliance']
    print('3.4 task success:', share(*m['success']), 'Wilson 95%:', wilson(*m['success']))
    print('3.4 by task:', {k: f'{v[0]}/{v[1]}' for k, v in m['by_task'].items()})
    print('3.4 accepted seeded errors:', share(*m['overreliance']), 'by error:', m['by_error'])
    print('3.4 T3 recovery seconds:', m['recovery'], 'median', m['recovery_median'], '| recovered', f"{m['recovery_done'][0]}/5")
    per_session = {}
    for r in ses:
        per_session[r[0]] = per_session.get(r[0], 0) + int(r[6])
    assert max(per_session.values()) <= 8 * 60, 'a session needs more than the 8 task minutes of the capstone round'
    print('3.4 task minutes per session:', {k: round(v / 60, 1) for k, v in per_session.items()}, '(capstone window 8)')


LABS_FN = {'1.1': lab_1_1, '1.2': lab_1_2, '1.3': lab_1_3, '1.4': lab_1_4, '2.1': lab_2_1, '2.2': lab_2_2,
           '2.3': lab_2_3, '2.4': lab_2_4, '3.1': lab_3_1, '3.2': lab_3_2, '3.3': lab_3_3, '3.4': lab_3_4}

if __name__ == '__main__':
    want = sys.argv[1:] or list(LABS_FN)
    for k in want:
        LABS_FN[k]()
    print('PASS', ', '.join(want))
