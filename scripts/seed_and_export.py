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
        'slug':'freelancers','name':'פרילנסרים / מנהלי צוות עצמאיים','category':'operations','short_description':'עצמאיים וסוכנויות קטנות שמחפשים leverage, אוטומציה ויותר תפוקה ללא גיוס.','pain_level':5,'wtp_score':4,'decision_speed':5,'targeting_ease':4,'technical_complexity':3,'priority_rank':1,
        'recommended_offer':'בנו לעצמכם עובד AI פנימי ללידים, הצעות מחיר, בריפים ו-follow-up','recommended_mvp':'טופס intake + סיכום דרישה + draft להצעת מחיר + follow-up reminders','notes':'קהל ראשון מומלץ. ROI מהיר, מעט חסמי רגולציה.',
        'core_message':'תפסיקו להיות צוואר הבקבוק של העסק שלכם.',
        'landing_angle':'פחות אדמין, יותר תפוקה, יותר רווח בלי להגדיל צוות.',
        'next_step':'לראיין 10 פרילנסרים על process של הצעת מחיר ו-follow-up.'
    },
    {
        'slug':'finance','name':'רואי חשבון / פיננסים','category':'finance','short_description':'משרדי ראיית חשבון ופיננסים עם עומס מסמכים, בדיקות, מעקב וחוסרים.','pain_level':5,'wtp_score':5,'decision_speed':3,'targeting_ease':4,'technical_complexity':4,'priority_rank':2,
        'recommended_offer':'בנו תהליכי AI פנימיים שחוסכים שעות עבודה בלי להחליף את המערכות הקיימות','recommended_mvp':'קליטת מסמכים + סיווג + dashboard לחוסרים + follow-up ללקוחות','notes':'Vertical חזק, אך דורש בקרה, audit trail ו-human-in-the-loop.',
        'core_message':'פחות עבודה שחורה, יותר שליטה, סדר ורווחיות.',
        'landing_angle':'AI כעוזר תפעולי למשרד, לא כתחליף לשיקול דעת מקצועי.',
        'next_step':'למפות תהליך חוסרים / מסמכים / סגירת חודש עם 8-10 משרדים.'
    },
    {
        'slug':'hr','name':'אנשי HR / גיוס','category':'hr','short_description':'צוותי HR וגיוס שרוצים לקצר עבודה תפעולית ולבנות כלי AI פנימיים.','pain_level':4,'wtp_score':4,'decision_speed':3,'targeting_ease':4,'technical_complexity':4,'priority_rank':3,
        'recommended_offer':'בנו כלי AI פנימיים שמקצרים עבודת גיוס ותפעול HR בלי תלות בפיתוח','recommended_mvp':'resume parsing + scorecard + interview questions + feedback summarizer','notes':'טוב, אבל רגיש לפרטיות, bias ואישור ארגוני.',
        'core_message':'שחררו את צוות הגיוס ממשימות שחוזרות על עצמן.',
        'landing_angle':'פחות אדמין, יותר גיוס, יותר candidate experience.',
        'next_step':'לראיין 8 מגייסים ולבחור workflow low-risk ראשון.'
    },
    {
        'slug':'real-estate','name':'סוכני נדל"ן / מתווכים','category':'real-estate','short_description':'מתווכים ומשרדי תיווך שרוצים follow-up מהיר יותר, סדר בלידים ויותר עסקאות.','pain_level':4,'wtp_score':3,'decision_speed':4,'targeting_ease':3,'technical_complexity':3,'priority_rank':4,
        'recommended_offer':'בנו עוזר AI ללידים, תיאומי פגישות ומעקב שוטף','recommended_mvp':'lead intake + prioritization + follow-up + התאמת נכסים בסיסית','notes':'יש כאב, אבל adoption פחות יציב.',
        'core_message':'יותר מהירות תגובה, יותר סדר, יותר עסקאות.',
        'landing_angle':'למכור תוצאה, לא טכנולוגיה. מהירות תגובה ו-follow-up = כסף.',
        'next_step':'לדבר עם 10 מתווכים ולבדוק איפה לידים באמת נופלים.'
    }
]

