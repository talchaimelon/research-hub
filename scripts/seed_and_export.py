import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'research.db'
SCHEMA = ROOT / 'schema' / 'schema.sql'
EXPORTS = ROOT / 'data' / 'exports'
RAW = ROOT / 'content' / 'raw' / '2026-04-19-seed.md'
GENERATED = ROOT / 'content' / 'generated' / 'latest-summary.md'
now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

audiences = [
    {
        'slug':'freelancers','name':'פרילנסרים / מנהלי צוות עצמאיים','category':'operations','short_description':'עצמאיים וסוכנויות קטנות שמחפשים leverage, אוטומציה ויותר תפוקה ללא גיוס.','pain_level':5,'wtp_score':4,'decision_speed':5,'targeting_ease':4,'technical_complexity':3,'priority_rank':1,
        'recommended_offer':'בנו לעצמכם עובד AI פנימי ללידים, הצעות מחיר, בריפים ו-follow-up','recommended_mvp':'טופס intake + סיכום דרישה + draft להצעת מחיר + follow-up reminders','notes':'קהל ראשון מומלץ. ROI מהיר, מעט חסמי רגולציה.','status':'approved',
        'core_message':'תפסיקו להיות צוואר הבקבוק של העסק שלכם.','landing_angle':'פחות אדמין, יותר תפוקה, יותר רווח בלי להגדיל צוות.','next_step':'לראיין 10 פרילנסרים על process של הצעת מחיר ו-follow-up.'
    },
    {
        'slug':'finance','name':'רואי חשבון / פיננסים','category':'finance','short_description':'משרדי ראיית חשבון ופיננסים עם עומס מסמכים, בדיקות, מעקב וחוסרים.','pain_level':5,'wtp_score':5,'decision_speed':3,'targeting_ease':4,'technical_complexity':4,'priority_rank':2,
        'recommended_offer':'בנו תהליכי AI פנימיים שחוסכים שעות עבודה בלי להחליף את המערכות הקיימות','recommended_mvp':'קליטת מסמכים + סיווג + dashboard לחוסרים + follow-up ללקוחות','notes':'Vertical חזק, אך דורש בקרה, audit trail ו-human-in-the-loop.','status':'approved',
        'core_message':'פחות עבודה שחורה, יותר שליטה, סדר ורווחיות.','landing_angle':'AI כעוזר תפעולי למשרד, לא כתחליף לשיקול דעת מקצועי.','next_step':'למפות תהליך חוסרים / מסמכים / סגירת חודש עם 8-10 משרדים.'
    },
    {
        'slug':'hr','name':'אנשי HR / גיוס','category':'hr','short_description':'צוותי HR וגיוס שרוצים לקצר עבודה תפעולית ולבנות כלי AI פנימיים.','pain_level':4,'wtp_score':4,'decision_speed':3,'targeting_ease':4,'technical_complexity':4,'priority_rank':3,
        'recommended_offer':'בנו כלי AI פנימיים שמקצרים עבודת גיוס ותפעול HR בלי תלות בפיתוח','recommended_mvp':'resume parsing + scorecard + interview questions + feedback summarizer','notes':'טוב, אבל רגיש לפרטיות, bias ואישור ארגוני.','status':'approved',
        'core_message':'שחררו את צוות הגיוס ממשימות שחוזרות על עצמן.','landing_angle':'פחות אדמין, יותר גיוס, יותר candidate experience.','next_step':'לראיין 8 מגייסים ולבחור workflow low-risk ראשון.'
    },
    {
        'slug':'real-estate','name':'סוכני נדל"ן / מתווכים','category':'real-estate','short_description':'מתווכים ומשרדי תיווך שרוצים follow-up מהיר יותר, סדר בלידים ויותר עסקאות.','pain_level':4,'wtp_score':3,'decision_speed':4,'targeting_ease':3,'technical_complexity':3,'priority_rank':4,
        'recommended_offer':'בנו עוזר AI ללידים, תיאומי פגישות ומעקב שוטף','recommended_mvp':'lead intake + prioritization + follow-up + התאמת נכסים בסיסית','notes':'יש כאב, אבל adoption פחות יציב.','status':'approved',
        'core_message':'יותר מהירות תגובה, יותר סדר, יותר עסקאות.','landing_angle':'למכור תוצאה, לא טכנולוגיה. מהירות תגובה ו-follow-up = כסף.','next_step':'לדבר עם 10 מתווכים ולבדוק איפה לידים באמת נופלים.'
    },
    {
        'slug':'lawyers','name':'עורכי דין / משרדי עורכי דין','category':'legal','short_description':'משרדים ועורכי דין שמחפשים לחסוך זמן על מסמכים, intake, תיאומים ומעקב.','pain_level':5,'wtp_score':5,'decision_speed':3,'targeting_ease':4,'technical_complexity':4,'priority_rank':5,
        'recommended_offer':'בנו כלי AI פנימיים למשרד שחוסכים זמן על intake, מסמכים ותקשורת ראשונית עם לקוחות','recommended_mvp':'client intake + סיכום שיחות + טיוטות מסמכים + checklist לתיקים','notes':'קהל חזק מאוד, value כספי ברור, אבל דורש זהירות משפטית וניסוח אחראי.','status':'pending_approval',
        'core_message':'פחות זמן על עבודה שחוזרת על עצמה, יותר זמן על עבודה משפטית שמכניסה כסף.','landing_angle':'לא למכור "AI חכם", למכור שליטה, חיסכון בזמן וזרימת עבודה למשרד.','next_step':'לאשר סגמנט, ואז למפות workflow ראשון: intake / draft / follow-up.'
    },
    {
        'slug':'accountants-extended','name':'הנהלת חשבונות / בק אופיס פיננסי','category':'finance-ops','short_description':'מנהלות חשבונות, back office פיננסי וצוותי תפעול כספי עם עומס תיעוד ומעקב.','pain_level':5,'wtp_score':4,'decision_speed':4,'targeting_ease':4,'technical_complexity':3,'priority_rank':6,
        'recommended_offer':'כלי AI לתיעוד, חוסרים, מעקב וסגירת קצוות פיננסיים יומיומיים','recommended_mvp':'document collection + reminders + reconciliations checklist','notes':'קרוב לפיננסים, אבל תת-סגמנט עם pain אופרטיבי חד יותר.','status':'pending_approval',
        'core_message':'לסגור קצוות פיננסיים מהר, בלי לרדוף ידנית אחרי כל מסמך.','landing_angle':'למכור שקט תפעולי, סדר ומהירות, לא אוטומציה לשם אוטומציה.','next_step':'לאשר אם להחזיק אותו כסגמנט עצמאי או כתת-סגמנט של פיננסים.'
    }
]

