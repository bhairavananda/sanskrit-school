#!/usr/bin/env python3
"""Build a single-page web UI for tantrikk sanskrit from all markdown files."""

import os
import json
import re

SCHOOL_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(SCHOOL_DIR, "index.html")

# ── Collect lesson stages ──

stages = []

overview_path = os.path.join(SCHOOL_DIR, "00-overview.md")
if os.path.exists(overview_path):
    with open(overview_path, "r") as f:
        stages.append({
            "id": "00-overview", "number": 0,
            "title": "Overview", "subtitle": "From Beginner to Avadhani",
            "files": {"overview": f.read()}, "tabs": ["overview"]
        })

stage_meta = {
    "01-nama": ("Nama", "Basic Vocabulary"),
    "02-guna": ("Guna", "Adjectives"),
    "03-rupa": ("Rupa", "Case / Number / Gender"),
    "04-kriya": ("Kriya", "Verbs"),
    "05-karaka": ("Karaka", "Semantic Relations"),
    "06-sambodhana": ("Sambodhana", "Direct Address"),
    "07-dhatu": ("Dhatu", "Roots & Upasargas"),
    "08-paryaya": ("Paryaya", "Synonyms"),
    "09-samasa": ("Samasa", "Compounds"),
    "10-vakya": ("Vakya", "Free Composition"),
    "11-bhava": ("Bhava", "Emotional Vocabulary"),
    "12-stotra-i": ("Stotra I", "Accusative Constructions"),
    "13-stotra-ii": ("Stotra II", "Varied Cases"),
    "14-prarthana": ("Prarthana", "Requests & Imperatives"),
    "15-katha": ("Katha", "Narration"),
    "16-chandas-i": ("Chandas I", "Syllables"),
    "17-chandas-ii": ("Chandas II", "Anustubh"),
    "18-chandas-iii": ("Chandas III", "Multiple Meters"),
    "19-paryaya-chandas": ("Paryaya-Chandas", "Lexical Flexibility"),
    "20-alankara": ("Alankara", "Poetic Ornament"),
    "21-rasa": ("Rasa", "Emotional Aesthetics"),
    "22-darshana": ("Darshana", "Philosophical Expression"),
    "23-samasyapurana": ("Samasyapurana", "Backwards Composition"),
    "24-dattapadi": ("Dattapadi", "Forced Vocabulary"),
    "25-nishiddhakshari": ("Nishiddhakshari", "Inhibition"),
    "26-citra-kavya": ("Citra-kavya", "Stacked Constraints"),
    "27-dharana-i": ("Dharana I", "Interrupted Memory"),
    "28-dharana-ii": ("Dharana II", "Associative Retrieval"),
    "29-aprastuta-prasanga": ("Aprastuta-prasanga", "Wit & Context Switching"),
    "30-multi-devata": ("Multi-devata", "Rapid Semantic Switching"),
    "31-ashtavadhana": ("Ashtavadhana", "Integrated Attention"),
    "32-avadhana-seva": ("Avadhana-seva", "Mastery"),
}

file_labels = {
    "theory": "Theory", "reference": "Reference",
    "workbook-questions": "Questions", "workbook-answers": "Answers",
}

for dirname, (title, subtitle) in stage_meta.items():
    stage_dir = os.path.join(SCHOOL_DIR, dirname)
    if not os.path.isdir(stage_dir):
        continue
    num = int(dirname.split("-")[0])
    files = {}
    tabs = []
    for fname in ["theory", "reference", "workbook-questions", "workbook-answers"]:
        fpath = os.path.join(stage_dir, f"{fname}.md")
        if os.path.exists(fpath):
            with open(fpath, "r") as f:
                files[fname] = f.read()
                tabs.append(fname)
    stages.append({"id": dirname, "number": num, "title": title,
                    "subtitle": subtitle, "files": files, "tabs": tabs})

stages.sort(key=lambda s: s["number"])

# ── Collect vocab files ──

vocab_dir = os.path.join(SCHOOL_DIR, "vocab")
vocab_categories = []

