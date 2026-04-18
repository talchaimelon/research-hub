import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'research.db'
SCHEMA = ROOT / 'schema' / 'schema.sql'
EXPORTS = ROOT / 'data' / 'exports'
RAW = ROOT / 'content' / 'raw' / '2026-04-18-seed.md'
GENERATED = ROOT / 'content' / 'generated' / 'latest-summary.md'
now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

audiences = [
    {
        'name':'פרילנסרים / מנהלי צוות עצמאיים','category':'operations','short_description':'עצמאיים וסוכנויות קטנות שמחפשים leverage, אוטומציה ויותר תפוקה ללא גיוס.','pain_level':5,'wtp_score':4,'decision_speed':5,'targeting_ease':4,'technical_complexity':3,'priority_rank':1,
        'recommended_offer':'בנו לעצמכם עובד AI פנימי ללידים, הצעות מחיר, בריפים ו-follow-up','recommended_mvp':'טופס intake + סיכום דרישה + draft להצעת מחיר + follow-up reminders','notes':'קהל ראשון מומלץ. ROI מהיר, מעט חסמי רגולציה.'
    },
    {
        'name':'רואי חשבון / פיננסים','category':'finance','short_description':'משרדי ראיית חשבון ופיננסים עם עומס מסמכים, בדיקות, מעקב וחוסרים.','pain_level':5,'wtp_score':5,'decision_speed':3,'targeting_ease':4,'technical_complexity':4,'priority_rank':2,
        'recommended_offer':'בנו תהליכי AI פנימיים שחוסכים שעות עבודה בלי להחליף את המערכות הקיימות','recommended_mvp':'קליטת מסמכים + סיווג + dashboard לחוסרים + follow-up ללקוחות','notes':'Vertical חזק, אך דורש בקרה, audit trail ו-human-in-the-loop.'
    },
    {
        'name':'אנשי HR / גיוס','category':'hr','short_description':'צוותי HR וגיוס שרוצים לקצר עבודה תפעולית ולבנות כלי AI פנימיים.','pain_level':4,'wtp_score':4,'decision_speed':3,'targeting_ease':4,'technical_complexity':4,'priority_rank':3,
        'recommended_offer':'בנו כלי AI פנימיים שמקצרים עבודת גיוס ותפעול HR בלי תלות בפיתוח','recommended_mvp':'resume parsing + scorecard + interview questions + feedback summarizer','notes':'טוב, אבל רגיש לפרטיות, bias ואישור ארגוני.'
    },
    {
        'name':'סוכני נדל"ן / מתווכים','category':'real-estate','short_description':'מתווכים ומשרדי תיווך שרוצים follow-up מהיר יותר, סדר בלידים ויותר עסקאות.','pain_level':4,'wtp_score':3,'decision_speed':4,'targeting_ease':3,'technical_complexity':3,'priority_rank':4,
        'recommended_offer':'בנו עוזר AI ללידים, תיאומי פגישות ומעקב שוטף','recommended_mvp':'lead intake + prioritization + follow-up + התאמת נכסים בסיסית','notes':'יש כאב, אבל adoption פחות יציב.'
    }
]