research = [
    ('freelancers','פרילנסרים / מנהלי צוות עצמאיים','הקהל המהיר ביותר ל-ROI','הקהל הזה חי על זמן, הצעות מחיר, בריפים ו-follow-up, ולכן מבין מהר leverage וערך.','אדמין, bottleneck, proposals, follow-up','לבנות עובד AI פנימי שמקצר זמן ומעלה תפוקה','רוצים להרוויח יותר בלי להגדיל צוות','עסוק מדי, כבר משתמש ב-ChatGPT',5,30,'approved'),
    ('finance','רואי חשבון / פיננסים','Vertical עם כאב חד ו-WTP גבוה','הכאב ברור, הכסף ברור, והחיסכון בשעות חוזר ישירות לרווחיות המשרד.','מסמכים, חוסרים, checklists, עבודה שחורה','AI כעוזר תפעולי עם בקרה ולא כתחליף לשיקול דעת','לחסוך שעות, לשפר סדר, לשרת יותר לקוחות','רגולציה, דיוק, אמון',5,29,'approved'),
    ('hr','אנשי HR / גיוס','כאב אמיתי אבל מחזור החלטה איטי יותר','צוותי HR סובלים מעומס תפעולי, אבל נתקלים בפרטיות, bias ותהליכי אישור ארגוניים.','סינון קו"ח, תיאום, פידבק מראיינים','פחות אדמין, יותר גיוס','לקצר זמן גיוס ולהיראות חדשניים','פרטיות, bias, מערכות סגורות',4,26,'approved'),
    ('real-estate','סוכני נדל"ן / מתווכים','פוטנציאל קיים, משמעת מוצרית פחות יציבה','יש כאב ב-follow-up ומהירות תגובה, אבל adoption ומחויבות לתהליך למידה פחות עקביים.','לידים, chaos, מעקב, תיאום ביקורים','להגיב מהר יותר ולעקוב טוב יותר אחרי כל ליד','לסגור יותר עסקאות','אין זמן, chaotic, כבר יש CRM',3,24,'approved'),
    ('general','כללי','אסור לבנות מוצר רוחבי לפני בחירת workflow אחד','המהלך הנכון הוא לבחור ICP צר ו-workflow כואב אחד, להוכיח ROI, ורק אז להרחיב.','scope רחב מדי, חוסר מיקוד','פתרון narrow עם ROI מדיד','להגיע להכנסות מהר','פיתוי לבנות מוצר כללי',5,31,'approved'),
    ('general','כללי','מחקרי שוק, קהלים והמלצות צריכים לחיות באתר אחד','צריך Research Hub מרוכז עם טבלאות, deliverables והמלצות שמתעדכן אוטומטית.','מידע מפוזר בצ׳אט','site + DB + daily refresh','לשמר ידע ולהפוך אותו לנכס','תחזוקה, סדר נתונים',5,32,'approved'),
    ('freelancers','פרילנסרים / מנהלי צוות עצמאיים','Workflow ראשון מומלץ: ליד → intake → proposal → follow-up','זה workflow עם ROI ברור, קל לדמו, וקל למדוד איפה זמן נשחק ואיפה conversion נופל.','אובדן זמן בין ליד להצעה','מערכת אחת שסוגרת את הפער מליד להצעת מחיר','לשפר response time ולסגור יותר עבודות','"אני כבר עובד ידנית"',5,33,'approved'),
    ('finance','רואי חשבון / פיננסים','Workflow ראשון מומלץ: מסמכים חסרים → dashboard → follow-up','זה אחד המקומות הכי שוחקים במשרד. אם חוסכים שם שעה ביום, זה רווח מיידי.','מסמכים חסרים, chase, בדיקות ידניות','בקרה וחיסכון בזמן בלי להחליף ERP','להוריד עומס מצוות קיים','"זה רגיש מדי"',5,34,'approved'),
    ('hr','אנשי HR / גיוס','אין להתחיל במנוע החלטה על מועמדים','צריך להתחיל בכלי עזר תפעולי, לא בכלי שקובע מי מתקדם. זה מפחית סיכון ומגדיל adoption.','סיכון bias, פרטיות, compliance','copilot לתהליך, לא שופט אוטונומי','לקצר זמן עבודה בלי להכניס סיכון כבד','"AI לא יכול להחליט על אנשים"',4,28,'approved'),
    ('real-estate','סוכני נדל"ן / מתווכים','לנדל"ן צריך mobile-first ו-WhatsApp-first','אם המוצר לא מתיישב על WhatsApp ומהירות תגובה, הוא לא ייכנס לעבודה היומיומית של מתווך.','לידים דרך וואטסאפ, chaotic workflow','follow-up מהיר ותיעוד פשוט','לצמצם לידים שנופלים בין הכיסאות','"אני כבר עובד מהטלפון"',4,27,'approved'),
    ('lawyers','עורכי דין / משרדי עורכי דין','הזדמנות חזקה, אבל רק עם מיצוב אחראי','לעורכי דין יש willingness to pay גבוה, pain חד, וערך ברור, אבל אסור למכור אוטומציה כאילו היא מחליפה שיקול דעת משפטי.','drafts, intake, מסמכים, תיאום, follow-up','להציג AI כמאיץ עבודה פנימי עם בקרה אנושית','לחסוך שעות על פרה-ליגל ותפעול','דיוק, אחריות משפטית, אתיקה',5,35,'pending_approval'),
    ('accountants-extended','הנהלת חשבונות / בק אופיס פיננסי','תת-סגמנט עם pain תפעולי חד','יש כאן pain יומיומי של חוסרים, מרדף, תיעוד וסגירת קצוות, לפעמים חד יותר ממסר CFO קלאסי.','מסמכים, חוסרים, reminders, reconciliation','למכור סגירת קצוות ולא חזון AI גדול','להקל על עומס שוטף','"יש לנו כבר מערכת"',4,30,'pending_approval')
]

