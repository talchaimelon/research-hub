import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPORTS = ROOT / 'data' / 'exports'
SRC = ROOT / 'src'
SEGMENTS = SRC / 'segments'
PAGES_DIR = SRC / 'pages'
for d in [SEGMENTS, PAGES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def load(name):
    return json.loads((EXPORTS / name).read_text())


def nav_link(prefix, href, label, active, key):
    cls = 'nav-link active' if active == key else 'nav-link'
    return f"<a class='{cls}' href='{prefix}{href}'>{label}</a>"


def render_document(title, body, active='', root='', summary=''):
    prefix = './' if root == '' else root
    nav = ''.join([
        nav_link(prefix, 'index.html', 'בית', active, 'home'),
        nav_link(prefix, 'audiences.html', 'קהלי יעד', active, 'audiences'),
        nav_link(prefix, 'research.html', 'מחקרים', active, 'research'),
        nav_link(prefix, 'recommendations.html', 'המלצות', active, 'recommendations'),
        nav_link(prefix, 'landing-pages.html', 'דפי נחיתה', active, 'landing'),
        nav_link(prefix, 'competitors.html', 'מתחרים', active, 'competitors'),
        nav_link(prefix, 'opportunities.html', 'הזדמנויות', active, 'opportunities'),
        nav_link(prefix, 'pages.html', 'דפים ותוצרים', active, 'pages'),
    ])
    css = f"{prefix}assets/styles.css"
    gate_js = f"{prefix}assets/gate.js"
    return f"""<!doctype html><html lang='he' dir='rtl'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{title}</title><meta name='robots' content='noindex,nofollow,noarchive'><link rel='stylesheet' href='{css}'></head><body><div id='gate' class='gate'><div class='gate-card'><div class='pill'>Restricted</div><h1 style='font-size:28px;margin-top:14px'>כניסה לאתר המחקרים</h1><p class='muted'>האתר סגור לבוטים ולגישה חופשית. הכנס סיסמה כדי להמשיך.</p><input id='site-password' type='password' inputmode='numeric' autocomplete='current-password' placeholder='הכנס סיסמה'><button id='unlock-btn'>כניסה</button><div id='gate-error' class='error'></div></div></div><div id='app' class='hidden'><header><div class='hero'><div class='hero-copy'><div class='pill'>Market Research Hub</div><h1>{title}</h1><p>{summary}</p><div class='hero-actions'><a class='btn' href='{prefix}audiences.html'>קהלי יעד</a><a class='btn secondary' href='{prefix}research.html'>מחקרי שוק</a></div></div><div class='small muted'>עודכן: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div></div><div class='section'><nav>{nav}</nav></div></header><main>{body}</main><footer class='footer-note small'>Continuous research repository, updated from live work.</footer></div><script src='{gate_js}'></script></body></html>"""


def write(path, html):
    path.write_text(html)


def card(title, body, meta=''):
    meta_html = f"<div class='kicker'>{meta}</div>" if meta else ''
    return f"<div class='card'><h3 style='margin:0 0 10px'>{title}</h3>{meta_html}<div class='muted' style='margin-top:10px'>{body}</div></div>"


def table(headers, rows):
    return "<div class='table-wrap'><table><thead><tr>" + ''.join([f'<th>{h}</th>' for h in headers]) + "</tr></thead><tbody>" + ''.join(["<tr>" + ''.join([f'<td>{c}</td>' for c in row]) + "</tr>" for row in rows]) + "</tbody></table></div>"


def section(title, desc, inner):
    return f"<section class='section'><div class='section-head'><div><h2>{title}</h2><p>{desc}</p></div></div>{inner}</section>"


def status_badge(status):
    label = 'ממתין לאישור' if status == 'pending_approval' else 'מאושר'
    return f"<span class='pill'>{label}</span>"


def main():
    summary = load('summary.json')
    research = load('market_research.json')
    recs = load('recommendations.json')
    pages = load('pages.json')
    integrations = load('integrations.json')
    skills = load('skills_required.json')
    competitors = load('competitors.json')
    opportunities = load('opportunities.json')
    profiles = load('segment_profiles.json')

    stats = ''.join([f"<div class='card stat'><div class='muted small'>{k}</div><div class='num'>{v}</div></div>" for k, v in summary['stats'].items()])
    segment_cards = ''.join([f"<a href='segments/{p['slug']}.html'>{card(p['name'], p['short_description'] + '<br><br>' + status_badge(p['status']), f'עדיפות #{p['priority_rank']}')}</a>" for p in profiles])
    insights = ''.join([f"<li><strong>{i['title']}</strong>, {i['summary']}</li>" for i in summary['top_insights']])
    top_recs = ''.join([f"<li><strong>{i['title']}</strong>, {i['details']}</li>" for i in summary['top_recommendations']])
    pending_cards = ''.join([card(p['name'], p['next_step'], 'pending approval') for p in profiles if p['status'] == 'pending_approval'])
    home = section('מדדי ליבה', 'מבט מהיר על היקף הידע שכבר יושב באתר.', f"<div class='metric-strip'>{stats}</div>")
    home += section('תקציר מנהלים', 'מה החלטנו עד עכשיו, בלי לקבור אותך בדאטה.', f"<div class='card'><p>{summary['executive_summary']}</p><p><strong>סדר עדיפויות:</strong> {' ← '.join(summary['priority_order'])}</p></div>")
    if pending_cards:
        home += section('מחכים לאישור', 'גם הכיוונים שעוד לא אושרו כבר בפנים, כדי שלא ילכו לאיבוד.', f"<div class='grid'>{pending_cards}</div>")
    home += section('סגמנטים', 'עמודי עומק לכל קהל, כולל כאלה שמחכים לאישור.', f"<div class='grid'>{segment_cards}</div>")
    home += section('Top Insights', 'הנקודות הכי חזקות שעלו מהמחקר עד עכשיו.', f"<div class='card'><ul class='list-clean'>{insights}</ul></div>")
    home += section('Top Recommendations', 'מה לעשות הלאה, ואיך למסגר את זה.', f"<div class='card'><ul class='list-clean'>{top_recs}</ul></div>")
    write(SRC / 'index.html', render_document('Market Research Hub', home, 'home', summary='מרכז אחד למחקרי שוק, קהלי יעד, המלצות מוצר והזדמנויות צמיחה, כולל כיוונים שממתינים לאישור.'))

    aud_cards = ''.join([card(p['name'], f"{status_badge(p['status'])}<br><br><strong>Pain:</strong> {p['pain_level']} | <strong>WTP:</strong> {p['wtp_score']} | <strong>מהירות החלטה:</strong> {p['decision_speed']}<br><br><strong>הצעת ערך:</strong> {p['recommended_offer']}<br><strong>MVP:</strong> {p['recommended_mvp']}", f"עדיפות #{p['priority_rank']}") for p in profiles])
    write(SRC / 'audiences.html', render_document('קהלי יעד', section('מפת קהלים', 'כל הקהלים בפנים, כולל אלה שמחכים לאישור.', f"<div class='grid'>{aud_cards}</div>") + section('השוואה מהירה', 'אם צריך מספרים, הם כאן.', table(['קהל','סטטוס','Pain','WTP','מהירות החלטה','קלות טירגוט','מורכבות טכנית'], [[p['name'], 'ממתין' if p['status']=='pending_approval' else 'מאושר', p['pain_level'], p['wtp_score'], p['decision_speed'], p['targeting_ease'], p['technical_complexity']] for p in profiles])), 'audiences', summary='השוואה ברורה בין קהלים מאושרים וקניונים שממתינים לאישור, עם סדר עדיפויות ומסרי ליבה.'))

    research_cards = ''.join([card(r['title'], f"<strong>סגמנט:</strong> {r['segment']}<br><br>{status_badge(r['status'])}<br><br>{r['summary']}<br><br><strong>כאבים:</strong> {r['pain_points']}<br><strong>התנגדויות:</strong> {r['objections']}", f"Score {r['priority_score']}") for r in research])
    write(SRC / 'research.html', render_document('מחקרי שוק', section('תובנות מחקר', 'כל המחקרים בפנים, גם pending approval.', f"<div class='grid'>{research_cards}</div>"), 'research', summary='מאגר מחקרי שוק חי, מסודר לפי סגמנטים, כאבים, התנגדויות, ציון עדיפות וסטטוס אישור.'))

    rec_cards = ''.join([card(r['title'], status_badge(r['status']) + '<br><br>' + r['details'], f"{r['audience_name'] or 'כללי'} · {r['type']} · {r['priority']}") for r in recs])
    write(SRC / 'recommendations.html', render_document('המלצות', section('מה לעשות עכשיו', 'המלצות action-oriented לפי קהל, מוצר, מחקר ודפי נחיתה.', f"<div class='grid'>{rec_cards}</div>"), 'recommendations', summary='רשימת ההמלצות הפרקטיות ביותר, כולל כאלה שמחכות לאישור ולא רק המאושרות.'))

    landing = ''.join([card(p['name'], f"{status_badge(p['status'])}<br><br><strong>מסר ליבה:</strong> {p['core_message']}<br><br><strong>זווית לדף נחיתה:</strong> {p['landing_angle']}", f"<a href='segments/{p['slug']}.html'>לעמוד הסגמנט</a>") for p in profiles])
    write(SRC / 'landing-pages.html', render_document('המלצות לדפי נחיתה', section('Angles לדפי נחיתה', 'איך למכור כל קהל בלי להיות כללי ומרוח.', f"<div class='grid'>{landing}</div>"), 'landing', summary='מסגור מסרים ו-headlines לדפי נחיתה לפי קהל, pain, outcome וסטטוס אישור.'))

    comp_cards = ''.join([card(c['competitor'], f"<strong>סגמנט:</strong> {c['segment']}<br><strong>חוזקה:</strong> {c['strength']}<br><strong>חולשה:</strong> {c['weakness']}<br><strong>הזדמנות:</strong> {c['opportunity']}", c['type']) for c in competitors])
    write(SRC / 'competitors.html', render_document('מחקר מתחרים ראשוני', section('Landscape', 'מי קיים בשטח, איפה הוא חזק, ואיפה אפשר לעקוף אותו.', f"<div class='grid'>{comp_cards}</div>"), 'competitors', summary='מיפוי ראשוני של אלטרנטיבות, פלטפורמות וכלים שמתחרים על תשומת הלב של הלקוח.'))

    opp_cards = ''.join([card(o['workflow'], f"{status_badge(o['status'])}<br><br><strong>סגמנט:</strong> {o['segment']}<br><strong>בעיה:</strong> {o['problem']}<br><strong>פתרון:</strong> {o['solution']}", o['priority']) for o in opportunities])
    write(SRC / 'opportunities.html', render_document('הזדמנויות מוצר', section('Opportunity Map', 'איפה הכי משתלם לבנות משהו narrow עם ROI חד.', f"<div class='grid'>{opp_cards}</div>"), 'opportunities', summary='מפת הזדמנויות למוצר, כולל workflows שמחכים לאישור ולא רק המסלולים הפעילים.'))

    page_cards = ''.join([card(p['title'], status_badge(p['status']) + '<br><br>' + p['summary'], f"{p['kind']} · {p['audience']}") for p in pages])
    write(SRC / 'pages.html', render_document('דפים ותוצרים', section('Library', 'כל הדפים, התוצרים והמסמכים שהופקו עד עכשיו.', f"<div class='grid'>{page_cards}</div>"), 'pages', summary='ספריית התוצרים של המחקר, כולל דפים מאושרים ודפים שמחכים לאישור.'))

    for p in profiles:
        p_research = [r for r in research if r['segment'] == p['name']]
        p_recs = [r for r in recs if r['audience_name'] == p['name']]
        p_int = [i for i in integrations if i['audience_name'] == p['name']]
        p_skills = [s for s in skills if s['audience_name'] == p['name']]
        body = section('למה הקהל הזה חשוב', 'Snapshot אסטרטגי, בלי לחפש בפסקאות.', f"<div class='grid-2'><div class='card'><div class='kicker'>סטטוס</div><h3>{'ממתין לאישור' if p['status']=='pending_approval' else 'מאושר'}</h3><p class='muted'>{p['core_message']}</p></div><div class='card'><div class='kicker'>מה עושים next</div><h3>{p['next_step']}</h3><p class='muted'>{p['landing_angle']}</p></div></div>")
        body += section('Scoring', 'המספרים עדיין כאן, אבל לא בתור כל החוויה.', f"<div class='metric-strip'><div class='card stat'><div class='muted small'>Pain</div><div class='num'>{p['pain_level']}</div></div><div class='card stat'><div class='muted small'>WTP</div><div class='num'>{p['wtp_score']}</div></div><div class='card stat'><div class='muted small'>Decision Speed</div><div class='num'>{p['decision_speed']}</div></div><div class='card stat'><div class='muted small'>Targeting Ease</div><div class='num'>{p['targeting_ease']}</div></div><div class='card stat'><div class='muted small'>Technical Complexity</div><div class='num'>{p['technical_complexity']}</div></div></div>")
        body += section('מחקרי מפתח', 'התובנות העיקריות על הקהל הזה.', f"<div class='feature-list'>{''.join([f'<div class="feature-item">{status_badge(r["status"])}<br><br><strong>{r["title"]}</strong><br><span class="muted">{r["summary"]}</span></div>' for r in p_research])}</div>")
        body += section('המלצות', 'מה לעשות עם הקהל הזה בשלב הבא.', f"<div class='feature-list'>{''.join([f'<div class="feature-item">{status_badge(r["status"])}<br><br><strong>{r["title"]}</strong><br><span class="muted">{r["details"]}</span></div>' for r in p_recs])}</div>")
        body += section('אינטגרציות נדרשות', 'איזה מערכות המוצר הזה יצטרך לגעת בהן.', table(['מערכת','סוג','חשיבות','הערות'], [[i['system_name'], i['system_type'], i['importance'], i['notes']] for i in p_int]))
        body += section('Skills נדרשים', 'אילו יכולות נצטרך כדי לבנות נכון.', table(['Skill','מטרה','עדיפות'], [[s['skill_name'], s['purpose'], s['priority']] for s in p_skills]))
        write(SEGMENTS / f"{p['slug']}.html", render_document(p['name'], body, root='../', summary='עמוד עומק ממוקד לקהל אחד, כולל סטטוס אישור, value prop, MVP, אינטגרציות והצעדים הבאים.'))

    audience_master = section('Audience Master', 'מפת החלטה אחת שמרכזת את כל הקהלים במקום אחד.', f"<div class='grid'>{''.join([card(p['name'], status_badge(p['status']) + f'<br><br><strong>מסר ליבה:</strong> {p["core_message"]}<br><br><strong>זווית לדף נחיתה:</strong> {p["landing_angle"]}<br><br><strong>צעד הבא:</strong> {p["next_step"]}', f'עדיפות #{p["priority_rank"]}') for p in profiles])}</div>")
    write(PAGES_DIR / 'audience-master.html', render_document('מסמך קהלי יעד מאוחד', audience_master, root='../', summary='עמוד־על שמרכז את מה שחשוב באמת, כולל קהלים מאושרים ואלה שמחכים לאישור.'))


if __name__ == '__main__':
    main()