research = [
    ('פרילנסרים / מנהלי צוות עצמאיים','הקהל המהיר ביותר ל-ROI','הקהל הזה חי על זמן, הצעות מחיר, בריפים ו-follow-up, ולכן מבין מהר leverage וערך.','אדמין, bottleneck, proposals, follow-up','לבנות עובד AI פנימי שמקצר זמן ומעלה תפוקה','רוצים להרוויח יותר בלי להגדיל צוות','עסוק מדי, כבר משתמש ב-ChatGPT','chat','telegram group',5,30),
    ('רואי חשבון / פיננסים','Vertical עם כאב חד ו-WTP גבוה','הכאב ברור, הכסף ברור, והחיסכון בשעות חוזר ישירות לרווחיות המשרד.','מסמכים, חוסרים, checklists, עבודה שחורה','AI כעוזר תפעולי עם בקרה ולא כתחליף לשיקול דעת','לחסוך שעות, לשפר סדר, לשרת יותר לקוחות','רגולציה, דיוק, אמון','chat','telegram group',5,29),
    ('אנשי HR / גיוס','כאב אמיתי אבל מחזור החלטה איטי יותר','צוותי HR סובלים מעומס תפעולי, אבל נתקלים בפרטיות, bias ותהליכי אישור ארגוניים.','סינון קו"ח, תיאום, פידבק מראיינים','פחות אדמין, יותר גיוס','לקצר זמן גיוס ולהיראות חדשניים','פרטיות, bias, מערכות סגורות','chat','telegram group',4,26),
    ('סוכני נדל"ן / מתווכים','פוטנציאל קיים, משמעת מוצרית פחות יציבה','יש כאב ב-follow-up ומהירות תגובה, אבל adoption ומחויבות לתהליך למידה פחות עקביים.','לידים, chaos, מעקב, תיאום ביקורים','להגיב מהר יותר ולעקוב טוב יותר אחרי כל ליד','לסגור יותר עסקאות','אין זמן, chaotic, כבר יש CRM','chat','telegram group',3,24),
    ('כללי','אסור לבנות מוצר רוחבי לפני בחירת workflow אחד','המהלך הנכון הוא לבחור ICP צר ו-workflow כואב אחד, להוכיח ROI, ורק אז להרחיב.','scope רחב מדי, חוסר מיקוד','פתרון narrow עם ROI מדיד','להגיע להכנסות מהר','פיתוי לבנות מוצר כללי','chat','telegram group',5,31),
    ('כללי','מחקרי שוק, קהלים והמלצות צריכים לחיות באתר אחד','צריך Research Hub מרוכז עם טבלאות, deliverables והמלצות שמתעדכן אוטומטית.','מידע מפוזר בצ׳אט','site + DB + daily refresh','לשמר ידע ולהפוך אותו לנכס','תחזוקה, סדר נתונים','chat','telegram group',5,32)
]

recommendations = [
    ('פרילנסרים / מנהלי צוות עצמאיים','offer','הצעת ערך ראשונה','תבנו לעצמכם עובד AI פנימי שמטפל בלידים, הצעות מחיר, בריפים ו-follow-up.','high'),
    ('פרילנסרים / מנהלי צוות עצמאיים','research','שאלות ראיונות שוק','לראיין 10 פרילנסרים על הצעות מחיר, bottlenecks, follow-up והיכן לידים נופלים.','high'),
    ('רואי חשבון / פיננסים','product','MVP ראשון','להתחיל ב-flow של מסמכים חסרים, סיווג, dashboard ומעקב ללקוח.','high'),
    ('רואי חשבון / פיננסים','tech','Human in the loop','לשמור בקרה אנושית, audit trail ו-approval logic כבר מהגרסה הראשונה.','high'),
    ('אנשי HR / גיוס','product','Workflow ראשון','להתחיל ב-resume parsing + scorecard + interview question generation, לא במנוע החלטה אוטונומי.','medium'),
    ('סוכני נדל"ן / מתווכים','landing-page','זווית לדף נחיתה','למכור מהירות תגובה, סדר בלידים ויותר פגישות, לא "AI מגניב".','medium'),
    ('כללי','site','Research Hub','להחזיק repo עם SQLite, JSON exports, אתר סטטי ו-deploy אוטומטי ל-GitHub Pages.','high'),
    ('כללי','strategy','סדר עדיפויות','להוביל עם פרילנסרים, אחריהם רואי חשבון, ורק אחר כך HR ונדל"ן.','high')
]

pages = [
    ('מסמך קהלי יעד מאוחד','report','כללי','מסמך master עם scoring, סדר עדיפויות, זוויות מסר ואתגרים טכנולוגיים.','/pages/audience-master','content/generated/latest-summary.md'),
    ('מחקר שוק לפרילנסרים','research','פרילנסרים / מנהלי צוות עצמאיים','ROI מהיר, pain חד, MVP פשוט יחסית.','/research/freelancers',None),
    ('מחקר שוק לרואי חשבון','research','רואי חשבון / פיננסים','Vertical חזק עם צורך בבקרה ואינטגרציות למסמכים ומערכות פיננסיות.','/research/finance',None),
    ('מחקר שוק ל-HR','research','אנשי HR / גיוס','שוק טוב עם חסמי פרטיות ואישור ארגוני.','/research/hr',None),
    ('מחקר שוק לנדל"ן','research','סוכני נדל"ן / מתווכים','פוטנציאל קיים, אבל adoption פחות יציב.','/research/real-estate',None),
    ('המלצות לדפי נחיתה','recommendation','כללי','מסרי landing page צריכים להיות outcome-first, narrow ICP, עם workflow אחד ברור.','/recommendations/landing-pages',None)
]