recommendations = [
    ('פרילנסרים / מנהלי צוות עצמאיים','offer','הצעת ערך ראשונה','תבנו לעצמכם עובד AI פנימי שמטפל בלידים, הצעות מחיר, בריפים ו-follow-up.','high','approved'),
    ('פרילנסרים / מנהלי צוות עצמאיים','research','שאלות ראיונות שוק','לראיין 10 פרילנסרים על הצעות מחיר, bottlenecks, follow-up והיכן לידים נופלים.','high','approved'),
    ('רואי חשבון / פיננסים','product','MVP ראשון','להתחיל ב-flow של מסמכים חסרים, סיווג, dashboard ומעקב ללקוח.','high','approved'),
    ('רואי חשבון / פיננסים','tech','Human in the loop','לשמור בקרה אנושית, audit trail ו-approval logic כבר מהגרסה הראשונה.','high','approved'),
    ('אנשי HR / גיוס','product','Workflow ראשון','להתחיל ב-resume parsing + scorecard + interview question generation, לא במנוע החלטה אוטונומי.','medium','approved'),
    ('סוכני נדל"ן / מתווכים','landing-page','זווית לדף נחיתה','למכור מהירות תגובה, סדר בלידים ויותר פגישות, לא "AI מגניב".','medium','approved'),
    ('כללי','site','Research Hub','להחזיק repo עם SQLite, JSON exports, אתר סטטי ו-deploy אוטומטי ל-GitHub Pages.','high','approved'),
    ('כללי','strategy','סדר עדיפויות','להוביל עם פרילנסרים, אחריהם רואי חשבון, ורק אחר כך HR ונדל"ן.','high','approved'),
    ('כללי','landing-page','מסגרת לדפי נחיתה','כל דף נחיתה חייב להתבסס על outcome אחד, workflow אחד, ו-CTA אחד. לא דף כללי מדי.','high','approved'),
    ('פרילנסרים / מנהלי צוות עצמאיים','landing-page','Headline מומלץ','פרילנסר חכם לא עובד יותר שעות, הוא בונה לעצמו מערכות.','high','approved'),
    ('רואי חשבון / פיננסים','landing-page','Headline מומלץ','פחות עבודה שחורה, יותר שליטה ורווחיות למשרד.','high','approved'),
    ('אנשי HR / גיוס','landing-page','Headline מומלץ','בנו כלי AI פנימיים שמקצרים עבודת גיוס בלי להוסיף כוח אדם.','medium','approved'),
    ('סוכני נדל"ן / מתווכים','product','MVP channel priority','להעדיף flows של WhatsApp + CRM sync + follow-up sequencing.','medium','approved'),
    ('עורכי דין / משרדי עורכי דין','strategy','Positioning rule','למסגר את הסגמנט המשפטי כ-workflow acceleration עם review אנושי, לא כאוטומציה שמחליפה עורך דין.','high','pending_approval'),
    ('הנהלת חשבונות / בק אופיס פיננסי','strategy','Segmentation decision','להחליט אם זה תת-סגמנט נפרד או שכבה בתוך פיננסים. כרגע כדאי לשמור אותו גלוי באתר כ-pending.','medium','pending_approval')
]

