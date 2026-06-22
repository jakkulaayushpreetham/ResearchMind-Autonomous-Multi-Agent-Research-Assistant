import re
import time
import html as htmllib

import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ══════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ResearchMind · Multi-Agent Research System",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM
#  Identity: a live signal system, not a SaaS landing page. Four agents are
#  nodes on a single trace; work is current that flows from node to node.
#  Palette: graphite base, bioluminescent signal-green for active current,
#  hot signal-pink reserved for critique/attention. Mono-forward type system
#  because this product IS infrastructure — it should read like one.
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

:root {
    --void:       #07080a;
    --panel:      #0d0f12;
    --panel-2:    #111418;
    --line:       rgba(255,255,255,0.08);
    --line-soft:  rgba(255,255,255,0.04);
    --paper:      #eef1ef;
    --paper-dim:  #8a9290;
    --paper-faint:#4d5350;

    --signal:      #39ffb0;
    --signal-dim:  #1c8f63;
    --signal-glow: rgba(57,255,176,0.18);
    --signal-soft: #a8ffd9;

    --pulse:       #ff3d8a;
    --pulse-glow:  rgba(255,61,138,0.18);

    --amber:       #ffb84d;
    --amber-glow:  rgba(255,184,77,0.16);

    --wire:        rgba(57,255,176,0.22);
    --wire-off:    rgba(255,255,255,0.06);
}

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; color: var(--paper); }

.stApp {
    background: var(--void);
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px),
        radial-gradient(ellipse 70% 45% at 50% -8%, rgba(57,255,176,0.1) 0%, transparent 60%),
        radial-gradient(ellipse 50% 35% at 90% 100%, rgba(255,61,138,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 100% 100% at 50% 50%, transparent 40%, rgba(0,0,0,0.45) 100%);
    background-size: 38px 38px, 38px 38px, 100% 100%, 100% 100%, 100% 100%;
    background-attachment: fixed;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.4rem 3rem 4rem; max-width: 1260px; }

::selection { background: var(--signal-glow); color: var(--paper); }
::-webkit-scrollbar { width: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(57,255,176,0.22); border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: rgba(57,255,176,0.4); }

/* ───────── keyframes ───────── */
@keyframes fade-up      { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
@keyframes blink-cursor { 0%,49% { opacity:1; } 50%,100% { opacity:0; } }
@keyframes node-pulse   { 0%,100% { box-shadow: 0 0 0 0 var(--signal-glow), 0 0 14px var(--signal); } 50% { box-shadow: 0 0 0 12px transparent, 0 0 4px var(--signal); } }
@keyframes ring-spin    { to { transform: rotate(360deg); } }
@keyframes current-flow { 0% { stroke-dashoffset: 24; } 100% { stroke-dashoffset: 0; } }
@keyframes flicker      { 0%,100% { opacity:1; } 92% { opacity:1; } 93% { opacity:.4; } 94% { opacity:1; } }
@keyframes scan-line    { 0% { transform: translateY(-100%); } 100% { transform: translateY(100%); } }

.fade-in { animation: fade-up .45s cubic-bezier(.16,1,.3,1) both; }

/* ═════════ HERO ═════════ */
.hero { padding: 1.6rem 0 1.6rem; text-align:center; position:relative; }
.hero-tag {
    display:inline-flex; align-items:center; gap:.55rem;
    font-family:'JetBrains Mono',monospace; font-size:.68rem; font-weight:500;
    letter-spacing:.2em; text-transform:uppercase; color:var(--signal-soft);
    background: rgba(57,255,176,0.06); border:1px solid rgba(57,255,176,0.28);
    padding:.42rem 1rem; margin-bottom:1.5rem;
    clip-path: polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%);
}
.hero-tag .blip { width:6px; height:6px; background:var(--signal); flex-shrink:0;
    box-shadow: 0 0 8px var(--signal); animation: blink-cursor 1.4s step-end infinite; }

.hero h1 {
    font-family:'Space Grotesk',sans-serif; font-size:clamp(2.9rem,6.4vw,5.4rem);
    font-weight:700; line-height:.95; letter-spacing:-.03em; color:var(--paper); margin:0 0 1.1rem;
    text-shadow: 0 0 40px rgba(57,255,176,0.12);
}
.hero h1 .glyph {
    color:var(--signal); display:inline-block;
    text-shadow: 0 0 18px var(--signal), 0 0 36px rgba(57,255,176,0.5);
    animation: glyph-spin 6s linear infinite;
}
@keyframes glyph-spin {
    0%, 40% { transform: rotate(0deg); }
    50% { transform: rotate(180deg); }
    90%, 100% { transform: rotate(180deg); }
}
.hero h1 .cursor-blink {
    display:inline-block; width:.09em; height:.78em; background:var(--signal);
    box-shadow: 0 0 12px var(--signal);
    margin-left:.06em; vertical-align:-.05em; animation: blink-cursor 1s step-end infinite;
}
.hero-sub {
    font-family:'JetBrains Mono',monospace; font-size:.92rem; font-weight:300; color:var(--paper-dim);
    max-width:580px; margin:0 auto; line-height:1.85;
}
.hero-sub b { color: var(--paper); font-weight:500; }