research = [
    ('freelancers','פרילנסרים / מנהלי צוות עצמאיים','הקהל המהיר ביותר ל-ROI','הקהל הזה חי על זמן, הצעות מחיר, בריפים ו-follow-up, ולכן מבין מהר leverage וערך.','אדמין, bottleneck, proposals, follow-up','לבנות עובד AI פנימי שמקצר זמן ומעלה תפוקה','רוצים להרוויח יותר בלי להגדיל צוות','עסוק מדי, כבר משתמש ב-ChatGPT',5,30),
    ('finance','רואי חשבון / פיננסים','Vertical עם כאב חד ו-WTP גבוה','הכאב ברור, הכסף ברור, והחיסכון בשעות חוזר ישירות לרווחיות המשרד.','מסמכים, חוסרים, checklists, עבודה שחורה','AI כעוזר תפעולי עם בקרה ולא כתחליף לשיקול דעת','לחסוך שעות, לשפר סדר, לשרת יותר לקוחות','רגולציה, דיוק, אמון',5,29),
    ('hr','אנשי HR / גיוס','כאב אמיתי אבל מחזור החלטה איטי יותר','צוותי HR סובלים מעומס תפעולי, אבל נתקלים בפרטיות, bias ותהליכי אישור ארגוניים.','סינון קו"ח, תיאום, פידבק מראיינים','פחות אדמין, יותר גיוס','לקצר זמן גיוס ולהיראות חדשניים','פרטיות, bias, מערכות סגורות',4,26),
    ('real-estate','סוכני נדל"ן / מתווכים','פוטנציאל קיים, משמעת מוצרית פחות יציבה','יש כאב ב-follow-up ומהירות תגובה, אבל adoption ומחויבות לתהליך למידה פחות עקביים.','לידים, chaos, מעקב, תיאום ביקורים','להגיב מהר יותר ולעקוב טוב יותר אחרי כל ליד','לסגור יותר עסקאות','אין זמן, chaotic, כבר יש CRM',3,24),
    ('general','כללי','אסור לבנות מוצר רוחבי לפני בחירת workflow אחד','המהלך הנכון הוא לבחור ICP צר ו-workflow כואב אחד, להוכיח ROI, ורק אז להרחיב.','scope רחב מדי, חוסר מיקוד','פתרון narrow עם ROI מדיד','להגיע להכנסות מהר','פיתוי לבנות מוצר כללי',5,31),
    ('general','כללי','מחקרי שוק, קהלים והמלצות צריכים לחיות באתר אחד','צריך Research Hub מרוכז עם טבלאות, deliverables והמלצות שמתעדכן אוטומטית.','מידע מפוזר בצ׳אט','site + DB + daily refresh','לשמר ידע ולהפוך אותו לנכס','תחזוקה, סדר נתונים',5,32),
    ('freelancers','פרילנסרים / מנהלי צוות עצמאיים','Workflow ראשון מומלץ: ליד → intake → proposal → follow-up','זה workflow עם ROI ברור, קל לדמו, וקל למדוד איפה זמן נשחק ואיפה conversion נופל.','אובדן זמן בין ליד להצעה','מערכת אחת שסוגרת את הפער מליד להצעת מחיר','לשפר response time ולסגור יותר עבודות','"אני כבר עובד ידנית"',5,33),
    ('finance','רואי חשבון / פיננסים','Workflow ראשון מומלץ: מסמכים חסרים → dashboard → follow-up','זה אחד המקומות הכי שוחקים במשרד. אם חוסכים שם שעה ביום, זה רווח מיידי.','מסמכים חסרים, chase, בדיקות ידניות','בקרה וחיסכון בזמן בלי להחליף ERP','להוריד עומס מצוות קיים','"זה רגיש מדי"',5,34),
    ('hr','אנשי HR / גיוס','אין להתחיל במנוע החלטה על מועמדים','צריך להתחיל בכלי עזר תפעולי, לא בכלי שקובע מי מתקדם. זה מפחית סיכון ומגדיל adoption.','סיכון bias, פרטיות, compliance','copilot לתהליך, לא שופט אוטונומי','לקצר זמן עבודה בלי להכניס סיכון כבד','"AI לא יכול להחליט על אנשים"',4,28),
    ('real-estate','סוכני נדל"ן / מתווכים','לנדל"ן צריך mobile-first ו-WhatsApp-first','אם המוצר לא מתיישב על WhatsApp ומהירות תגובה, הוא לא ייכנס לעבודה היומיומית של מתווך.','לידים דרך וואטסאפ, chaotic workflow','follow-up מהיר ותיעוד פשוט','לצמצם לידים שנופלים בין הכיסאות','"אני כבר עובד מהטלפון"',4,27)
]

