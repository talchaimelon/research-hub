import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPORTS = ROOT / 'data' / 'exports'
SRC = ROOT / 'src'


def load(name):
    return json.loads((EXPORTS / name).read_text())


def render_page(title, body, active=''):
    nav = ''.join([
        f"<a href='index.html'>{'בית' if active!='home' else '<strong>בית</strong>'}</a>",
        f"<a href='audiences.html'>{'קהלי יעד' if active!='audiences' else '<strong>קהלי יעד</strong>'}</a>",
        f"<a href='research.html'>{'מחקרים' if active!='research' else '<strong>מחקרים</strong>'}</a>",
        f"<a href='recommendations.html'>{'המלצות' if active!='recommendations' else '<strong>המלצות</strong>'}</a>",
        f"<a href='pages.html'>{'דפים ותוצרים' if active!='pages' else '<strong>דפים ותוצרים</strong>'}</a>",
    ])
    return f"""<!doctype html><html lang='he' dir='rtl'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{title}</title><link rel='stylesheet' href='assets/styles.css'></head><body><header><div class='hero'><div><div class='pill'>Market Research Hub</div><h1>{title}</h1><div class='muted small'>עודכן: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div></div><nav>{nav}</nav></div></header><main>{body}</main><footer class='muted small'>Built for continuous research updates.</footer></body></html>"""


def save(name, html):
    (SRC / name).write_text(html)


def main():
    summary = load('summary.json')
    audiences = load('audiences.json')
    research = load('market_research.json')
    recs = load('recommendations.json')
    pages = load('pages.json')

    home_cards = ''.join([f"<div class='card'><div class='muted small'>{k}</div><div style='font-size:30px;font-weight:bold'>{v}</div></div>" for k,v in summary['stats'].items()])
    top_insights = ''.join([f"<li><strong>{i['title']}</strong> — {i['summary']}</li>" for i in summary['top_insights']])
    top_recs = ''.join([f"<li><strong>{i['title']}</strong> — {i['details']}</li>" for i in summary['top_recommendations']])
    save('index.html', render_page('Market Research Hub', f"<section class='grid'>{home_cards}</section><section class='section card'><h2>תקציר מנהלים</h2><p>{summary['executive_summary']}</p></section><section class='section card'><h2>Top Insights</h2><ul>{top_insights}</ul></section><section class='section card'><h2>Top Recommendations</h2><ul>{top_recs}</ul></section>", 'home'))

    aud_rows = [[a['name'], a['short_description'], a['pain_level'], a['wtp_score'], a['decision_speed'], a['targeting_ease'], a['technical_complexity'], a['priority_rank'], a['recommended_offer'], a['recommended_mvp']] for a in audiences]
    aud_table = "<table><thead><tr><th>קהל</th><th>תיאור</th><th>Pain</th><th>WTP</th><th>מהירות החלטה</th><th>קלות טירגוט</th><th>מורכבות טכנית</th><th>דירוג</th><th>הצעת ערך</th><th>MVP</th></tr></thead><tbody>" + ''.join(["<tr>" + ''.join([f"<td>{c}</td>" for c in row]) + "</tr>" for row in aud_rows]) + "</tbody></table>"
    save('audiences.html', render_page('קהלי יעד', f"<section class='card'>{aud_table}</section>", 'audiences'))

    res_rows = [[r['created_at'], r['segment'], r['title'], r['summary'], r['pain_points'], r['objections'], r['priority_score'], r['status']] for r in research]
    res_table = "<table><thead><tr><th>תאריך</th><th>סגמנט</th><th>כותרת</th><th>סיכום</th><th>כאבים</th><th>התנגדויות</th><th>Score</th><th>סטטוס</th></tr></thead><tbody>" + ''.join(["<tr>" + ''.join([f"<td>{c}</td>" for c in row]) + "</tr>" for row in res_rows]) + "</tbody></table>"
    save('research.html', render_page('מחקרי שוק', f"<section class='card'>{res_table}</section>", 'research'))

    rec_cards = ''.join([f"<div class='card'><div class='pill'>{r['type']}</div><h3>{r['title']}</h3><div class='muted small'>{r['audience_name'] or 'כללי'} | {r['priority']}</div><p>{r['details']}</p></div>" for r in recs])
    save('recommendations.html', render_page('המלצות', f"<section class='grid'>{rec_cards}</section>", 'recommendations'))

    page_rows = [[p['created_at'], p['title'], p['kind'], p['audience'], p['summary'], p['status']] for p in pages]
    page_table = "<table><thead><tr><th>תאריך</th><th>כותרת</th><th>סוג</th><th>קהל</th><th>סיכום</th><th>סטטוס</th></tr></thead><tbody>" + ''.join(["<tr>" + ''.join([f"<td>{c}</td>" for c in row]) + "</tr>" for row in page_rows]) + "</tbody></table>"
    save('pages.html', render_page('דפים ותוצרים', f"<section class='card'>{page_table}</section>", 'pages'))


if __name__ == '__main__':
    main()
