#!/usr/bin/env python3
"""Build a single-page web UI for conversational sanskrit from all markdown files."""

import os
import json
import re

CONV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversation")
OUTPUT = os.path.join(CONV_DIR, "conversation.html")

# ── Collect stages ──

stages = []

overview_path = os.path.join(CONV_DIR, "00-overview.md")
if os.path.exists(overview_path):
    with open(overview_path, "r") as f:
        stages.append({
            "id": "00-overview", "number": 0,
            "title": "Overview", "subtitle": "The Lego Track",
            "files": {"overview": f.read()}, "tabs": ["overview"]
        })

stage_meta = {
    "conv-01-this-is": ("This Is / That Is", "etat X asti"),
    "conv-02-i-am": ("I Am / You Are", "aham X asmi"),
    "conv-03-questions": ("Questions", "kim, kutra, kaḥ, kadā"),
    "conv-04-wanting": ("Wanting & Needing", "icchāmi, āvaśyakam"),
    "conv-05-doing": ("Doing Things", "Present tense verbs"),
    "conv-06-past-future": ("Did & Will Do", "Past & future tense"),
    "conv-07-having": ("Having & Existing", "mama asti, atra asti"),
    "conv-08-going-coming": ("Going & Coming", "gacchāmi, āgaccha"),
    "conv-09-give-take": ("Give & Take", "dehi, gṛhāṇa"),
    "conv-10-likes": ("Likes & Preferences", "rocate, priyam"),
    "conv-11-knowing": ("Knowing & Not Knowing", "jānāmi, na jānāmi"),
    "conv-12-can-cannot": ("Can & Cannot", "śaknomi, na śaknomi"),
    "conv-13-polite": ("Polite Phrases", "kṛpayā, dhanyavādaḥ"),
    "conv-14-because": ("Because & Therefore", "yataḥ...tataḥ"),
    "conv-15-if-then": ("If & Then", "yadi...tarhi"),
    "conv-16-but-although": ("But & Although", "kintu, yadyapi...tathāpi"),
    "conv-17-when-while": ("When & While", "yadā...tadā"),
    "conv-18-sequencing": ("First, Then, Finally", "prathamam, tataḥ, ante"),
    "conv-19-comparing": ("Comparing", "uttamam, iva, sadṛśam"),
    "conv-20-who-which": ("The One Who...", "yaḥ...saḥ"),
    "conv-21-opinions": ("I Think & Opinions", "manye, mama matena"),
    "conv-22-should-must": ("Should & Must", "kartavyam, karaṇīyam"),
    "conv-23-would-have": ("Would Have / But Instead", "Conditional past"),
    "conv-24-telling-stories": ("Telling a Story", "ekadā...tataḥ...ante"),
    "conv-25-particles": ("Particles & Emphasis", "eva, api, khalu, nanu, kila"),
    "conv-26-still-already": ("Still / Already / No Longer", "adhunāpi, pūrvam eva, na punaḥ"),
    "conv-27-frequency": ("Always / Sometimes / Never", "sadā, kadācit, na kadāpi"),
    "conv-28-reported-speech": ("Reported Speech", "saḥ avadat yat..., iti"),
    "conv-29-clarifying": ("Clarifying & Repairing", "punaḥ vadatu, ko'rthaḥ?"),
    "conv-30-exclamations": ("Exclamations & Reactions", "aho!, sādhu!, adbhutam!"),
    "conv-31-lakara-trio": ("Blessings, Promises & Vivid Past", "Luṅ, Liṭ, Luṭ, āśīrliṅ"),
}

file_labels = {
    "theory": "Theory", "workbook-questions": "Questions",
    "workbook-answers": "Answers",
}

for dirname, (title, subtitle) in stage_meta.items():
    stage_dir = os.path.join(CONV_DIR, dirname)
    if not os.path.isdir(stage_dir):
        continue
    num = int(dirname.split("-")[1])
    files = {}
    tabs = []
    for fname in ["theory", "workbook-questions", "workbook-answers"]:
        fpath = os.path.join(stage_dir, f"{fname}.md")
        if os.path.exists(fpath):
            with open(fpath, "r") as f:
                files[fname] = f.read()
                tabs.append(fname)
    if tabs:
        stages.append({"id": dirname, "number": num, "title": title,
                        "subtitle": subtitle, "files": files, "tabs": tabs})

stages.sort(key=lambda s: s["number"])

# ── Build HTML ──

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>conversational sanskrit</title>
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
  --accent: #34d399;
  --accent-glow: #34d39920;
  --accent-secondary: #64d2ff;
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
  font-size: 18px;
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

.sidebar-header .back-link {
  display: inline-block;
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-dim);
  text-decoration: none;
  font-family: 'Menlo', monospace;
}

.sidebar-header .back-link:hover { color: var(--accent); }

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