recommendations = [
    ('פרילנסרים / מנהלי צוות עצמאיים','offer','הצעת ערך ראשונה','תבנו לעצמכם עובד AI פנימי שמטפל בלידים, הצעות מחיר, בריפים ו-follow-up.','high'),
    ('פרילנסרים / מנהלי צוות עצמאיים','research','שאלות ראיונות שוק','לראיין 10 פרילנסרים על הצעות מחיר, bottlenecks, follow-up והיכן לידים נופלים.','high'),
    ('רואי חשבון / פיננסים','product','MVP ראשון','להתחיל ב-flow של מסמכים חסרים, סיווג, dashboard ומעקב ללקוח.','high'),
    ('רואי חשבון / פיננסים','tech','Human in the loop','לשמור בקרה אנושית, audit trail ו-approval logic כבר מהגרסה הראשונה.','high'),
    ('אנשי HR / גיוס','product','Workflow ראשון','להתחיל ב-resume parsing + scorecard + interview question generation, לא במנוע החלטה אוטונומי.','medium'),
    ('סוכני נדל"ן / מתווכים','landing-page','זווית לדף נחיתה','למכור מהירות תגובה, סדר בלידים ויותר פגישות, לא "AI מגניב".','medium'),
    ('כללי','site','Research Hub','להחזיק repo עם SQLite, JSON exports, אתר סטטי ו-deploy אוטומטי ל-GitHub Pages.','high'),
    ('כללי','strategy','סדר עדיפויות','להוביל עם פרילנסרים, אחריהם רואי חשבון, ורק אחר כך HR ונדל"ן.','high'),
    ('כללי','landing-page','מסגרת לדפי נחיתה','כל דף נחיתה חייב להתבסס על outcome אחד, workflow אחד, ו-CTA אחד. לא דף כללי מדי.','high'),
    ('פרילנסרים / מנהלי צוות עצמאיים','landing-page','Headline מומלץ','פרילנסר חכם לא עובד יותר שעות, הוא בונה לעצמו מערכות.','high'),
    ('רואי חשבון / פיננסים','landing-page','Headline מומלץ','פחות עבודה שחורה, יותר שליטה ורווחיות למשרד.','high'),
    ('אנשי HR / גיוס','landing-page','Headline מומלץ','בנו כלי AI פנימיים שמקצרים עבודת גיוס בלי להוסיף כוח אדם.','medium'),
    ('סוכני נדל"ן / מתווכים','product','MVP channel priority','להעדיף flows של WhatsApp + CRM sync + follow-up sequencing.','medium')
]