.rule {
    height:1px; margin:2rem 0;
    background: repeating-linear-gradient(90deg, var(--line) 0, var(--line) 6px, transparent 6px, transparent 12px);
}
.rule-solid { height:1px; background:var(--line-soft); margin:1.5rem 0; }

/* ═════════ CONSOLE / INPUT ═════════ */
.console {
    background: var(--panel);
    border:1px solid var(--line); position:relative;
    padding: 0; margin-bottom: 1.6rem;
}
.console-head {
    display:flex; align-items:center; gap:.5rem;
    padding:.65rem 1.1rem; border-bottom:1px solid var(--line);
    background: var(--panel-2);
}
.console-head .dot { width:7px; height:7px; border-radius:50%; }
.console-head .dot:nth-child(1) { background:#ff5f56; }
.console-head .dot:nth-child(2) { background:#ffbd2e; }
.console-head .dot:nth-child(3) { background:#27c93f; }
.console-head .path {
    margin-left:.6rem; font-family:'JetBrains Mono',monospace; font-size:.7rem;
    color: var(--paper-faint); letter-spacing:.04em;
}
.console-body { padding: 1.6rem 1.4rem 1.3rem; }

.field-label {
    font-family:'JetBrains Mono',monospace; font-size:.68rem; font-weight:500;
    letter-spacing:.18em; text-transform:uppercase; color:var(--signal-soft);
    margin-bottom:.55rem; display:flex; align-items:center; gap:.5rem;
}
.field-label::before { content:'>'; color:var(--signal); }

.stTextInput > div > div > input {
    background: var(--void) !important;
    border:1px solid var(--line) !important; border-radius:0 !important;
    color:var(--paper) !important;
    font-family:'JetBrains Mono',monospace !important; font-size:.95rem !important;
    padding:.85rem 1rem !important;
    transition: border-color .2s, box-shadow .2s !important;
}
.stTextInput > div > div > input:focus {
    border-color:var(--signal) !important; box-shadow:0 0 0 3px var(--signal-glow) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--paper-faint) !important; }
.stTextInput > label { display:none !important; }

.stButton > button {
    background: var(--signal) !important;
    color:#04140d !important; font-family:'JetBrains Mono',monospace !important;
    font-weight:700 !important; font-size:.9rem !important; letter-spacing:.12em !important;
    text-transform:uppercase !important;
    border:none !important; border-radius:0 !important; padding:.95rem 2rem !important;
    cursor:pointer !important; width:100%;
    transition: filter .15s, transform .1s, box-shadow .2s !important;
    box-shadow: 0 0 0 0 rgba(57,255,176,0.5), 0 10px 28px -8px rgba(57,255,176,0.4) !important;
    clip-path: polygon(0 0, 100% 0, 100% 70%, calc(100% - 14px) 100%, 0 100%);
}
.stButton > button:hover {
    filter:brightness(1.15) !important;
    box-shadow: 0 0 0 3px rgba(57,255,176,0.18), 0 14px 36px -8px rgba(57,255,176,0.55) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform:translateY(1px) !important; }

.stDownloadButton > button {
    background: transparent !important;
    color: var(--signal-soft) !important;
    border:1px solid var(--signal-dim) !important; border-radius:0 !important;
    font-family:'JetBrains Mono',monospace !important; font-size:.74rem !important;
    letter-spacing:.1em !important; text-transform:uppercase !important;
    padding:.65rem 1.3rem !important; transition:.15s !important;
}
.stDownloadButton > button:hover { background: rgba(57,255,176,0.08) !important; border-color: var(--signal) !important; }

/* query chips */
.chip-row { display:flex; gap:.5rem; flex-wrap:wrap; margin-top:1.1rem; align-items:center; }
.chip-label {
    font-family:'JetBrains Mono',monospace; font-size:.66rem; color:var(--paper-faint);
    letter-spacing:.14em; margin-right:.3rem; text-transform:uppercase;
}
.chip {
    background: transparent; border:1px solid var(--line);
    padding:.3rem .75rem; font-size:.76rem; color:var(--paper-dim);
    font-family:'JetBrains Mono',monospace; transition: border-color .15s, color .15s;
}

/* ═════════ SECTION LABEL ═════════ */
.section-label {
    font-family:'JetBrains Mono',monospace; font-size:.74rem; font-weight:600;
    color:var(--paper); margin:0 0 1.2rem; letter-spacing:.12em; text-transform:uppercase;
    display:flex; align-items:center; gap:.7rem;
}
.section-label::before { content:''; width:9px; height:9px; background:var(--signal); flex-shrink:0; }
.section-label .count {
    font-family:'JetBrains Mono',monospace; font-size:.66rem; font-weight:500;
    color:var(--signal-soft); background:rgba(57,255,176,0.07);
    border:1px solid rgba(57,255,176,0.25); padding:.18rem .55rem; letter-spacing:.06em;
    margin-left:auto;
}

/* ═════════ SIGNAL RAIL — the pipeline ═════════ */
.rail { position:relative; padding-left: 2.6rem; }
.rail-wire {
    position:absolute; left: 1.05rem; top: 1.3rem; bottom: 1.3rem; width:2px;
    background: var(--wire-off);
}
.rail-wire .charge {
    position:absolute; left:0; top:0; width:100%; height:34%;
    background: linear-gradient(180deg, transparent, var(--signal), transparent);
    animation: current-rise 1.4s linear infinite;
    opacity:0;
}
@keyframes current-rise {
    0%   { top:-34%; opacity:0; }
    15%  { opacity:1; }
    85%  { opacity:1; }
    100% { top:100%; opacity:0; }
}
.rail-wire.live .charge { opacity:1; }

.node {
    position:relative; margin-bottom: 1.55rem; padding: 1.05rem 1.2rem 1.05rem 0;
}
.node:last-child { margin-bottom:0; }
.node-marker {
    position:absolute; left:-2.6rem; top:.95rem;
    width: 34px; height:34px; border-radius:50%;
    background: var(--panel); border:2px solid var(--wire-off);
    display:flex; align-items:center; justify-content:center;
    transition: border-color .3s, background .3s; z-index:2;
}
.node-marker svg { width:16px; height:16px; stroke: var(--paper-faint); transition: stroke .3s; }
.node.running .node-marker { border-color: var(--signal); background: rgba(57,255,176,0.08); animation: node-pulse 1.6s ease-in-out infinite; }
.node.running .node-marker svg { stroke: var(--signal); }
.node.done .node-marker { border-color: var(--signal-dim); background: rgba(57,255,176,0.1); }
.node.done .node-marker svg { stroke: var(--signal); }

.node-card {
    background: var(--panel); border:1px solid var(--line);
    padding: 1.05rem 1.3rem; transition: border-color .3s, background .3s;
}
.node.running .node-card {
    border-color: var(--signal); background: rgba(57,255,176,0.06);
    box-shadow: 0 0 0 1px rgba(57,255,176,0.15), 0 8px 30px -10px rgba(57,255,176,0.35);
}
.node.done .node-card { border-color: var(--line); background: var(--panel); }

.node-top { display:flex; align-items:baseline; gap:.7rem; margin-bottom:.3rem; }
.node-id { font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--paper-faint); letter-spacing:.05em; }
.node-title { font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:600; color:var(--paper); flex:1; }
.node-state {
    font-family:'JetBrains Mono',monospace; font-size:.64rem; letter-spacing:.1em; text-transform:uppercase;
    display:flex; align-items:center; gap:.4rem;
}
.state-idle    { color: var(--paper-faint); }
.state-running { color: var(--signal); }
.state-done    { color: var(--signal-soft); }
.state-running::before {
    content:''; width:6px; height:6px; border-radius:50%; background:var(--signal);
    box-shadow: 0 0 6px var(--signal); animation: blink-cursor 1s step-end infinite;
}
.state-done::before { content:'✓'; }
.node-desc { font-family:'JetBrains Mono',monospace; font-size:.78rem; color:var(--paper-faint); line-height:1.6; }

/* ═════════ RAW OUTPUT ═════════ */
.raw-panel {
    background: var(--void); border:1px solid var(--line-soft);
    padding:1.2rem 1.4rem; font-size:.83rem;
    line-height:1.75; color: var(--paper-dim); white-space:pre-wrap;
    font-family:'JetBrains Mono',monospace; max-height:420px; overflow-y:auto;
}

/* ═════════ REPORT ═════════ */
.report-shell {
    background: var(--panel); border:1px solid var(--line);
    border-left: 3px solid var(--signal);
    padding: 2.2rem 2.4rem 2rem; margin-top:.5rem;
}
.report-kicker {
    display:flex; align-items:center; justify-content:space-between; gap:1rem;
    margin-bottom:1.6rem; padding-bottom:1.2rem; border-bottom:1px solid var(--line);
}
.report-kicker-left { display:flex; align-items:center; gap:.75rem; }
.report-kicker-mark {
    width:1.7rem; height:1.7rem; border:1px solid var(--signal-dim);
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.report-kicker-mark svg { width:15px; height:15px; stroke:var(--signal); }
.report-kicker-label {
    font-family:'JetBrains Mono',monospace; font-size:.7rem; letter-spacing:.18em;
    text-transform:uppercase; color:var(--signal-soft);
}
.report-meta { font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--paper-faint); letter-spacing:.05em; }

.report-title {
    font-family:'Space Grotesk',sans-serif; font-size:1.85rem; font-weight:700; letter-spacing:-.02em;
    color:var(--paper); line-height:1.18; margin: 0 0 1.5rem;
}

.report-toc { display:flex; flex-wrap:wrap; gap:.5rem; margin-bottom:2rem; }
.report-toc-item {
    font-family:'JetBrains Mono',monospace; font-size:.72rem; color:var(--paper-dim);
    background: transparent; border:1px solid var(--line);
    padding:.38rem .8rem;
}
.report-toc-item b { color: var(--signal-soft); margin-right:.35rem; font-weight:500; }

.report-h2 {
    font-family:'Space Grotesk',sans-serif; font-size:1.25rem; font-weight:700; color:var(--paper);
    margin: 1.6rem 0 .9rem; padding-bottom:.55rem; border-bottom:1px solid var(--line);
    letter-spacing:-.01em;
}
.report-h2:first-of-type { margin-top:0; }
.report-h3 {
    font-family:'Space Grotesk',sans-serif; font-size:1.02rem; font-weight:700; color:var(--signal-soft);
    margin: 1.2rem 0 .6rem;
}
.report-body { font-size:.95rem; line-height:1.85; color:#cdd3d0; font-weight:400; margin:0 0 .9rem; }
.report-body b, .report-body strong { color: var(--paper); font-weight:600; }
.report-body em, .report-body i { color: var(--signal-soft); font-style:normal; border-bottom: 1px dotted var(--signal-dim); }
.report-body code {
    background: rgba(57,255,176,0.1); color: var(--signal-soft);
    padding:.1rem .4rem; font-family:'JetBrains Mono',monospace; font-size:.86em;
}
.report-list { margin: .4rem 0 1.1rem; padding-left:0; list-style:none; }
.report-list li {
    position:relative; padding-left:1.5rem; margin-bottom:.6rem;
    font-size:.94rem; line-height:1.75; color:#cdd3d0;
}
.report-list li::before {
    content:''; position:absolute; left:0; top:.6rem; width:7px; height:1px;
    background: var(--signal);
}
.report-list.numbered { counter-reset: item; }
.report-list.numbered li { counter-increment: item; padding-left:1.9rem; }
.report-list.numbered li::before {
    content: counter(item, decimal-leading-zero); width:auto; height:auto;
    background:none; font-family:'JetBrains Mono',monospace; font-size:.74rem;
    color:var(--signal); top:.05rem; font-weight:600;
}
.report-quote {
    border-left:2px solid var(--pulse); background: rgba(255,61,138,0.05);
    padding:.85rem 1.15rem; margin:1rem 0;
    font-size:.92rem; color: var(--paper-dim); font-family:'JetBrains Mono',monospace; line-height:1.7;
}
.report-conclusion {
    margin-top: 1.4rem; padding: 1.15rem 1.35rem;
    background: rgba(57,255,176,0.045); border:1px solid var(--signal-dim);
    border-left: 2px solid var(--signal);
    font-size:.93rem; line-height:1.75; color:#d7f5e7;
}
.report-conclusion .label {
    font-family:'JetBrains Mono',monospace; font-size:.64rem; letter-spacing:.16em; text-transform:uppercase;
    color: var(--signal); margin-bottom:.5rem; display:block;
}

/* ═════════ CRITIC PANEL ═════════ */
.feedback-shell {
    background: var(--panel); border:1px solid var(--line);
    border-left: 3px solid var(--pulse);
    padding: 2.1rem 2.3rem; margin-top:.5rem;
}
.feedback-kicker {
    display:flex; align-items:center; gap:.75rem; margin-bottom:1.5rem;
    padding-bottom:1.15rem; border-bottom:1px solid var(--line);
}
.feedback-kicker-mark {
    width:1.7rem; height:1.7rem; border:1px solid var(--pulse);
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.feedback-kicker-mark svg { width:15px; height:15px; stroke:var(--pulse); }
.feedback-kicker-label {
    font-family:'JetBrains Mono',monospace; font-size:.7rem; letter-spacing:.18em;
    text-transform:uppercase; color:var(--pulse);
}

.score-row { display:flex; align-items:center; gap:1.7rem; margin-bottom:1.6rem; flex-wrap:wrap; }
.score-dial-wrap { position:relative; width:84px; height:84px; flex-shrink:0; }
.score-dial-wrap svg { width:84px; height:84px; transform:rotate(-90deg); }
.score-dial-bg { fill:none; stroke:rgba(255,255,255,0.07); stroke-width:5; }
.score-dial-fg { fill:none; stroke-width:5; stroke-linecap:square; transition: stroke-dashoffset 1.1s cubic-bezier(.16,1,.3,1); }
.score-dial-num {
    position:absolute; top:0; left:0; width:100%; height:100%;
    display:flex; align-items:center; justify-content:center;
    font-family:'JetBrains Mono',monospace; font-weight:700; font-size:1.35rem; color: var(--paper);
}
.score-caption { flex:1; min-width:180px; }
.score-caption .verdict { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.02rem; color: var(--paper); margin-bottom:.25rem; }
.score-caption .sub { font-family:'JetBrains Mono',monospace; font-size:.68rem; color: var(--paper-faint); letter-spacing:.08em; text-transform:uppercase; }

.feedback-body { font-size:.92rem; line-height:1.8; color:#d4dad7; margin:0 0 .8rem; }
.feedback-list { list-style:none; padding-left:0; margin:.3rem 0 1rem; }
.feedback-list li {
    position:relative; padding-left:1.5rem; margin-bottom:.6rem; font-size:.9rem; line-height:1.7; color:#d4dad7;
}
.feedback-list li::before {
    content:''; position:absolute; left:0; top:.5rem; width:8px; height:8px;
    background: var(--signal);
}
.feedback-list.issues li::before { background: var(--pulse); }

/* ═════════ EXPANDER ═════════ */
[data-testid="stExpander"] {
    border: 1px solid var(--line) !important; border-radius: 0 !important;
    background: var(--panel) !important;
}
[data-testid="stExpander"] summary {
    font-family:'JetBrains Mono',monospace !important; font-size:.76rem !important;
    color: var(--paper-dim) !important; letter-spacing:.04em !important;
}

.stSpinner > div { color: var(--signal) !important; }
.stSpinner p { font-family:'JetBrains Mono',monospace !important; font-size:.8rem !important; color: var(--paper-dim) !important; }
[data-testid="stAlert"] { border-radius: 0 !important; font-family:'JetBrains Mono',monospace !important; }

/* ═════════ FOOTER ═════════ */
.notice {
    font-family:'JetBrains Mono',monospace; font-size:.68rem; color: var(--paper-faint);
    text-align:center; margin-top:3.2rem; letter-spacing:.08em;
}
.notice .sep { margin: 0 .6rem; opacity:.4; color: var(--signal-dim); }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  CUSTOM LINE ICONS (inline SVG — no emoji)
# ══════════════════════════════════════════════════════════════════════════
ICON_SEARCH = """<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.5" y1="15.5" x2="20.5" y2="20.5"/></svg>"""

ICON_READER = """<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M5 3.5h9l4 4V20a.5.5 0 0 1-.5.5H5.5A.5.5 0 0 1 5 20V4a.5.5 0 0 1 .5-.5z"/>
<path d="M8.5 11h7M8.5 14.5h7M8.5 17.5h4.5"/></svg>"""

ICON_WRITER = """<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M4 20l1-4.2L15.6 5.2a1.4 1.4 0 0 1 2 0l1.2 1.2a1.4 1.4 0 0 1 0 2L8.2 19 4 20z"/>
<line x1="13.8" y1="6.8" x2="17.2" y2="10.2"/></svg>"""

ICON_CRITIC = """<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M9.5 3.5a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/>
<line x1="14.2" y1="13.6" x2="20" y2="19.5"/>
<path d="M7 9.5h5"/></svg>"""

ICON_DOC = """<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M6 3.5h8l4 4V20a.5.5 0 0 1-.5.5H6.5A.5.5 0 0 1 6 20V4a.5.5 0 0 1 .5-.5z"/>
<path d="M9 10.5h6M9 14h6M9 17.5h3.5"/></svg>"""

ICON_GAUGE = """<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M4 16a8 8 0 1 1 16 0"/><line x1="12" y1="16" x2="15.2" y2="11.5"/><circle cx="12" cy="16" r="1"/></svg>"""

NODE_ICONS = {"search": ICON_SEARCH, "reader": ICON_READER, "writer": ICON_WRITER, "critic": ICON_CRITIC}


def _html(s: str) -> str:
    """
    Strip leading whitespace from every line of an HTML chunk before it is
    handed to st.markdown(). Streamlit's markdown layer treats any line
    indented 4+ spaces as a code fence — since multi-line f-strings written
    inside an indented `for`/`with` block inherit that indentation verbatim,
    skipping this step causes raw tags to render as literal visible text
    instead of being parsed as HTML.
    """
    return "\n".join(line.lstrip() for line in s.split("\n"))


# ══════════════════════════════════════════════════════════════════════════
#  MARKDOWN → STYLED HTML RENDERER
# ══════════════════════════════════════════════════════════════════════════
def _inline(text: str) -> str:
    """Convert inline markdown (bold/italic/code) to HTML, escaping the rest."""
    text = htmllib.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+?)`", r"<code>\1</code>", text)
    return text


def to_text(content) -> str:
    """
    Normalize LangChain/LangGraph message content into a plain string.
    `.content` can be a str, or a list of content blocks (e.g. when a model
    returns mixed text/tool_use blocks), or occasionally a dict. This makes
    every downstream renderer (html.escape, markdown parser, etc.) safe.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                if "text" in block:
                    parts.append(str(block["text"]))
                elif "content" in block:
                    parts.append(to_text(block["content"]))
                else:
                    parts.append(str(block))
            else:
                parts.append(str(block))
        return "\n".join(p for p in parts if p)
    if isinstance(content, dict):
        if "text" in content:
            return str(content["text"])
        if "content" in content:
            return to_text(content["content"])
        return str(content)
    return str(content)


def render_report_html(md_text: str) -> str:
    """
    Parse a markdown research report into a structured set of styled HTML
    blocks: title, TOC chips, h2/h3 sections, paragraphs, bullet/numbered
    lists, blockquotes, and a highlighted conclusion block.
    """
    if not md_text or not md_text.strip():
        return "<div class='report-body'><i>No report content was returned.</i></div>"

    lines = md_text.replace("\r\n", "\n").split("\n")
    blocks = []
    i, n = 0, len(lines)
    title = None
    toc_entries = []

    while i < n:
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        m = re.match(r"^#\s+(.*)", line)
        if m and title is None:
            title = _inline(m.group(1).strip())
            i += 1
            continue

        m = re.match(r"^##\s+(.*)", line)
        if m:
            heading = _inline(m.group(1).strip())
            toc_entries.append(re.sub(r"<.*?>", "", heading))
            blocks.append(("h2", heading))
            i += 1
            continue

        m = re.match(r"^###\s+(.*)", line)
        if m:
            blocks.append(("h3", _inline(m.group(1).strip())))
            i += 1
            continue

        if line.strip().startswith(">"):
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append(("quote", _inline(" ".join(quote_lines))))
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()))
                i += 1
            blocks.append(("numbered", items))
            continue

        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()))
                i += 1
            blocks.append(("bullets", items))
            continue

        m = re.match(r"^\s*\*?\*?(Conclusion|Verdict|Summary|Bottom Line)\*?\*?\s*:\s*(.*)", line, re.IGNORECASE)
        if m:
            label, rest = m.group(1), m.group(2)
            para_lines = [rest]
            i += 1
            while i < n and lines[i].strip() and not re.match(r"^#{1,3}\s", lines[i]) and not re.match(r"^\s*[-*\d]", lines[i]):
                para_lines.append(lines[i].strip())
                i += 1
            blocks.append(("conclusion", (label.upper(), _inline(" ".join(para_lines).strip()))))
            continue

        para_lines = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^#{1,3}\s", lines[i]) and not re.match(r"^\s*[-*\d]", lines[i]) and not lines[i].strip().startswith(">"):
            para_lines.append(lines[i].strip())
            i += 1
        blocks.append(("p", _inline(" ".join(para_lines))))

    out = []
    if title:
        out.append(f'<div class="report-title">{title}</div>')

    if toc_entries:
        chips = "".join(
            f'<span class="report-toc-item"><b>{idx:02d}</b>{name}</span>'
            for idx, name in enumerate(toc_entries, 1)
        )
        out.append(f'<div class="report-toc">{chips}</div>')

    for kind, payload in blocks:
        if kind == "h2":
            out.append(f'<div class="report-h2">{payload}</div>')
        elif kind == "h3":
            out.append(f'<div class="report-h3">{payload}</div>')
        elif kind == "p":
            out.append(f'<div class="report-body">{payload}</div>')
        elif kind == "quote":
            out.append(f'<div class="report-quote">"{payload}"</div>')
        elif kind == "bullets":
            items = "".join(f"<li>{it}</li>" for it in payload)
            out.append(f'<ul class="report-list">{items}</ul>')
        elif kind == "numbered":
            items = "".join(f"<li>{it}</li>" for it in payload)
            out.append(f'<ul class="report-list numbered">{items}</ul>')
        elif kind == "conclusion":
            label, text = payload
            out.append(
                f'<div class="report-conclusion"><span class="label">{label}</span>{text}</div>'
            )

    return "".join(out) if out else f"<div class='report-body'>{_inline(md_text)}</div>"


def extract_score(critic_text: str):
    """Try to pull a numeric score (e.g. 8/10, 85%, Score: 7) out of critic feedback."""
    if not critic_text:
        return None
    patterns = [
        r"(?:score|rating)\s*[:\-]?\s*(\d{1,3})\s*/\s*10",
        r"(?:score|rating)\s*[:\-]?\s*(\d{1,3})\s*%",
        r"(\d{1,3})\s*/\s*10\b",
        r"(\d{1,3})\s*%",
    ]
    for pat in patterns:
        m = re.search(pat, critic_text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if "/" in pat or "10" in pat.split("%")[0]:
                return min(val * 10, 100) if "/ 10" in pat or "/\\s*10" in pat else min(val, 100)
    return None


def render_critic_html(critic_text: str) -> str:
    score = extract_score(critic_text)

    strengths, issues, other_paras = [], [], []
    lines = critic_text.replace("\r\n", "\n").split("\n")
    mode = None
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        low = line.lower()
        if re.match(r"^#{1,3}\s", line):
            if any(k in low for k in ["strength", "what works", "positive"]):
                mode = "strength"
            elif any(k in low for k in ["weakness", "issue", "improve", "concern", "gap"]):
                mode = "issue"
            else:
                mode = None
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", line):
            text = _inline(re.sub(r"^\s*[-*]\s+", "", line))
            if mode == "issue":
                issues.append(text)
            elif mode == "strength":
                strengths.append(text)
            else:
                if re.search(r"\b(lack|missing|weak|should|could|improve|unclear|vague|outdated)\b", low):
                    issues.append(text)
                else:
                    strengths.append(text)
            i += 1
            continue
        if re.match(r"^(?:score|rating)\s*[:\-]?\s*\d{1,3}\s*(?:/\s*10|%)\s*$", line, re.IGNORECASE):
            i += 1
            continue
        other_paras.append(_inline(line))
        i += 1

    parts = []
    if score is not None:
        pct = max(0, min(score, 100))
        dash = 264 * (1 - pct / 100)
        ring_color = "var(--signal)" if pct >= 70 else ("var(--amber)" if pct >= 45 else "var(--pulse)")
        verdict = "Strong report" if pct >= 70 else ("Needs refinement" if pct >= 45 else "Significant gaps")
        parts.append(f"""
        <div class="score-row">
            <div class="score-dial-wrap">
                <svg viewBox="0 0 100 100">
                    <circle class="score-dial-bg" cx="50" cy="50" r="42"></circle>
                    <circle class="score-dial-fg" cx="50" cy="50" r="42"
                        stroke="{ring_color}"
                        stroke-dasharray="264"
                        stroke-dashoffset="{dash}"></circle>
                </svg>
                <div class="score-dial-num">{pct}</div>
            </div>
            <div class="score-caption">
                <div class="verdict">{verdict}</div>
                <div class="sub">Critic score · out of 100</div>
            </div>
        </div>
        """)

    if other_paras:
        for p in other_paras[:3]:
            parts.append(f'<div class="feedback-body">{p}</div>')

    if strengths:
        items = "".join(f"<li>{s}</li>" for s in strengths)
        parts.append(f'<div class="report-h3" style="color:var(--signal-soft);">Strengths</div><ul class="feedback-list">{items}</ul>')

    if issues:
        items = "".join(f"<li>{s}</li>" for s in issues)
        parts.append(f'<div class="report-h3" style="color:var(--pulse);">Suggested Improvements</div><ul class="feedback-list issues">{items}</ul>')

    if not parts:
        parts.append(f'<div class="feedback-body">{_inline(critic_text)}</div>')

    return "".join(parts)


# ══════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════
for key, default in (("results", {}), ("running", False), ("done", False)):
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero fade-in">
    <div class="hero-tag"><span class="blip"></span>MULTI-AGENT RESEARCH SYSTEM</div>
    <h1><span class="glyph">◈</span> ResearchMind<span class="cursor-blink"></span></h1>
    <p class="hero-sub">Four agents on one trace — <b>search → read → write → critique</b> —
    pass a topic through the pipeline and a sourced, reviewed report comes out the other end.</p>
</div>
<div class="rule"></div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  LAYOUT: CONSOLE (left)  +  SIGNAL RAIL (right)
# ══════════════════════════════════════════════════════════════════════════
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown(_html("""
    <div class="console fade-in">
        <div class="console-head">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            <span class="path">researchmind / new_query</span>
        </div>
        <div class="console-body">
    """), unsafe_allow_html=True)

    st.markdown('<div class="field-label">research topic</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="collapsed",
    )
    run_btn = st.button("RUN PIPELINE", use_container_width=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    chips_html = "".join(f'<span class="chip">{ex}</span>' for ex in examples)
    st.markdown(_html(f"""
    <div class="chip-row">
        <span class="chip-label">try</span>{chips_html}
    </div>
    """), unsafe_allow_html=True)

with col_pipeline:
    r = st.session_state.results
    steps_order = ["search", "reader", "writer", "critic"]
    step_labels = {
        "search": ("Search Agent", "Gathers recent web information"),
        "reader": ("Reader Agent", "Scrapes and extracts deep content"),
        "writer": ("Writer Chain", "Drafts the full research report"),
        "critic": ("Critic Chain", "Reviews and scores the report"),
    }

    def step_state(step_key: str) -> str:
        if step_key in r:
            return "done"
        if st.session_state.running:
            for k in steps_order:
                if k not in r:
                    return "running" if k == step_key else "waiting"
        return "waiting"

    any_running = any(step_state(k) == "running" for k in steps_order)

    st.markdown(
        f'<div class="section-label">Pipeline<span class="count">{len(r)} / 4</span></div>',
        unsafe_allow_html=True,
    )

    rail_html = ['<div class="rail">', f'<div class="rail-wire{" live" if any_running else ""}"><div class="charge"></div></div>']
    for idx, key in enumerate(steps_order, 1):
        state = step_state(key)
        title, desc = step_labels[key]
        state_label = {"waiting": "idle", "running": "running", "done": "complete"}[state]
        state_cls = {"waiting": "state-idle", "running": "state-running", "done": "state-done"}[state]
        rail_html.append(_html(f"""
        <div class="node {state if state != 'waiting' else ''}">
            <div class="node-marker">{NODE_ICONS[key]}</div>
            <div class="node-card">
                <div class="node-top">
                    <span class="node-id">{idx:02d}</span>
                    <span class="node-title">{title}</span>
                    <span class="node-state {state_cls}">{state_label}</span>
                </div>
                <div class="node-desc">{desc}</div>
            </div>
        </div>
        """))
    rail_html.append("</div>")
    st.markdown("".join(rail_html), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  PIPELINE EXECUTION
#  Runs exactly ONE stage per script pass, then reruns — this is what makes
#  the signal rail above accurately reflect which agent is active right now.
# ══════════════════════════════════════════════════════════════════════════
if run_btn:
    if not topic.strip():
        st.warning("Enter a research topic to start the pipeline.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = st.session_state.results
    topic_val = st.session_state.topic_input

    if "search" not in results:
        with st.spinner("Search agent is working…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = to_text(sr["messages"][-1].content)
            st.session_state.results = dict(results)
        st.rerun()

    elif "reader" not in results:
        with st.spinner("Reader agent is scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = to_text(rr["messages"][-1].content)
            st.session_state.results = dict(results)
        st.rerun()

    elif "writer" not in results:
        with st.spinner("Writer is drafting the report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = to_text(writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            }))
            st.session_state.results = dict(results)
        st.rerun()

    elif "critic" not in results:
        with st.spinner("Critic is reviewing the report…"):
            results["critic"] = to_text(critic_chain.invoke({
                "report": results["writer"]
            }))
            st.session_state.results = dict(results)
        st.session_state.running = False
        st.session_state.done = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
#  RESULTS DISPLAY
# ══════════════════════════════════════════════════════════════════════════
r = st.session_state.results

if r:
    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-label">Output<span class="count">{len(r)} / 4 stages</span></div>',
        unsafe_allow_html=True,
    )

    if "search" in r:
        with st.expander("Search results — raw agent output", expanded=False):
            st.markdown(f'<div class="raw-panel">{htmllib.escape(to_text(r["search"]))}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("Scraped content — raw agent output", expanded=False):
            st.markdown(f'<div class="raw-panel">{htmllib.escape(to_text(r["reader"]))}</div>', unsafe_allow_html=True)

    if "writer" in r:
        writer_text = to_text(r["writer"])
        report_html = render_report_html(writer_text)
        st.markdown(_html(f"""
        <div class="report-shell fade-in">
            <div class="report-kicker">
                <div class="report-kicker-left">
                    <div class="report-kicker-mark">{ICON_DOC}</div>
                    <div class="report-kicker-label">Final Research Report</div>
                </div>
                <div class="report-meta">{len(writer_text.split())} words</div>
            </div>
            {report_html}
        </div>
        """), unsafe_allow_html=True)

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
        st.download_button(
            label="Download report (.md)",
            data=writer_text,
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown('<div style="height:1.6rem;"></div>', unsafe_allow_html=True)
        critic_html = render_critic_html(to_text(r["critic"]))
        st.markdown(_html(f"""
        <div class="feedback-shell fade-in">
            <div class="feedback-kicker">
                <div class="feedback-kicker-mark">{ICON_GAUGE}</div>
                <div class="feedback-kicker-label">Critic Feedback</div>
            </div>
            {critic_html}
        </div>
        """), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="notice">
    RESEARCHMIND <span class="sep">◈</span> LANGCHAIN MULTI-AGENT PIPELINE <span class="sep">◈</span> BUILT WITH STREAMLIT
</div>
""", unsafe_allow_html=True)