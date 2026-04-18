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


def render_document(title, body, active='', root=''):
    prefix = './' if root == '' else root
    nav = ''.join([
        f"<a href='{prefix}index.html'>{'בית' if active!='home' else '<strong>בית</strong>'}</a>",
        f"<a href='{prefix}audiences.html'>{'קהלי יעד' if active!='audiences' else '<strong>קהלי יעד</strong>'}</a>",
        f"<a href='{prefix}research.html'>{'מחקרים' if active!='research' else '<strong>מחקרים</strong>'}</a>",
        f"<a href='{prefix}recommendations.html'>{'המלצות' if active!='recommendations' else '<strong>המלצות</strong>'}</a>",
        f"<a href='{prefix}landing-pages.html'>{'דפי נחיתה' if active!='landing' else '<strong>דפי נחיתה</strong>'}</a>",
        f"<a href='{prefix}competitors.html'>{'מתחרים' if active!='competitors' else '<strong>מתחרים</strong>'}</a>",
        f"<a href='{prefix}opportunities.html'>{'הזדמנויות' if active!='opportunities' else '<strong>הזדמנויות</strong>'}</a>",
        f"<a href='{prefix}pages.html'>{'דפים ותוצרים' if active!='pages' else '<strong>דפים ותוצרים</strong>'}</a>",
    ])
    css = f"{prefix}assets/styles.css"
    gate_js = f"{prefix}assets/gate.js"
    return f"""<!doctype html><html lang='he' dir='rtl'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{title}</title><meta name='robots' content='noindex,nofollow,noarchive'><link rel='stylesheet' href='{css}'></head><body><div id='gate' class='gate'><div class='gate-card'><div class='pill'>Restricted</div><h1 style='font-size:28px;margin-top:10px'>כניסה לאתר המחקרים</h1><p class='muted'>האתר סגור לבוטים ולגישה חופשית. הכנס סיסמה כדי להמשיך.</p><input id='site-password' type='password' inputmode='numeric' autocomplete='current-password' placeholder='הכנס סיסמה'><button id='unlock-btn'>כניסה</button><div id='gate-error' class='error'></div></div></div><div id='app' class='hidden'><header><div class='hero'><div><div class='pill'>Market Research Hub</div><h1>{title}</h1><div class='muted small'>עודכן: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div></div><nav>{nav}</nav></div></header><main>{body}</main><footer class='muted small'>Continuous research repository, updated from live work.</footer></div><script src='{gate_js}'></script></body></html>"""


def write(path, html):
    path.write_text(html)


def card(title, body, meta=''):
    meta_html = f"<div class='muted small'>{meta}</div>" if meta else ''
    return f"<div class='card'><h3>{title}</h3>{meta_html}<p>{body}</p></div>"


def table(headers, rows):
    return "<table><thead><tr>" + ''.join([f'<th>{h}</th>' for h in headers]) + "</tr></thead><tbody>" + ''.join(["<tr>" + ''.join([f'<td>{c}</td>' for c in row]) + "</tr>" for row in rows]) + "</tbody></table>"