integrations = [
    ('פרילנסרים / מנהלי צוות עצמאיים','Gmail','email','high','קריאה, סיכום, draft replies ו-follow-up'),
    ('פרילנסרים / מנהלי צוות עצמאיים','Google Calendar','calendar','medium','תיאומים, משימות, action items'),
    ('פרילנסרים / מנהלי צוות עצמאיים','Notion','workspace','medium','ניהול בריפים וידע'),
    ('פרילנסרים / מנהלי צוות עצמאיים','Airtable / CRM','database','high','pipeline ללידים והצעות'),
    ('רואי חשבון / פיננסים','Google Drive / Dropbox','documents','high','קליטת מסמכים וארגון'),
    ('רואי חשבון / פיננסים','Excel / Google Sheets','spreadsheets','high','ייצוא, בדיקות, reconciliation'),
    ('רואי חשבון / פיננסים','ERP / הנה"ח','finance-system','medium','חיבור לייצואים ממערכות legacy'),
    ('אנשי HR / גיוס','ATS','hr-system','high','resume parsing ו-pipeline'),
    ('אנשי HR / גיוס','Calendar','calendar','medium','תיאום ראיונות'),
    ('אנשי HR / גיוס','Email','email','high','תקשורת עם מועמדים'),
    ('סוכני נדל"ן / מתווכים','WhatsApp','messaging','high','follow-up ולידים'),
    ('סוכני נדל"ן / מתווכים','CRM נדל"ן','crm','high','סטטוס לידים ונכסים'),
    ('סוכני נדל"ן / מתווכים','Google Sheets','spreadsheets','medium','גיבוי ומעקב פשוט')
]

skills = [
    ('פרילנסרים / מנהלי צוות עצמאיים','workflow design','אפיון תהליך intake → proposal → follow-up','high'),
    ('פרילנסרים / מנהלי צוות עצמאיים','prompt engineering','בניית agents/tasks אמינים','high'),
    ('פרילנסרים / מנהלי צוות עצמאיים','email automation','הצעות ומעקב אוטומטי','high'),
    ('רואי חשבון / פיננסים','document processing','סיווג, OCR, חוסרים','high'),
    ('רואי חשבון / פיננסים','human-in-the-loop','בקרה ואישור אנושי','high'),
    ('רואי חשבון / פיננסים','audit trails','מעקב על החלטות ושינויים','high'),
    ('אנשי HR / גיוס','resume parsing','פענוח קו"ח ותיוג','high'),
    ('אנשי HR / גיוס','structured evaluation','scorecards וקריטריונים','high'),
    ('אנשי HR / גיוס','privacy controls','הרשאות, פרטיות, גישה','high'),
    ('סוכני נדל"ן / מתווכים','lead routing','תיעדוף והפצת לידים','high'),
    ('סוכני נדל"ן / מתווכים','messaging automation','follow-up והודעות','high'),
    ('סוכני נדל"ן / מתווכים','matching logic','התאמת נכסים לצרכים','medium')
]

executive_summary = 'יש ארבעה קהלים חזקים, אבל לא כולם שווים באטרקטיביות עסקית. הבחירה הנכונה עכשיו היא להוביל עם פרילנסרים ומנהלי צוות עצמאיים, אחריהם רואי חשבון ופיננסים. הסיבה פשוטה: ROI ברור יותר, פחות חסמי פרטיות ורגולציה, ו-MVP מהיר יותר לבנייה. בכל הסגמנטים אסור להתחיל ממוצר רחב. צריך לבחור ICP צר, workflow אחד כואב, למדוד ROI, ורק אז להרחיב.'

