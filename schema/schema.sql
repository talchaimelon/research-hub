PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS audiences (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  category TEXT,
  short_description TEXT,
  pain_level INTEGER,
  wtp_score INTEGER,
  decision_speed INTEGER,
  targeting_ease INTEGER,
  technical_complexity INTEGER,
  priority_rank INTEGER,
  recommended_offer TEXT,
  recommended_mvp TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS market_research (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  segment TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  pain_points TEXT,
  value_proposition TEXT,
  buying_motivation TEXT,
  objections TEXT,
  willingness_to_pay INTEGER,
  priority_score INTEGER,
  source_type TEXT,
  source_ref TEXT,
  status TEXT DEFAULT 'validated'
);

CREATE TABLE IF NOT EXISTS recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  audience_name TEXT,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  details TEXT NOT NULL,
  priority TEXT,
  owner TEXT DEFAULT 'Elon',
  status TEXT DEFAULT 'open'
);

CREATE TABLE IF NOT EXISTS content_pages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  title TEXT NOT NULL,
  kind TEXT NOT NULL,
  audience TEXT,
  summary TEXT,
  url_slug TEXT,
  content_path TEXT,
  status TEXT DEFAULT 'published'
);

CREATE TABLE IF NOT EXISTS integrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  audience_name TEXT NOT NULL,
  system_name TEXT NOT NULL,
  system_type TEXT,
  required_for_mvp INTEGER DEFAULT 1,
  importance TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS skills_required (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  audience_name TEXT NOT NULL,
  skill_name TEXT NOT NULL,
  purpose TEXT,
  priority TEXT
);