if os.path.isdir(vocab_dir):
    vocab_meta = {
        "00-index": ("Index", "Source texts & overview"),
        "01-goddess-names": ("Goddess Names", "Names, epithets, forms of Devi"),
        "02-god-names": ("God Names", "Male deities, sages, celestials"),
        "03-demons": ("Demons", "Asuras, demon vocabulary"),
        "04-weapons": ("Weapons", "Weapons, instruments, battle gear"),
        "05-body": ("Body", "Body parts, description, adornment"),
        "06-nature-cosmos": ("Nature & Cosmos", "Earth, sky, water, mountains"),
        "07-war-combat": ("War & Combat", "Battle terms, combat verbs"),
        "08-sound-speech": ("Sound & Speech", "Sound, praise, narrative markers"),
        "09-emotions": ("Emotions", "Mental states, qualities of mind"),
        "10-verbs": ("Verbs", "High-frequency action verbs"),
        "11-adjectives": ("Adjectives", "Power, beauty, size, intensity"),
        "12-ritual": ("Ritual", "Worship, offering, mantra"),
        "13-philosophy": ("Philosophy", "Metaphysics, tattvas, moksa"),
        "14-animals": ("Animals", "Animals, vehicles, mounts"),
        "15-indeclinables": ("Indeclinables", "Particles, conjunctions, adverbs"),
        "16-prefixes-suffixes": ("Prefixes & Suffixes", "Upasargas, taddhita, krt"),
        "17-compounds": ("Compounds", "Key samasas broken down"),
        "18-formulae": ("Formulae", "Recurring phrases, refrains"),
        "19-numbers-time-space": ("Numbers & Time", "Numbers, time, directions"),
        "20-sacred-geography": ("Sacred Geography", "Places, tirthas, plants"),
    }
    for fname in sorted(os.listdir(vocab_dir)):
        if not fname.endswith(".md"):
            continue
        key = fname.replace(".md", "")
        title, subtitle = vocab_meta.get(key, (key, ""))
        fpath = os.path.join(vocab_dir, fname)
        with open(fpath, "r") as f:
            content = f.read()
        # Extract flashcard pairs from markdown tables
        # Look for rows like: | term | meaning | ... |
        cards = []
        for line in content.split("\n"):
            line = line.strip()
            if not line.startswith("|") or line.startswith("|---") or line.startswith("| -"):
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 2:
                term = cols[0]
                meaning = cols[1]
                # Skip header rows
                if term.lower() in ("term", "root", "phrase", "file", "abbreviation",
                                     "prefix", "suffix", "pattern", "number", "type",
                                     "compound", "element", "#", ""):
                    continue
                if meaning.lower() in ("meaning", "function", "category", "text",
                                        "tradition", "entries", ""):
                    continue
                # Clean markdown formatting
                term = re.sub(r'\*\*(.+?)\*\*', r'\1', term)
                meaning = re.sub(r'\*\*(.+?)\*\*', r'\1', meaning)
                if term and meaning and len(term) < 100:
                    cards.append({"t": term, "m": meaning})
        vocab_categories.append({
            "id": key, "title": title, "subtitle": subtitle,
            "content": content, "cards": cards
        })

# ── Build HTML ──

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>tantrikk sanskrit</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root {
  --bg: #0f0f17;
  --bg-secondary: #151520;
  --bg-card: #1c1c2e;
  --bg-card-hover: #25253d;
  --text: #f0eef5;
  --text-muted: #9b95b0;
  --text-dim: #605a75;
  --accent: #ff6b4a;
  --accent-glow: #ff6b4a20;
  --accent-secondary: #ffa63e;
  --border: #2a2940;
  --code-bg: #0a0a12;
  --table-header: #1a1a2c;
  --table-row-alt: #131320;
  --scrollbar-thumb: #3d3a55;
  --sidebar-width: 300px;
  --link: #64d2ff;
  --green: #34d399;
  --red: #f87171;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Georgia', 'Palatino', serif;
  background: var(--bg);
  color: var(--text);
  display: flex;
  height: 100vh;
  overflow: hidden;
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 4px; }