raw_text = '''# Seed notes\n\nהוקם Research Hub ראשוני עם מסד נתונים, טבלאות קהלים, מחקרי שוק, המלצות, אינטגרציות ו-skills.\n\n## סדר עדיפויות\n1. פרילנסרים / מנהלי צוות עצמאיים\n2. רואי חשבון / פיננסים\n3. HR / גיוס\n4. נדל"ן\n\n## עיקרון\nלא לבנות מוצר רוחבי. לבחור workflow כואב אחד לכל סגמנט, להוכיח ROI, ולהרחיב רק אחרי validation.\n'''

summary_md = f'''# Latest Summary\n\n## Executive Summary\n{executive_summary}\n\n## Priority Order\n1. פרילנסרים / מנהלי צוות עצמאיים\n2. רואי חשבון / פיננסים\n3. אנשי HR / גיוס\n4. סוכני נדל"ן / מתווכים\n\n## Core Rule\nStart from one painful workflow, not a broad AI product.\n'''

conn = sqlite3.connect(DB)
conn.executescript(SCHEMA.read_text())
for table in ['audiences','market_research','recommendations','content_pages','integrations','skills_required']:
    conn.execute(f'DELETE FROM {table}')

for a in audiences:
    conn.execute('''INSERT INTO audiences (name,category,short_description,pain_level,wtp_score,decision_speed,targeting_ease,technical_complexity,priority_rank,recommended_offer,recommended_mvp,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                 (a['name'],a['category'],a['short_description'],a['pain_level'],a['wtp_score'],a['decision_speed'],a['targeting_ease'],a['technical_complexity'],a['priority_rank'],a['recommended_offer'],a['recommended_mvp'],a['notes']))

for r in research:
    conn.execute('''INSERT INTO market_research (created_at,updated_at,segment,title,summary,pain_points,value_proposition,buying_motivation,objections,willingness_to_pay,priority_score,source_type,source_ref,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                 (now,now,r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[9],r[10],r[7],r[8],'validated'))

for r in recommendations:
    conn.execute('''INSERT INTO recommendations (created_at,audience_name,type,title,details,priority,status) VALUES (?,?,?,?,?,?,?)''',
                 (now,r[0],r[1],r[2],r[3],r[4],'open'))

for p in pages:
    conn.execute('''INSERT INTO content_pages (created_at,title,kind,audience,summary,url_slug,content_path,status) VALUES (?,?,?,?,?,?,?,?)''',
                 (now,p[0],p[1],p[2],p[3],p[4],p[5],'published'))

for i in integrations:
    conn.execute('''INSERT INTO integrations (audience_name,system_name,system_type,importance,notes,required_for_mvp) VALUES (?,?,?,?,?,?)''',
                 (i[0],i[1],i[2],i[3],i[4],1))

for s in skills:
    conn.execute('''INSERT INTO skills_required (audience_name,skill_name,purpose,priority) VALUES (?,?,?,?)''',
                 (s[0],s[1],s[2],s[3]))

conn.commit()
conn.row_factory = sqlite3.Row

def dump(query, path):
    rows = [dict(r) for r in conn.execute(query).fetchall()]
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    return rows

export_aud = dump('SELECT * FROM audiences ORDER BY priority_rank ASC', EXPORTS / 'audiences.json')
export_res = dump('SELECT * FROM market_research ORDER BY priority_score DESC, id DESC', EXPORTS / 'market_research.json')
export_rec = dump('SELECT * FROM recommendations ORDER BY CASE priority WHEN "high" THEN 1 WHEN "medium" THEN 2 ELSE 3 END, id DESC', EXPORTS / 'recommendations.json')
export_pages = dump('SELECT * FROM content_pages ORDER BY id DESC', EXPORTS / 'pages.json')
dump('SELECT * FROM integrations ORDER BY audience_name, importance DESC', EXPORTS / 'integrations.json')
dump('SELECT * FROM skills_required ORDER BY audience_name, priority DESC', EXPORTS / 'skills_required.json')

summary = {
    'executive_summary': executive_summary,
    'stats': {
        'קהלי יעד': len(export_aud),
        'מחקרים': len(export_res),
        'המלצות': len(export_rec),
        'תוצרים': len(export_pages)
    },
    'top_insights': export_res[:5],
    'top_recommendations': export_rec[:5]
}
(EXPORTS / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
RAW.write_text(raw_text)
GENERATED.write_text(summary_md)
conn.close()
print('Seeded database and exported JSON.')