pages = [
    ('מסמך קהלי יעד מאוחד','report','כללי','מסמך master עם scoring, סדר עדיפויות, זוויות מסר ואתגרים טכנולוגיים.','pages/audience-master.html','content/generated/latest-summary.md','approved'),
    ('מחקר שוק לפרילנסרים','research','פרילנסרים / מנהלי צוות עצמאיים','ROI מהיר, pain חד, MVP פשוט יחסית.','segments/freelancers.html',None,'approved'),
    ('מחקר שוק לרואי חשבון','research','רואי חשבון / פיננסים','Vertical חזק עם צורך בבקרה ואינטגרציות למסמכים ומערכות פיננסיות.','segments/finance.html',None,'approved'),
    ('מחקר שוק ל-HR','research','אנשי HR / גיוס','שוק טוב עם חסמי פרטיות ואישור ארגוני.','segments/hr.html',None,'approved'),
    ('מחקר שוק לנדל"ן','research','סוכני נדל"ן / מתווכים','פוטנציאל קיים, אבל adoption פחות יציב.','segments/real-estate.html',None,'approved'),
    ('מחקר שוק לעורכי דין','research','עורכי דין / משרדי עורכי דין','קהל עם willingness to pay גבוה ורגישות גבוהה לניסוח ולאחריות.','segments/lawyers.html',None,'pending_approval'),
    ('מחקר שוק להנהלת חשבונות','research','הנהלת חשבונות / בק אופיס פיננסי','תת-סגמנט עם pain תפעולי חד סביב חוסרים, מסמכים ומעקב.','segments/accountants-extended.html',None,'pending_approval'),
    ('המלצות לדפי נחיתה','recommendation','כללי','מסרי landing page צריכים להיות outcome-first, narrow ICP, עם workflow אחד ברור.','landing-pages.html',None,'approved'),
    ('מחקר מתחרים ראשוני','research','כללי','מיפוי פתרונות חלופיים: SaaS, automation tools, agencies, no-code.','competitors.html',None,'approved'),
    ('הזדמנויות מוצר','product','כללי','רשימת product opportunities לפי סגמנטים ו-workflows.','opportunities.html',None,'approved')
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
    ('סוכני נדל"ן / מתווכים','Google Sheets','spreadsheets','medium','גיבוי ומעקב פשוט'),
    ('עורכי דין / משרדי עורכי דין','Gmail / Outlook','email','high','תקשורת לקוחות, intake, follow-up'),
    ('עורכי דין / משרדי עורכי דין','Google Drive / DMS','documents','high','מסמכים, תיוג, טיוטות, checklists'),
    ('עורכי דין / משרדי עורכי דין','Calendar','calendar','medium','פגישות, deadlines, follow-up'),
    ('הנהלת חשבונות / בק אופיס פיננסי','Sheets / Excel','spreadsheets','high','מעקב חוסרים, reconciliation, checklists'),
    ('הנהלת חשבונות / בק אופיס פיננסי','Drive / Email','documents','high','מסמכים ו-reminders')
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
    ('סוכני נדל"ן / מתווכים','matching logic','התאמת נכסים לצרכים','medium'),
    ('עורכי דין / משרדי עורכי דין','document drafting guardrails','טיוטות עם review אנושי','high'),
    ('עורכי דין / משרדי עורכי דין','client intake automation','קליטת לקוחות ושיחות ראשוניות','high'),
    ('הנהלת חשבונות / בק אופיס פיננסי','document chase workflows','מרדף חוסרים ותיעוד','high')
]