/* ── Sidebar ── */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.sidebar-header {
  padding: 24px 20px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.sidebar-header h1 {
  font-size: 20px;
  color: var(--accent);
  letter-spacing: 1px;
  font-weight: normal;
}

.sidebar-header p {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
  letter-spacing: 0.5px;
}

.sidebar-search {
  padding: 12px 16px;
  flex-shrink: 0;
}

.sidebar-search input {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 13px;
  font-family: 'Georgia', serif;
  outline: none;
}

.sidebar-search input:focus { border-color: var(--accent); }
.sidebar-search input::placeholder { color: var(--text-dim); }

/* Section toggles */
.section-toggle {
  padding: 12px 20px;
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--border);
}

.section-btn {
  flex: 1;
  padding: 7px 0;
  text-align: center;
  font-size: 12px;
  font-family: 'Menlo', monospace;
  letter-spacing: 0.5px;
  border-radius: 5px;
  cursor: pointer;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  transition: all 0.15s;
}

.section-btn.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.section-btn:hover:not(.active) {
  border-color: var(--accent);
  color: var(--text);
}

.stage-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.stage-item {
  padding: 10px 20px;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: all 0.15s;
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.stage-item:hover { background: var(--bg-card); }

.stage-item.active {
  background: var(--bg-card);
  border-left-color: var(--accent);
}

.stage-item.hidden { display: none; }

.stage-num {
  font-size: 11px;
  color: var(--text-dim);
  min-width: 22px;
  font-family: 'Menlo', monospace;
}

.stage-info { flex: 1; min-width: 0; }

.stage-title { font-size: 14px; color: var(--text); }
.active .stage-title { color: var(--accent); }

.stage-subtitle {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.phase-label {
  padding: 16px 20px 6px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--text-dim);
  font-family: 'Menlo', monospace;
}

/* ── Main ── */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-bar {
  display: flex;
  padding: 0 32px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
  flex-shrink: 0;
  overflow-x: auto;
}

.tab {
  padding: 14px 24px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s;
  font-family: 'Menlo', monospace;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.tab:hover { color: var(--text); background: var(--bg-card); }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }

.content-wrap {
  flex: 1;
  overflow-y: auto;
}

.content {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 48px 80px;
}

/* Table horizontal scroll */
.content .table-wrap {
  overflow-x: auto;
  margin: 16px 0;
}

/* Bottom nav */
.bottom-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.nav-btn {
  padding: 10px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 13px;
  font-family: 'Georgia', serif;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
}

.nav-btn:hover { border-color: var(--accent); color: var(--accent); }
.nav-btn.disabled { opacity: 0.3; pointer-events: none; }

.nav-btn .nav-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-dim);
  display: block;
  margin-bottom: 4px;
}

.nav-btn .nav-title { color: var(--accent); }

/* Progress bar under tab-bar */
.progress-bar {
  height: 2px;
  background: var(--border);
  flex-shrink: 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
  transition: width 0.4s;
}

/* ── Markdown ── */
.content h1 { font-size: 28px; color: var(--accent); margin-bottom: 24px; font-weight: normal; line-height: 1.3; border-bottom: 1px solid var(--border); padding-bottom: 16px; }
.content h2 { font-size: 21px; color: var(--accent-secondary); margin-top: 40px; margin-bottom: 16px; font-weight: normal; }
.content h3 { font-size: 17px; margin-top: 28px; margin-bottom: 12px; font-weight: bold; }
.content h4 { font-size: 15px; color: var(--text-muted); margin-top: 20px; margin-bottom: 8px; font-weight: bold; }
.content p { font-size: 15px; line-height: 1.8; margin-bottom: 14px; }
.content ul, .content ol { margin-bottom: 14px; padding-left: 24px; }
.content li { font-size: 15px; line-height: 1.7; margin-bottom: 4px; }
.content blockquote { border-left: 3px solid var(--accent); padding: 12px 20px; margin: 16px 0; background: var(--accent-glow); border-radius: 0 6px 6px 0; font-style: italic; }
.content blockquote p { margin-bottom: 4px; }
.content code { background: var(--code-bg); padding: 2px 6px; border-radius: 3px; font-family: 'Menlo', monospace; font-size: 13px; color: var(--accent); }
.content pre { background: var(--code-bg); padding: 16px 20px; border-radius: 8px; overflow-x: auto; margin: 16px 0; border: 1px solid var(--border); }
.content pre code { background: none; padding: 0; font-size: 13px; line-height: 1.6; color: var(--text); }
.content table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
.content thead { background: var(--table-header); }
.content th { padding: 10px 14px; text-align: left; color: var(--accent); font-weight: normal; border-bottom: 2px solid var(--border); font-size: 13px; }
.content td { padding: 8px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
.content tbody tr:nth-child(even) { background: var(--table-row-alt); }
.content tbody tr:hover { background: var(--bg-card-hover); }
.content hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }
.content strong { color: var(--accent); font-weight: bold; }
.content a { color: var(--link); text-decoration: none; }
.content a:hover { text-decoration: underline; }