def main():
    summary = load('summary.json')
    audiences = load('audiences.json')
    research = load('market_research.json')
    recs = load('recommendations.json')
    pages = load('pages.json')
    integrations = load('integrations.json')
    skills = load('skills_required.json')
    competitors = load('competitors.json')
    opportunities = load('opportunities.json')
    profiles = load('segment_profiles.json')

    stat_cards = ''.join([f"<div class='card'><div class='muted small'>{k}</div><div style='font-size:30px;font-weight:bold'>{v}</div></div>" for k, v in summary['stats'].items()])
    segment_cards = ''.join([f"<a href='segments/{p['slug']}.html'>{card(p['name'], p['short_description'], f'עדיפות #{p['priority_rank']}')}</a>" for p in profiles])
    top_insights = ''.join([f"<li><strong>{i['title']}</strong> — {i['summary']}</li>" for i in summary['top_insights']])
    top_recs = ''.join([f"<li><strong>{i['title']}</strong> — {i['details']}</li>" for i in summary['top_recommendations']])
    home = f"<section class='grid'>{stat_cards}</section><section class='section card'><h2>תקציר מנהלים</h2><p>{summary['executive_summary']}</p><p><strong>סדר עדיפויות:</strong> {' ← '.join(summary['priority_order'])}</p></section><section class='section'><h2>סגמנטים</h2><div class='grid'>{segment_cards}</div></section><section class='section card'><h2>Top Insights</h2><ul>{top_insights}</ul></section><section class='section card'><h2>Top Recommendations</h2><ul>{top_recs}</ul></section>"
    write(SRC / 'index.html', render_document('Market Research Hub', home, 'home'))

    aud_rows = [[f"<a href='segments/{p['slug']}.html'>{p['name']}</a>", p['pain_level'], p['wtp_score'], p['decision_speed'], p['targeting_ease'], p['technical_complexity'], p['priority_rank'], p['recommended_offer'], p['recommended_mvp']] for p in profiles]
    write(SRC / 'audiences.html', render_document('קהלי יעד', f"<section class='card'>{table(['קהל','Pain','WTP','מהירות החלטה','קלות טירגוט','מורכבות טכנית','דירוג','הצעת ערך','MVP'], aud_rows)}</section>", 'audiences'))

    res_rows = [[r['created_at'], r['segment'], r['title'], r['summary'], r['pain_points'], r['objections'], r['priority_score']] for r in research]
    write(SRC / 'research.html', render_document('מחקרי שוק', f"<section class='card'>{table(['תאריך','סגמנט','כותרת','סיכום','כאבים','התנגדויות','Score'], res_rows)}</section>", 'research'))

    rec_cards = ''.join([card(r['title'], r['details'], f"{r['audience_name'] or 'כללי'} | {r['type']} | {r['priority']}") for r in recs])
    write(SRC / 'recommendations.html', render_document('המלצות', f"<section class='grid'>{rec_cards}</section>", 'recommendations'))

    landing = ''.join([card(p['name'], p['landing_angle'] + '<br><strong>Headline:</strong> ' + p['core_message'], f"<a href='segments/{p['slug']}.html'>לעמוד הסגמנט</a>") for p in profiles])
    write(SRC / 'landing-pages.html', render_document('המלצות לדפי נחיתה', f"<section class='grid'>{landing}</section>", 'landing'))

    comp_rows = [[c['segment'], c['competitor'], c['type'], c['strength'], c['weakness'], c['opportunity']] for c in competitors]
    write(SRC / 'competitors.html', render_document('מחקר מתחרים ראשוני', f"<section class='card'>{table(['סגמנט','מתחרה','סוג','חוזקה','חולשה','הזדמנות'], comp_rows)}</section>", 'competitors'))

    opp_cards = ''.join([card(o['workflow'], f"<strong>בעיה:</strong> {o['problem']}<br><strong>פתרון:</strong> {o['solution']}", f"{o['segment']} | {o['priority']}") for o in opportunities])
    write(SRC / 'opportunities.html', render_document('הזדמנויות מוצר', f"<section class='grid'>{opp_cards}</section>", 'opportunities'))

    page_rows = [[p['created_at'], p['title'], p['kind'], p['audience'], p['summary'], p['url_slug']] for p in pages]
    write(SRC / 'pages.html', render_document('דפים ותוצרים', f"<section class='card'>{table(['תאריך','כותרת','סוג','קהל','סיכום','slug'], page_rows)}</section>", 'pages'))

    for p in profiles:
        p_research = [r for r in research if r['segment'] == p['name']]
        p_recs = [r for r in recs if r['audience_name'] == p['name']]
        p_int = [i for i in integrations if i['audience_name'] == p['name']]
        p_skills = [s for s in skills if s['audience_name'] == p['name']]
        body = f"<section class='card'><h2>למה הקהל הזה חשוב</h2><p>{p['short_description']}</p><p><strong>מסר ליבה:</strong> {p['core_message']}</p><p><strong>זווית לדף נחיתה:</strong> {p['landing_angle']}</p><p><strong>צעד הבא:</strong> {p['next_step']}</p></section>"
        body += f"<section class='section card'><h2>Scoring</h2>{table(['Pain','WTP','Decision Speed','Targeting Ease','Technical Complexity','Priority Rank'], [[p['pain_level'],p['wtp_score'],p['decision_speed'],p['targeting_ease'],p['technical_complexity'],p['priority_rank']]])}</section>"
        body += f"<section class='section card'><h2>מחקרי מפתח</h2><ul>{''.join([f"<li><strong>{r['title']}</strong> — {r['summary']}</li>" for r in p_research])}</ul></section>"
        body += f"<section class='section card'><h2>המלצות</h2><ul>{''.join([f"<li><strong>{r['title']}</strong> — {r['details']}</li>" for r in p_recs])}</ul></section>"
        body += f"<section class='section card'><h2>אינטגרציות נדרשות</h2>{table(['מערכת','סוג','חשיבות','הערות'], [[i['system_name'], i['system_type'], i['importance'], i['notes']] for i in p_int])}</section>"
        body += f"<section class='section card'><h2>Skills נדרשים</h2>{table(['Skill','מטרה','עדיפות'], [[s['skill_name'], s['purpose'], s['priority']] for s in p_skills])}</section>"
        write(SEGMENTS / f"{p['slug']}.html", render_document(p['name'], body, root='../'))

    audience_master = "<section class='card'><h2>Audience Master Document</h2><p>עמוד זה מרכז את כל ההחלטות: scoring, סדר עדיפויות, זוויות מסר, אתגרים טכנולוגיים וצעדים הבאים.</p></section>"
    audience_master += f"<section class='section card'>{table(['קהל','מסר ליבה','זווית דף נחיתה','צעד הבא'], [[p['name'], p['core_message'], p['landing_angle'], p['next_step']] for p in profiles])}</section>"
    write(PAGES_DIR / 'audience-master.html', render_document('מסמך קהלי יעד מאוחד', audience_master, root='../'))


if __name__ == '__main__':
    main()