pages = [
    ('מסמך קהלי יעד מאוחד','report','כללי','מסמך master עם scoring, סדר עדיפויות, זוויות מסר ואתגרים טכנולוגיים.','pages/audience-master.html','content/generated/latest-summary.md'),
    ('מחקר שוק לפרילנסרים','research','פרילנסרים / מנהלי צוות עצמאיים','ROI מהיר, pain חד, MVP פשוט יחסית.','segments/freelancers.html',None),
    ('מחקר שוק לרואי חשבון','research','רואי חשבון / פיננסים','Vertical חזק עם צורך בבקרה ואינטגרציות למסמכים ומערכות פיננסיות.','segments/finance.html',None),
    ('מחקר שוק ל-HR','research','אנשי HR / גיוס','שוק טוב עם חסמי פרטיות ואישור ארגוני.','segments/hr.html',None),
    ('מחקר שוק לנדל"ן','research','סוכני נדל"ן / מתווכים','פוטנציאל קיים, אבל adoption פחות יציב.','segments/real-estate.html',None),
    ('המלצות לדפי נחיתה','recommendation','כללי','מסרי landing page צריכים להיות outcome-first, narrow ICP, עם workflow אחד ברור.','landing-pages.html',None),
    ('מחקר מתחרים ראשוני','research','כללי','מיפוי פתרונות חלופיים: SaaS, automation tools, agencies, no-code.','competitors.html',None),
    ('הזדמנויות מוצר','product','כללי','רשימת product opportunities לפי סגמנטים ו-workflows.','opportunities.html',None)
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

competitors = [
    {'segment':'פרילנסרים','competitor':'Zapier / Make','type':'automation','strength':'אוטומציה רחבה','weakness':'לא package אנכי לבעיה עסקית אחת','opportunity':'למכור outcome ולא רק automation builder'},
    {'segment':'פרילנסרים','competitor':'ChatGPT','type':'general AI','strength':'זמין ומוכר','weakness':'לא workflow system','opportunity':'להמיר שיחות לכלי עבודה קבועים'},
    {'segment':'פיננסים','competitor':'משרדי אוטומציה / BI','type':'services','strength':'פתרון מותאם','weakness':'יקר ואיטי','opportunity':'פתרון internal-first, מהיר וזול יותר'},
    {'segment':'HR','competitor':'ATS קיימים','type':'platform','strength':'תשתית קיימת','weakness':'חסרים שכבת AI גמישה מותאמת צוות','opportunity':'copilot מעל ATS'},
    {'segment':'נדל"ן','competitor':'CRM נדל"ן','type':'crm','strength':'מנהלים pipeline','weakness':'חלשים ב-follow-up אינטליגנטי','opportunity':'WhatsApp-first follow-up assistant'}
]

opportunities = [
    {'segment':'פרילנסרים / מנהלי צוות עצמאיים','workflow':'Lead to Proposal','problem':'לידים נמרחים בין שיחה להצעה','solution':'agent שמרכז brief, מייצר draft להצעה, ועוקב עד סגירה','priority':'high'},
    {'segment':'רואי חשבון / פיננסים','workflow':'Missing Documents','problem':'ריצה ידנית אחרי מסמכים חסרים','solution':'dashboard + reminders + classification + exceptions','priority':'high'},
    {'segment':'אנשי HR / גיוס','workflow':'Interview Ops','problem':'תיאום, שאלות, פידבק מפוזרים','solution':'coordinator שמסכם קו"ח, בונה שאלות ומרכז feedback','priority':'medium'},
    {'segment':'סוכני נדל"ן / מתווכים','workflow':'Lead Follow-Up','problem':'לידים נופלים בין הודעות ופגישות','solution':'assistant לוואטסאפ, CRM sync, ותיעדוף follow-up','priority':'medium'}
]

executive_summary = 'יש ארבעה קהלים חזקים, אבל לא כולם שווים באטרקטיביות עסקית. הבחירה הנכונה עכשיו היא להוביל עם פרילנסרים ומנהלי צוות עצמאיים, אחריהם רואי חשבון ופיננסים. הסיבה פשוטה: ROI ברור יותר, פחות חסמי פרטיות ורגולציה, ו-MVP מהיר יותר לבנייה. בכל הסגמנטים אסור להתחיל ממוצר רחב. צריך לבחור ICP צר, workflow אחד כואב, למדוד ROI, ורק אז להרחיב.'

raw_text = '''# Seed notes\n\nהורחב Research Hub לאתר multi-page עם עמודי סגמנט, מחקר מתחרים, הזדמנויות מוצר והמלצות לדפי נחיתה.\n\n## סדר עדיפויות\n1. פרילנסרים / מנהלי צוות עצמאיים\n2. רואי חשבון / פיננסים\n3. HR / גיוס\n4. נדל"ן\n\n## עיקרון\nלא לבנות מוצר רוחבי. לבחור workflow כואב אחד לכל סגמנט, להוכיח ROI, ולהרחיב רק אחרי validation.\n'''

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
                 (now,now,r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],'chat','telegram group','validated'))

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
export_int = dump('SELECT * FROM integrations ORDER BY audience_name, importance DESC', EXPORTS / 'integrations.json')
export_sk = dump('SELECT * FROM skills_required ORDER BY audience_name, priority DESC', EXPORTS / 'skills_required.json')
(EXPORTS / 'competitors.json').write_text(json.dumps(competitors, ensure_ascii=False, indent=2))
(EXPORTS / 'opportunities.json').write_text(json.dumps(opportunities, ensure_ascii=False, indent=2))
(EXPORTS / 'segment_profiles.json').write_text(json.dumps(audiences, ensure_ascii=False, indent=2))

summary = {
    'executive_summary': executive_summary,
    'stats': {
        'קהלי יעד': len(export_aud),
        'מחקרים': len(export_res),
        'המלצות': len(export_rec),
        'תוצרים': len(export_pages),
        'אינטגרציות': len(export_int),
        'Skills': len(export_sk)
    },
    'top_insights': export_res[:6],
    'top_recommendations': export_rec[:6],
    'priority_order': [a['name'] for a in audiences]
}
(EXPORTS / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
RAW.write_text(raw_text)
GENERATED.write_text(summary_md)
conn.close()
print('Seeded expanded database and exported JSON.')