/* ── Flashcard ── */
.flashcard-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  max-width: 600px;
}

.fc-progress {
  font-size: 13px;
  color: var(--text-muted);
  font-family: 'Menlo', monospace;
  margin-bottom: 8px;
}

.fc-bar {
  width: 100%;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  margin-bottom: 32px;
  overflow: hidden;
}

.fc-bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.3s;
}

.fc-card {
  width: 100%;
  min-height: 220px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
  cursor: pointer;
  user-select: none;
  transition: border-color 0.2s;
  position: relative;
}

.fc-card:hover { border-color: var(--accent); }

.fc-term {
  font-size: 32px;
  color: var(--accent);
  text-align: center;
  line-height: 1.4;
}

.fc-hint {
  font-size: 12px;
  color: var(--text-dim);
  margin-top: 16px;
  font-family: 'Menlo', monospace;
}

.fc-meaning {
  font-size: 20px;
  color: var(--text);
  text-align: center;
  margin-top: 20px;
  line-height: 1.5;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  width: 100%;
}

.fc-buttons {
  display: flex;
  gap: 16px;
  margin-top: 32px;
  width: 100%;
}

.fc-btn {
  flex: 1;
  padding: 14px 24px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 14px;
  font-family: 'Georgia', serif;
  cursor: pointer;
  transition: all 0.15s;
  text-align: center;
}

.fc-btn:hover { border-color: var(--accent); }
.fc-btn.again { border-color: var(--red); color: var(--red); }
.fc-btn.again:hover { background: var(--red); color: white; }
.fc-btn.good { border-color: var(--green); color: var(--green); }
.fc-btn.good:hover { background: var(--green); color: white; }

.fc-score {
  display: flex;
  gap: 24px;
  margin-top: 20px;
  font-size: 13px;
  font-family: 'Menlo', monospace;
}

.fc-score span { color: var(--text-dim); }
.fc-score .g { color: var(--green); }
.fc-score .r { color: var(--red); }

.fc-done {
  text-align: center;
  padding: 60px 20px;
}

.fc-done h2 { color: var(--accent); font-weight: normal; margin-bottom: 16px; }
.fc-done p { color: var(--text-muted); margin-bottom: 24px; }

.fc-restart {
  padding: 12px 32px;
  background: var(--accent);
  color: var(--bg);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Georgia', serif;
  cursor: pointer;
}

.fc-restart:hover { opacity: 0.9; }

/* ── Mobile ── */
@media (max-width: 768px) {
  .sidebar { position: fixed; left: -100%; z-index: 100; width: 85vw; transition: left 0.3s; }
  .sidebar.open { left: 0; }
  .content { padding: 24px 20px 60px; }
  .tab { padding: 12px 16px; font-size: 12px; }
  .mobile-toggle { display: flex !important; }
}

.mobile-toggle {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 200;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--accent);
  width: 40px;
  height: 40px;
  border-radius: 8px;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
}

.overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 50; }
.overlay.show { display: block; }
</style>
</head>
<body>