/* Progress bar */
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
    <h1>conversational sanskrit</h1>
    <p>31 Lego Pieces &middot; From Pointing to Storytelling</p>
    <a class="back-link" href="../index.html">&larr; main syllabus</a>
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
const STAGES = """ + json.dumps(stages, ensure_ascii=False) + r""";
const FILE_LABELS = """ + json.dumps(file_labels) + r""";

const PHASES = [
  { after: 0, label: "Survival" },
  { after: 8, label: "Fluency" },
  { after: 16, label: "Mastery" },
  { after: 24, label: "Polish" },
];

let currentStage = null;
let currentTab = null;

function buildSidebar() {
  const list = document.getElementById('stageList');
  let html = '';
  let phaseIdx = 0;

  STAGES.forEach((stage, i) => {
    while (phaseIdx < PHASES.length && stage.number > PHASES[phaseIdx].after) {
      if (stage.number > 0) html += '<div class="phase-label">' + PHASES[phaseIdx].label + '</div>';
      phaseIdx++;
    }
    const num = stage.number === 0 ? '' : String(stage.number).padStart(2, '0');
    html += '<div class="stage-item" data-idx="' + i + '" onclick="selectStage(' + i + ')">';
    html += '<span class="stage-num">' + num + '</span>';
    html += '<div class="stage-info"><div class="stage-title">' + stage.title + '</div>';
    html += '<div class="stage-subtitle">' + stage.subtitle + '</div></div></div>';
  });

  list.innerHTML = html;
}

function selectStage(idx) {
  currentStage = idx;
  const stage = STAGES[idx];

  document.querySelectorAll('.stage-item').forEach(el => el.classList.remove('active'));
  const item = document.querySelector('.stage-item[data-idx="' + idx + '"]');
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
      tabHtml += '<div class="tab ' + cls + '" data-tab="' + t + '" onclick="selectTab(\'' + t + '\')">' + label + '</div>';
    });
    tabBar.innerHTML = tabHtml;
    currentTab = stage.tabs[0];
    renderContent(stage.files[currentTab]);
  }

  closeMobileSidebar();
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
  html = html.replace(/<table>/g, '<div class="table-wrap"><table>').replace(/<\/table>/g, '</table></div>');
  if (currentStage !== null) {
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

  if (tabIdx > 0) {
    const prevTab = tabs[tabIdx - 1];
    h += '<div class="nav-btn" onclick="selectTab(\'' + prevTab + '\')"><span class="nav-label">Previous</span><span class="nav-title">' + (FILE_LABELS[prevTab] || prevTab) + '</span></div>';
  } else if (currentStage > 0) {
    const prevStage = STAGES[currentStage - 1];
    h += '<div class="nav-btn" onclick="selectStage(' + (currentStage - 1) + ')"><span class="nav-label">Previous Stage</span><span class="nav-title">' + prevStage.title + '</span></div>';
  } else {
    h += '<div class="nav-btn disabled"></div>';
  }

  if (tabIdx < tabs.length - 1) {
    const nextTab = tabs[tabIdx + 1];
    h += '<div class="nav-btn" onclick="selectTab(\'' + nextTab + '\')"><span class="nav-label">Next</span><span class="nav-title">' + (FILE_LABELS[nextTab] || nextTab) + '</span></div>';
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
  if (currentStage !== null) {
    const stage = STAGES[currentStage];
    const tabs = stage.tabs || [];
    const tabIdx = Math.max(0, tabs.indexOf(currentTab));
    const stageProgress = (currentStage / STAGES.length);
    const tabProgress = tabs.length > 1 ? (tabIdx / (tabs.length - 1)) / STAGES.length : 0;
    fill.style.width = Math.round((stageProgress + tabProgress) * 100) + '%';
  }
}

function filterItems(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.stage-item').forEach(el => {
    const idx = parseInt(el.dataset.idx);
    const s = STAGES[idx];
    const text = (s.title + ' ' + s.subtitle + ' ' + s.id).toLowerCase();
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

  if (currentStage !== null && currentStage > 0) {
    const stage = STAGES[currentStage];
    const tabNum = parseInt(e.key);
    if (tabNum >= 1 && tabNum <= 3 && stage.tabs[tabNum - 1]) {
      selectTab(stage.tabs[tabNum - 1]);
      return;
    }
  }

  if (e.key === 'ArrowDown' && currentStage < STAGES.length - 1) {
    selectStage(currentStage + 1);
    document.querySelector('.stage-item.active')?.scrollIntoView({ block: 'nearest' });
  } else if (e.key === 'ArrowUp' && currentStage > 0) {
    selectStage(currentStage - 1);
    document.querySelector('.stage-item.active')?.scrollIntoView({ block: 'nearest' });
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

print(f"Built: {OUTPUT}")
print(f"Stages: {len(stages)}")