competitors = [
    {'segment':'פרילנסרים','competitor':'Zapier / Make','type':'automation','strength':'אוטומציה רחבה','weakness':'לא package אנכי לבעיה עסקית אחת','opportunity':'למכור outcome ולא רק automation builder'},
    {'segment':'פרילנסרים','competitor':'ChatGPT','type':'general AI','strength':'זמין ומוכר','weakness':'לא workflow system','opportunity':'להמיר שיחות לכלי עבודה קבועים'},
    {'segment':'פיננסים','competitor':'משרדי אוטומציה / BI','type':'services','strength':'פתרון מותאם','weakness':'יקר ואיטי','opportunity':'פתרון internal-first, מהיר וזול יותר'},
    {'segment':'HR','competitor':'ATS קיימים','type':'platform','strength':'תשתית קיימת','weakness':'חסרים שכבת AI גמישה מותאמת צוות','opportunity':'copilot מעל ATS'},
    {'segment':'נדל"ן','competitor':'CRM נדל"ן','type':'crm','strength':'מנהלים pipeline','weakness':'חלשים ב-follow-up אינטליגנטי','opportunity':'WhatsApp-first follow-up assistant'},
    {'segment':'משפטי','competitor':'LegalTech point solutions','type':'legaltech','strength':'פתרונות נישתיים למסמכים','weakness':'לא flow מלא של משרד קטן/בינוני','opportunity':'להוביל עם workflow orchestration ולא רק drafting'}
]