<div class="mobile-toggle" onclick="toggleSidebar()">&#9776;</div>
<div class="overlay" id="overlay" onclick="toggleSidebar()"></div>

<nav class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <h1>tantrikk sanskrit</h1>
    <p>Beginner to Avadhani &middot; 32 Stages + Vocab</p>
  </div>
  <div class="section-toggle">
    <div class="section-btn active" onclick="showSection('lessons')">Lessons</div>
    <div class="section-btn" onclick="showSection('vocab')">Vocab</div>
  </div>
  <div class="sidebar-search">
    <input type="text" id="search" placeholder="Search..." oninput="filterItems(this.value)">
  </div>
  <div class="stage-list" id="stageList"></div>
</nav>

<main class="main">
  <div class="tab-bar" id="tabBar"></div>
  <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:0%"></div></div>
  <div class="content-wrap" id="contentWrap">
    <div class="content" id="content">
      <p style="color: var(--text-muted); margin-top: 40px; text-align: center;">Select a stage from the sidebar to begin.</p>
    </div>
  </div>
</main>

<script>
const STAGES = """ + json.dumps(stages, ensure_ascii=False) + """;
const FILE_LABELS = """ + json.dumps(file_labels) + """;
const VOCAB = """ + json.dumps(vocab_categories, ensure_ascii=False) + """;

const PHASES = [
  { after: 0, label: "Foundation" },
  { after: 6, label: "Roots & Building" },
  { after: 10, label: "Devotional Composition" },
  { after: 15, label: "Poetic Craft" },
  { after: 22, label: "Constraint Mastery" },
  { after: 26, label: "Avadhana Training" },
  { after: 30, label: "Avadhana" },
];

let currentSection = 'lessons';
let currentStage = null;
let currentTab = null;
let currentVocab = null;

// Flashcard state
let fcCards = [];
let fcIdx = 0;
let fcRevealed = false;
let fcGood = 0;
let fcAgain = 0;

function showSection(section) {
  currentSection = section;
  document.querySelectorAll('.section-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('.section-btn[onclick*="' + section + '"]').classList.add('active');
  document.getElementById('search').value = '';
  buildSidebar();
  if (section === 'lessons') {
    selectStage(0);
  } else {
    selectVocab(0);
  }
}

function buildSidebar() {
  const list = document.getElementById('stageList');
  let html = '';

  if (currentSection === 'lessons') {
    let phaseIdx = 0;
    STAGES.forEach((stage, i) => {
      while (phaseIdx < PHASES.length && stage.number > PHASES[phaseIdx].after) {
        if (stage.number > 0) html += '<div class="phase-label">' + PHASES[phaseIdx].label + '</div>';
        phaseIdx++;
      }
      const num = stage.number === 0 ? '' : String(stage.number).padStart(2, '0');
      html += '<div class="stage-item" data-idx="' + i + '" data-section="lessons" onclick="selectStage(' + i + ')">';
      html += '<span class="stage-num">' + num + '</span>';
      html += '<div class="stage-info"><div class="stage-title">' + stage.title + '</div>';
      html += '<div class="stage-subtitle">' + stage.subtitle + '</div></div></div>';
    });
  } else {
    html += '<div class="phase-label">Vocabulary Bank</div>';
    VOCAB.forEach((v, i) => {
      const num = v.id.split('-')[0];
      const cardCount = v.cards.length;
      const sub = v.subtitle + (cardCount > 0 ? ' &middot; ' + cardCount + ' cards' : '');
      html += '<div class="stage-item" data-idx="' + i + '" data-section="vocab" onclick="selectVocab(' + i + ')">';
      html += '<span class="stage-num">' + num + '</span>';
      html += '<div class="stage-info"><div class="stage-title">' + v.title + '</div>';
      html += '<div class="stage-subtitle">' + sub + '</div></div></div>';
    });
  }

  list.innerHTML = html;
}

function selectStage(idx) {
  currentStage = idx;
  currentVocab = null;
  const stage = STAGES[idx];

  document.querySelectorAll('.stage-item').forEach(el => el.classList.remove('active'));
  const item = document.querySelector('.stage-item[data-idx="' + idx + '"][data-section="lessons"]');
  if (item) item.classList.add('active');

  const tabBar = document.getElementById('tabBar');
  if (stage.number === 0) {
    tabBar.innerHTML = '<div class="tab active">Overview</div>';
    renderContent(stage.files.overview);
    currentTab = 'overview';
  } else {
    let tabHtml = '';
    stage.tabs.forEach((t, ti) => {
      const cls = ti === 0 ? 'active' : '';
      const label = FILE_LABELS[t] || t;
      tabHtml += '<div class="tab ' + cls + '" data-tab="' + t + '" onclick="selectTab(&quot;' + t + '&quot;)">' + label + '</div>';
    });
    tabBar.innerHTML = tabHtml;
    currentTab = stage.tabs[0];
    renderContent(stage.files[currentTab]);
  }

  closeMobileSidebar();
}

function selectVocab(idx) {
  currentVocab = idx;
  currentStage = null;
  const v = VOCAB[idx];

  document.querySelectorAll('.stage-item').forEach(el => el.classList.remove('active'));
  const item = document.querySelector('.stage-item[data-idx="' + idx + '"][data-section="vocab"]');
  if (item) item.classList.add('active');

  const tabBar = document.getElementById('tabBar');
  let tabHtml = '<div class="tab active" data-tab="browse" onclick="selectVocabTab(&quot;browse&quot;)">Browse</div>';
  if (v.cards.length > 0) {
    tabHtml += '<div class="tab" data-tab="flashcard" onclick="selectVocabTab(&quot;flashcard&quot;)">Flashcards</div>';
  }
  tabBar.innerHTML = tabHtml;
  currentTab = 'browse';
  renderContent(v.content);
  closeMobileSidebar();
}

function selectVocabTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  const tabEl = document.querySelector('.tab[data-tab="' + tab + '"]');
  if (tabEl) tabEl.classList.add('active');

  if (tab === 'browse') {
    renderContent(VOCAB[currentVocab].content);
  } else {
    startFlashcards(VOCAB[currentVocab].cards);
  }
}

function selectTab(tab) {
  if (currentStage === null) return;
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  const tabEl = document.querySelector('.tab[data-tab="' + tab + '"]');
  if (tabEl) tabEl.classList.add('active');
  renderContent(STAGES[currentStage].files[tab]);
}

function renderContent(md) {
  const el = document.getElementById('content');
  let html = marked.parse(md);
  // Wrap tables for horizontal scroll
  html = html.replace(/<table>/g, '<div class="table-wrap"><table>').replace(/<\/table>/g, '<\/table><\/div>');
  // Add bottom nav for lessons
  if (currentSection === 'lessons' && currentStage !== null) {
    html += buildBottomNav();
  }
  el.innerHTML = html;
  document.getElementById('contentWrap').scrollTop = 0;
  updateProgress();
}

function buildBottomNav() {
  const stage = STAGES[currentStage];
  const tabs = stage.tabs || [];
  const tabIdx = tabs.indexOf(currentTab);
  let h = '<div class="bottom-nav">';

  // Prev: previous tab, or previous stage last tab
  if (tabIdx > 0) {
    const prevTab = tabs[tabIdx - 1];
    h += '<div class="nav-btn" onclick="selectTab(&quot;' + prevTab + '&quot;)"><span class="nav-label">Previous</span><span class="nav-title">' + (FILE_LABELS[prevTab] || prevTab) + '</span></div>';
  } else if (currentStage > 0) {
    const prevStage = STAGES[currentStage - 1];
    h += '<div class="nav-btn" onclick="selectStage(' + (currentStage - 1) + ')"><span class="nav-label">Previous Stage</span><span class="nav-title">' + prevStage.title + '</span></div>';
  } else {
    h += '<div class="nav-btn disabled"></div>';
  }

  // Next: next tab, or next stage first tab
  if (tabIdx < tabs.length - 1) {
    const nextTab = tabs[tabIdx + 1];
    h += '<div class="nav-btn" onclick="selectTab(&quot;' + nextTab + '&quot;)"><span class="nav-label">Next</span><span class="nav-title">' + (FILE_LABELS[nextTab] || nextTab) + '</span></div>';
  } else if (currentStage < STAGES.length - 1) {
    const nextStage = STAGES[currentStage + 1];
    h += '<div class="nav-btn" onclick="selectStage(' + (currentStage + 1) + ')"><span class="nav-label">Next Stage</span><span class="nav-title">' + nextStage.title + '</span></div>';
  } else {
    h += '<div class="nav-btn disabled"></div>';
  }

  h += '</div>';
  return h;
}