opportunities = [
    {'segment':'פרילנסרים / מנהלי צוות עצמאיים','workflow':'Lead to Proposal','problem':'לידים נמרחים בין שיחה להצעה','solution':'agent שמרכז brief, מייצר draft להצעה, ועוקב עד סגירה','priority':'high','status':'approved'},
    {'segment':'רואי חשבון / פיננסים','workflow':'Missing Documents','problem':'ריצה ידנית אחרי מסמכים חסרים','solution':'dashboard + reminders + classification + exceptions','priority':'high','status':'approved'},
    {'segment':'אנשי HR / גיוס','workflow':'Interview Ops','problem':'תיאום, שאלות, פידבק מפוזרים','solution':'coordinator שמסכם קו"ח, בונה שאלות ומרכז feedback','priority':'medium','status':'approved'},
    {'segment':'סוכני נדל"ן / מתווכים','workflow':'Lead Follow-Up','problem':'לידים נופלים בין הודעות ופגישות','solution':'assistant לוואטסאפ, CRM sync, ותיעדוף follow-up','priority':'medium','status':'approved'},
    {'segment':'עורכי דין / משרדי עורכי דין','workflow':'Client Intake + Drafting','problem':'אובדן זמן על intake, סיכום שיחות וטיוטות ראשוניות','solution':'flow פנימי עם intake, summarization, draft ו-review אנושי','priority':'high','status':'pending_approval'},
    {'segment':'הנהלת חשבונות / בק אופיס פיננסי','workflow':'Daily Missing Docs Ops','problem':'הרבה chase ועבודה שחוזרת על עצמה סביב מסמכים','solution':'reminders, checklist וסטטוס פתוח לכל לקוח','priority':'medium','status':'pending_approval'}
]

executive_summary = 'האתר מחזיק עכשיו גם את הקהלים שאושרו וגם את אלה שממתינים לאישור, כדי שלא נאבד כיוונים באמצע. כרגע הסדר המומלץ נשאר: פרילנסרים, פיננסים, HR, נדל"ן. בנוסף נוספו סגמנטים בהמתנה: עורכי דין והנהלת חשבונות. כלל העל נשאר זהה: לא בונים מוצר רחב, בוחרים workflow אחד כואב, מוכיחים ROI, ורק אז מרחיבים.'

raw_text = '''# Seed notes\n\nהורחב Research Hub כך שיכלול גם סגמנטים ומחקרים בסטטוס pending approval.\n\n## Approved\n- פרילנסרים\n- רואי חשבון / פיננסים\n- HR / גיוס\n- נדל"ן / מתווכים\n\n## Pending approval\n- עורכי דין / משרדי עורכי דין\n- הנהלת חשבונות / בק אופיס פיננסי\n'''

summary_md = f'''# Latest Summary\n\n## Executive Summary\n{executive_summary}\n\n## Approved\n- פרילנסרים / מנהלי צוות עצמאיים\n- רואי חשבון / פיננסים\n- אנשי HR / גיוס\n- סוכני נדל"ן / מתווכים\n\n## Pending approval\n- עורכי דין / משרדי עורכי דין\n- הנהלת חשבונות / בק אופיס פיננסי\n'''

conn = sqlite3.connect(DB)
conn.executescript(SCHEMA.read_text())
for table in ['audiences','market_research','recommendations','content_pages','integrations','skills_required']:
    conn.execute(f'DELETE FROM {table}')

for a in audiences:
    conn.execute('''INSERT INTO audiences (name,category,short_description,pain_level,wtp_score,decision_speed,targeting_ease,technical_complexity,priority_rank,recommended_offer,recommended_mvp,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                 (a['name'],a['category'],a['short_description'],a['pain_level'],a['wtp_score'],a['decision_speed'],a['targeting_ease'],a['technical_complexity'],a['priority_rank'],a['recommended_offer'],a['recommended_mvp'],a['notes']))

for r in research:
    conn.execute('''INSERT INTO market_research (created_at,updated_at,segment,title,summary,pain_points,value_proposition,buying_motivation,objections,willingness_to_pay,priority_score,source_type,source_ref,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                 (now,now,r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],'chat','telegram group',r[10]))

for r in recommendations:
    conn.execute('''INSERT INTO recommendations (created_at,audience_name,type,title,details,priority,status) VALUES (?,?,?,?,?,?,?)''',
                 (now,r[0],r[1],r[2],r[3],r[4],r[5]))

for p in pages:
    conn.execute('''INSERT INTO content_pages (created_at,title,kind,audience,summary,url_slug,content_path,status) VALUES (?,?,?,?,?,?,?,?)''',
                 (now,p[0],p[1],p[2],p[3],p[4],p[5],p[6]))

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
    'priority_order': [a['name'] for a in audiences[:4]],
    'pending_segments': [a['name'] for a in audiences if a['status'] == 'pending_approval']
}
(EXPORTS / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
RAW.write_text(raw_text)
GENERATED.write_text(summary_md)
conn.close()
print('Seeded expanded database and exported JSON with pending segments.')