function updateProgress() {
  const fill = document.getElementById('progressFill');
  if (currentSection === 'lessons' && currentStage !== null) {
    const stage = STAGES[currentStage];
    const tabs = stage.tabs || [];
    const tabIdx = Math.max(0, tabs.indexOf(currentTab));
    // Progress = stage position + tab fraction within stage
    const stageProgress = (currentStage / STAGES.length);
    const tabProgress = tabs.length > 1 ? (tabIdx / (tabs.length - 1)) / STAGES.length : 0;
    fill.style.width = Math.round((stageProgress + tabProgress) * 100) + '%';
  } else if (currentSection === 'vocab' && currentVocab !== null) {
    fill.style.width = Math.round(((currentVocab + 1) / VOCAB.length) * 100) + '%';
  }
}

// ── Flashcards ──

let fcBatchSize = 20;
let fcMissed = [];

function startFlashcards(cards, batchSize) {
  batchSize = batchSize || fcBatchSize;
  const deck = shuffle([...cards]);
  fcCards = deck.slice(0, Math.min(batchSize, deck.length));
  fcBatchSize = batchSize;
  fcIdx = 0;
  fcRevealed = false;
  fcGood = 0;
  fcAgain = 0;
  fcMissed = [];
  renderFlashcard();
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function renderFlashcard() {
  const el = document.getElementById('content');
  const total = VOCAB[currentVocab].cards.length;

  if (fcIdx >= fcCards.length) {
    let h = '<div class="fc-done"><h2>Round Complete</h2>';
    h += '<p>' + fcGood + ' known &middot; ' + fcAgain + ' to review &middot; ' + fcCards.length + ' cards</p>';
    if (fcMissed.length > 0) {
      h += '<button class="fc-restart" onclick="startFlashcards(fcMissed, fcMissed.length)" style="margin-right:12px">Drill Missed (' + fcMissed.length + ')</button>';
    }
    h += '<button class="fc-restart" onclick="startFlashcards(VOCAB[currentVocab].cards, fcBatchSize)">New Round</button>';
    if (total > 20) {
      h += '<div style="margin-top:20px">';
      [10, 20, 50, total].forEach(n => {
        const label = n === total ? 'All ' + total : n;
        const act = n === fcBatchSize ? 'color:var(--accent);border-color:var(--accent)' : '';
        h += '<button class="nav-btn" style="margin:4px;' + act + '" onclick="startFlashcards(VOCAB[currentVocab].cards,' + n + ')">' + label + '</button>';
      });
      h += '</div>';
    }
    h += '</div>';
    el.innerHTML = h;
    document.getElementById('contentWrap').scrollTop = 0;
    return;
  }

  const card = fcCards[fcIdx];
  const pct = Math.round((fcIdx / fcCards.length) * 100);

  let h = '<div class="flashcard-container">';
  h += '<div class="fc-progress">' + (fcIdx + 1) + ' / ' + fcCards.length;
  if (total > fcCards.length) h += ' (of ' + total + ')';
  h += '</div>';
  h += '<div class="fc-bar"><div class="fc-bar-fill" style="width:' + pct + '%"></div></div>';
  h += '<div class="fc-card" onclick="revealCard()">';
  h += '<div class="fc-term">' + escHtml(card.t) + '</div>';

  if (fcRevealed) {
    h += '<div class="fc-meaning">' + escHtml(card.m) + '</div>';
  } else {
    h += '<div class="fc-hint">space to reveal &middot; then &#8592; again / &#8594; good</div>';
  }

  h += '</div>';

  if (fcRevealed) {
    h += '<div class="fc-buttons">';
    h += '<button class="fc-btn again" onclick="fcAnswer(false)">&#8592; Again</button>';
    h += '<button class="fc-btn good" onclick="fcAnswer(true)">Good &#8594;</button>';
    h += '</div>';
  }

  h += '<div class="fc-score"><span class="g">good: ' + fcGood + '</span><span class="r">again: ' + fcAgain + '</span></div>';
  h += '</div>';

  el.innerHTML = h;
  document.getElementById('contentWrap').scrollTop = 0;
}

function revealCard() {
  if (!fcRevealed) {
    fcRevealed = true;
    renderFlashcard();
  }
}

function fcAnswer(good) {
  if (good) {
    fcGood++;
  } else {
    fcAgain++;
    fcMissed.push(fcCards[fcIdx]);
    // Re-queue missed card ~5 cards later
    const reinsert = Math.min(fcIdx + 3 + Math.floor(Math.random() * 4), fcCards.length);
    fcCards.splice(reinsert, 0, fcCards[fcIdx]);
  }
  fcIdx++;
  fcRevealed = false;
  renderFlashcard();
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Utilities ──

function filterItems(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.stage-item').forEach(el => {
    const idx = parseInt(el.dataset.idx);
    let text = '';
    if (currentSection === 'lessons') {
      const s = STAGES[idx];
      text = (s.title + ' ' + s.subtitle + ' ' + s.id).toLowerCase();
    } else {
      const v = VOCAB[idx];
      if (v) text = (v.title + ' ' + v.subtitle + ' ' + v.id).toLowerCase();
    }
    el.classList.toggle('hidden', q.length > 0 && !text.includes(q));
  });
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('show');
}

function closeMobileSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}

// Keyboard
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT') return;

  // Flashcard keys
  if (currentTab === 'flashcard' && currentVocab !== null) {
    if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); revealCard(); }
    else if (fcRevealed && (e.key === '1' || e.key === 'a' || e.key === 'ArrowLeft')) { e.preventDefault(); fcAnswer(false); }
    else if (fcRevealed && (e.key === '2' || e.key === 'g' || e.key === 'ArrowRight')) { e.preventDefault(); fcAnswer(true); }
    return;
  }

  // Tab shortcuts: 1-4 for lesson tabs
  if (currentSection === 'lessons' && currentStage !== null && currentStage > 0) {
    const stage = STAGES[currentStage];
    const tabNum = parseInt(e.key);
    if (tabNum >= 1 && tabNum <= 4 && stage.tabs[tabNum - 1]) {
      selectTab(stage.tabs[tabNum - 1]);
      return;
    }
  }

  if (currentSection === 'lessons') {
    if (e.key === 'ArrowDown' && currentStage < STAGES.length - 1) {
      selectStage(currentStage + 1);
      document.querySelector('.stage-item.active')?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'ArrowUp' && currentStage > 0) {
      selectStage(currentStage - 1);
      document.querySelector('.stage-item.active')?.scrollIntoView({ block: 'nearest' });
    }
  } else {
    if (e.key === 'ArrowDown' && currentVocab < VOCAB.length - 1) {
      selectVocab(currentVocab + 1);
      document.querySelector('.stage-item.active')?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'ArrowUp' && currentVocab > 0) {
      selectVocab(currentVocab - 1);
      document.querySelector('.stage-item.active')?.scrollIntoView({ block: 'nearest' });
    }
  }

  if (e.key === '/' && !e.metaKey) {
    e.preventDefault();
    document.getElementById('search').focus();
  }
});

// Init
buildSidebar();
selectStage(0);
</script>
</body>
</html>
"""

with open(OUTPUT, "w") as f:
    f.write(html)

total_cards = sum(len(v["cards"]) for v in vocab_categories)
print(f"Built: {OUTPUT}")
print(f"Lessons: {len(stages)} stages")
print(f"Vocab: {len(vocab_categories)} categories, {total_cards} flashcards")
