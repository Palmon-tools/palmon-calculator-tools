#!/usr/bin/env python3
"""
Build an interactive HTML calculator for BUILDING upgrades: enter your CURRENT
level for every building, it sums up how much Gold/Lumber/Steel/Electricity and
how much time is still needed to bring everything to max level.

Reads buildings_final.json (display names merged in) if present, else falls
back to buildings_v2.json (raw name_keys). Data is embedded directly into the
HTML so it works by double-click, no server needed.

Output: buildings_calculator.html
"""
from __future__ import annotations
import json, html
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "buildings_final.json"
if not SRC.exists():
    SRC = ROOT / "buildings_v2.json"
BD = json.loads(SRC.read_text(encoding="utf-8"))
ICON_DIR = "building_icons"
EXCLUDED_BUILDINGS = {"Generator", "Brick Kiln", "Super Brick Kiln", "Holy Tower", "Mithril Workshop", "Super Mithril Workshop"}
BD["buildings"] = [b for b in BD["buildings"] if b.get("display_name") not in EXCLUDED_BUILDINGS]

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, sans-serif; }
body { background: #1a1a1e; color: #ddd; padding: 24px; }
.site-header { display: flex; justify-content: flex-end; margin-bottom: 4px; }
.site-brand { text-align: center; }
.site-logo { width: 56px; height: 56px; object-fit: contain; display: block; margin: 0 auto 4px; opacity: 0.9; }
.site-credit { font-size: 11px; color: #888; }
h1 { color: #fff; margin-bottom: 6px; }
.meta { color: #888; font-size: 13px; margin-bottom: 20px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-top: 12px; }
.tile { background: #2a2a30; border: 1px solid #3a3a42; border-radius: 8px; padding: 10px; }
.tile.done { border-color: #34d399; }
.tile img { width: 56px; height: 56px; object-fit: contain; background: #16161a; border-radius: 4px; float: left; margin-right: 8px; }
.tile img.missing { display: flex; align-items: center; justify-content: center; color: #666; font-size: 9px; text-align: center; }
.tile .name { font-size: 13px; font-weight: 600; color: #fff; }
.tile .meta-line { font-size: 10px; color: #888; }
.tile .lvl-row { clear: both; padding-top: 8px; display: flex; align-items: center; gap: 6px; }
.tile .lvl-row label { font-size: 11px; color: #999; }
.tile .lvl-row input { width: 55px; padding: 4px 6px; background: #16161a; border: 1px solid #444; border-radius: 4px; color: #fff; font-size: 13px; }
.tile .lvl-step { width: 26px; height: 26px; padding: 0; background: #16161a; border: 1px solid #444; border-radius: 4px; color: #fff; font-size: 15px; line-height: 1; cursor: pointer; }
.tile .lvl-step:hover { background: #2a2a32; }
.tile .remaining { margin-top: 6px; font-size: 11px; line-height: 1.5; }
.tile .remaining .row0 { color: #6ee7b7; }
.res-gold { color: #fbbf24; } .res-lumber { color: #a78bfa; } .res-steel { color: #94a3b8; }
.res-elec { color: #38bdf8; } .res-badge { color: #f472b6; } .res-time { color: #6ee7b7; }
.tile .details-toggle { margin-top: 8px; background: none; border: 1px solid #444; color: #9ca3af; font-size: 10px; padding: 3px 8px; width: auto; border-radius: 4px; }
.tile .details-toggle:hover { background: #333; }
.tile .level-breakdown { margin-top: 8px; border-top: 1px solid #3a3a42; padding-top: 6px; display: none; max-height: 260px; overflow-y: auto; }
.tile .level-breakdown.open { display: block; }
.level-row { font-size: 10.5px; padding: 4px 0; border-bottom: 1px solid #303038; }
.level-row .lvl-num { color: #fff; font-weight: 700; }
.level-row .req { color: #f59e0b; font-size: 10px; margin-top: 2px; }
.level-row .res-line { display: inline-block; margin-right: 8px; }
.controls { position: sticky; top: 0; background: #1a1a1e; padding: 10px 0; z-index: 10; margin-bottom: 12px; border-bottom: 1px solid #333; }
button { padding: 8px 16px; background: #6ee7b7; color: #111; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; margin-right: 8px; margin-top: 6px; }
button:hover { background: #34d399; }
button.secondary { background: #444; color: #ddd; }
.totals { display: flex; flex-wrap: wrap; gap: 18px; font-size: 20px; font-weight: 700; margin: 10px 0; }
.totals div span.label { display: block; font-size: 11px; font-weight: 400; color: #888; }
.totals div span.raw { display: block; font-size: 10px; font-weight: 400; color: #666; }
.modifiers { background: #24242a; border: 1px solid #3a3a42; border-radius: 6px; padding: 10px 14px; margin: 10px 0; font-size: 13px; }
.modifiers h3 { color: #fbbf24; font-size: 13px; margin-bottom: 8px; }
.modifiers label { display: inline-flex; align-items: center; gap: 6px; margin-right: 18px; margin-bottom: 6px; color: #ccc; }
.modifiers select, .modifiers input[type=number] { background: #16161a; border: 1px solid #444; border-radius: 4px; color: #fff; padding: 3px 6px; }
.modifiers .note { color: #888; font-size: 11px; margin-top: 4px; }

@media (max-width: 640px) {
  .controls { position: static; }
  body { padding: 10px; }
  h1 { font-size: 18px; }
  .grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
  .tile { padding: 8px; }
  .tile img { width: 40px; height: 40px; margin-right: 6px; }
  .tile .name { font-size: 12px; }
  .tile .lvl-row input { width: 44px; font-size: 16px; }
  .tile .lvl-step { width: 32px; height: 32px; font-size: 18px; }
  .totals { font-size: 15px; gap: 10px; }
  .modifiers label { display: flex; margin-right: 0; width: 100%; }
  .modifiers select, .modifiers input[type=number], .modifiers input[type=text] { flex: 1; min-width: 0; font-size: 16px; }
  button { padding: 10px 14px; font-size: 14px; margin-bottom: 6px; width: 100%; }
  .tile .details-toggle { width: 100%; padding: 6px; }
  .tile .level-breakdown { max-height: 200px; }
  .site-header { justify-content: center; margin-bottom: 8px; }
  .site-logo { width: 40px; height: 40px; }
}
"""

JS_TEMPLATE = """
const LS_KEY = 'palmon_building_levels_v1';
const LS_KEY_MOD = 'palmon_building_modifiers_v1';
const DATA = __DATA__;

function loadLevels() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); }
  catch(e) { return {}; }
}
function saveLevels(store) {
  localStorage.setItem(LS_KEY, JSON.stringify(store));
}
function loadModifiers() {
  const defaults = { devMaxed: false, title: 0, constructionAid: 0, vip: 0, lifetimePass: false, monthlyPass: false, builderClassPct: 0, masterBuilderPct: 0 };
  try { return { ...defaults, ...JSON.parse(localStorage.getItem(LS_KEY_MOD) || '{}') }; }
  catch(e) { return defaults; }
}
function saveModifiers(mod) {
  localStorage.setItem(LS_KEY_MOD, JSON.stringify(mod));
}
function fmtNum(n) { return n ? Math.round(n).toLocaleString('en-US') : '0'; }
function fmtTime(totalSeconds) {
  if (!totalSeconds) return '0s';
  let s = totalSeconds;
  const d = Math.floor(s / 86400); s -= d * 86400;
  const h = Math.floor(s / 3600); s -= h * 3600;
  const m = Math.floor(s / 60); s -= m * 60;
  const parts = [];
  if (d) parts.push(d + 'd');
  if (h) parts.push(h + 'h');
  if (m && !d) parts.push(m + 'm');
  if (!d && !h && !m) parts.push(Math.round(s) + 's');
  return parts.join(' ');
}

const RESOURCE_CLASS = { Gold: 'res-gold', Lumber: 'res-lumber', Steel: 'res-steel', Electricity: 'res-elec' };
function resClass(key) { return RESOURCE_CLASS[key.split('(')[0]] || 'res-badge'; }
const EXCLUDED_OVERVIEW_RESOURCES = [];
const RESOURCE_NAMES = { resource_42: 'Pharaoh Coin' };
function resLabel(key) { return RESOURCE_NAMES[key] || key; }

// remaining cost from (currentLevel+1) to max_level, inclusive
function remainingCost(building, currentLevel) {
  const totals = {};
  let time = 0;
  const levelTimes = [];
  for (const lvl of building.levels) {
    if (lvl.level <= currentLevel || lvl.level === 0) continue;
    for (const [k, v] of Object.entries(lvl.cost || {})) totals[k] = (totals[k] || 0) + v;
    time += lvl.up_time_seconds || 0;
    levelTimes.push(lvl.up_time_seconds || 0);
  }
  return { totals, time, levelTimes };
}

function adjustedTimeFromLevels(levelTimes, timeFactor) {
  return levelTimes.reduce((sum, t) => sum + t * timeFactor, 0);
}

function fmtAdjustedResource(k, raw, resFactor) {
  const adj = raw * resFactor;
  const suffix = resFactor !== 1 ? ` <span class="raw">(raw ${fmtNum(raw)})</span>` : '';
  return `<div class="${resClass(k)}">${resLabel(k)}: ${fmtNum(adj)}${suffix}</div>`;
}
function fmtAdjustedTime(raw, adj) {
  const suffix = adj !== raw ? ` <span class="raw">(raw ${fmtTime(raw)})</span>` : '';
  return `<div class="res-time">Time: ${fmtTime(adj)}${suffix}</div>`;
}

function renderTileRemaining(remaining, resFactor, timeFactor) {
  const entries = Object.entries(remaining.totals);
  if (!entries.length && !remaining.time) return '<div class="row0">max level reached</div>';
  let html = entries.map(([k, v]) => fmtAdjustedResource(k, v, resFactor)).join('');
  const adjTime = adjustedTimeFromLevels(remaining.levelTimes, timeFactor);
  html += fmtAdjustedTime(remaining.time, adjTime);
  return html;
}

function renderLevelBreakdown(building, currentLevel, resFactor, timeFactor) {
  const upcoming = building.levels.filter(lvl => lvl.level > currentLevel && lvl.level !== 0);
  if (!upcoming.length) return '<div class="level-row">max level reached</div>';
  return upcoming.map(lvl => {
    const resLine = Object.entries(lvl.cost || {}).map(([k, v]) => {
      const adj = v * (k.startsWith('Gold') || k.startsWith('Lumber') || k.startsWith('Steel') || k.startsWith('Electricity') ? resFactor : 1);
      return `<span class="res-line ${resClass(k)}">${resLabel(k)}: ${fmtNum(adj)}</span>`;
    }).join('');
    const time = (lvl.up_time_seconds || 0) * timeFactor;
    const reqs = (lvl.prerequisite_buildings || []);
    const reqLine = reqs.length
      ? `<div class="req">Requires: ${reqs.map(r => `${r.display_name || r.name_key || ('build_type ' + r.build_type)} Lv.${r.at_level}`).join(', ')}</div>`
      : '';
    return `<div class="level-row"><span class="lvl-num">Lv.${lvl.level_label}</span> — ${resLine}<span class="res-time">Time: ${fmtTime(time)}</span>${reqLine}</div>`;
  }).join('');
}

function toggleDetails(btn) {
  const tile = btn.closest('.tile');
  const panel = tile.querySelector('.level-breakdown');
  const open = panel.classList.toggle('open');
  btn.textContent = open ? 'Hide level-by-level details \u25b2' : 'Show level-by-level details \u25bc';
}

function recalcAll() {
  const levels = loadLevels();
  const mod = loadModifiers();
  const resourceDiscountPct = (mod.devMaxed ? 2.5 : 0) + (mod.builderClassPct || 0);
  const resFactor = 1 - resourceDiscountPct / 100;
  // Verified against real in-game timers (raw 13d21h20m -> buffed 5d9h16m with Dev+VIP9+Lifetime+Monthly):
  // building-speed sources compound sequentially/multiplicatively (each is its own divisor).
  const speedSources = [mod.devMaxed ? 20 : 0, mod.title || 0, mod.constructionAid || 0, mod.vip || 0,
    mod.lifetimePass ? 30 : 0, mod.monthlyPass ? 10 : 0];
  const speedFactorProduct = speedSources.reduce((p, v) => p * (1 + v / 100), 1);
  // Master Builder reduces build TIME directly (up to -25%), not resource cost — applied as its own
  // multiplier on top of the speed-sources factor.
  const timeFactor = (1 / speedFactorProduct) * (1 - (mod.masterBuilderPct || 0) / 100);
  const speedBonusPct = Math.round((speedFactorProduct - 1) * 1000) / 10;
  const grand = { totals: {}, rawTime: 0, adjTime: 0 };

  document.querySelectorAll('.tile[data-key]').forEach(tile => {
    const key = tile.dataset.key;
    const building = DATA.buildingByKey[key];
    const cur = levels[key] ?? 0;
    const rem = remainingCost(building, cur);
    const adjTime = adjustedTimeFromLevels(rem.levelTimes, timeFactor);
    tile.querySelector('.remaining-slot').innerHTML = renderTileRemaining(rem, resFactor, timeFactor);
    tile.classList.toggle('done', cur >= building.max_level);
    tile.querySelector('.level-breakdown').innerHTML = renderLevelBreakdown(building, cur, resFactor, timeFactor);

    for (const [k, v] of Object.entries(rem.totals)) grand.totals[k] = (grand.totals[k] || 0) + v;
    grand.rawTime += rem.time;
    grand.adjTime += adjTime;
  });

  const grandEl = document.getElementById('grand-totals');
  const order = ['Gold', 'Lumber', 'Steel', 'Electricity'];
  const otherKeys = Object.keys(grand.totals).filter(k => !order.includes(k) && !EXCLUDED_OVERVIEW_RESOURCES.includes(k));
  const allKeys = [...order.filter(k => k in grand.totals), ...otherKeys];
  grandEl.innerHTML = allKeys.map(k => {
    const raw = grand.totals[k];
    const adj = raw * resFactor;
    const rawNote = (resFactor !== 1) ? `<span class="raw">raw: ${fmtNum(raw)}</span>` : '';
    return `<div><span class="${resClass(k)}">${fmtNum(adj)}</span><span class="label">${resLabel(k)}</span>${rawNote}</div>`;
  }).join('') + (() => {
    const rawTime = grand.rawTime;
    const adjTime = grand.adjTime;
    const rawNote = adjTime !== rawTime ? `<span class="raw">raw: ${fmtTime(rawTime)}</span>` : '';
    return `<div><span class="res-time">${fmtTime(adjTime)}</span><span class="label">Total time (${speedBonusPct}% faster)</span>${rawNote}</div>`;
  })();
}

function setLevel(key, value, max) {
  const levels = loadLevels();
  let v = Math.round(parseFloat(value) * 10) / 10;
  if (isNaN(v) || v < 0) v = 0;
  const base = Math.floor(v);
  // Below level 30 only whole levels exist; from 30+ only .1-.4 sub-stages exist (no .5+).
  if (base < 30) {
    v = Math.round(v);
  } else {
    let frac = Math.round((v - base) * 10);
    if (frac > 4) frac = 4;
    v = base + frac / 10;
  }
  if (v > max) v = max;
  levels[key] = v;
  saveLevels(levels);
  return v;
}

// Step to the next/prev level that actually exists in this building's real level sequence
// (handles the 29 -> 30 -> 30.1..30.4 -> 31 stepping correctly across sub-stage boundaries).
function stepLevel(key, dir) {
  const building = DATA.buildingByKey[key];
  const sequence = building.levels.map(l => l.level).filter(l => l !== 0).sort((a, b) => a - b);
  const levels = loadLevels();
  const current = levels[key] ?? 0;
  let next = current;
  if (dir > 0) {
    next = sequence.find(l => l > current + 1e-9);
    if (next === undefined) next = current;
  } else {
    const below = sequence.filter(l => l < current - 1e-9);
    next = below.length ? below[below.length - 1] : 0;
  }
  levels[key] = next;
  saveLevels(levels);
  return next;
}

function resetAll() {
  if (!confirm('Reset ALL current levels to 0?')) return;
  localStorage.removeItem(LS_KEY);
  location.reload();
}
function maxAll() {
  if (!confirm('Set ALL buildings to their max level (nothing left to calculate)?')) return;
  const levels = {};
  for (const key in DATA.buildingByKey) levels[key] = DATA.buildingByKey[key].max_level;
  saveLevels(levels);
  location.reload();
}
function exportLevels() {
  const data = JSON.stringify(loadLevels(), null, 2);
  const blob = new Blob([data], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'current_building_levels.json';
  a.click();
  URL.revokeObjectURL(url);
}
function importLevels() {
  const inp = document.createElement('input');
  inp.type = 'file'; inp.accept = 'application/json';
  inp.onchange = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const rd = new FileReader();
    rd.onload = () => {
      try {
        saveLevels(JSON.parse(rd.result));
        location.reload();
      } catch(e) { alert('Bad file: ' + e); }
    };
    rd.readAsText(f);
  };
  inp.click();
}

document.addEventListener('DOMContentLoaded', () => {
  const levels = loadLevels();
  const mod = loadModifiers();
  document.getElementById('mod-dev-maxed').checked = mod.devMaxed;
  document.getElementById('mod-title').value = mod.title;
  document.getElementById('mod-construction-aid').value = mod.constructionAid;
  document.getElementById('mod-vip').value = mod.vip;
  document.getElementById('mod-lifetime-pass').checked = mod.lifetimePass;
  document.getElementById('mod-monthly-pass').checked = mod.monthlyPass;
  document.getElementById('mod-builder-class').value = mod.builderClassPct;
  document.getElementById('mod-master-builder').value = mod.masterBuilderPct;
  document.querySelectorAll('.mod-input').forEach(el => {
    el.addEventListener('input', () => {
      const m = loadModifiers();
      m.devMaxed = document.getElementById('mod-dev-maxed').checked;
      m.title = parseInt(document.getElementById('mod-title').value, 10) || 0;
      m.constructionAid = parseInt(document.getElementById('mod-construction-aid').value, 10) || 0;
      m.vip = parseInt(document.getElementById('mod-vip').value, 10) || 0;
      m.lifetimePass = document.getElementById('mod-lifetime-pass').checked;
      m.monthlyPass = document.getElementById('mod-monthly-pass').checked;
      m.builderClassPct = parseInt(document.getElementById('mod-builder-class').value, 10) || 0;
      m.masterBuilderPct = parseInt(document.getElementById('mod-master-builder').value, 10) || 0;
      saveModifiers(m);
      recalcAll();
    });
  });

  document.querySelectorAll('.lvl-input').forEach(el => {
    const key = el.dataset.key;
    const max = parseInt(el.dataset.max, 10);
    el.value = levels[key] ?? 0;
    el.addEventListener('input', () => {
      el.value = setLevel(key, el.value, max);
      recalcAll();
    });
  });

  document.querySelectorAll('.lvl-step').forEach(el => {
    el.addEventListener('click', () => {
      const key = el.dataset.key;
      const dir = parseInt(el.dataset.dir, 10);
      const v = stepLevel(key, dir);
      const input = document.querySelector(`.lvl-input[data-key="${key}"]`);
      if (input) input.value = v;
      recalcAll();
    });
  });
  recalcAll();
});
"""


def render_tile(b: dict) -> str:
    name_key = b.get("name_key") or f"build_type_{b['build_type']}"
    display = b.get("display_name") or name_key
    icon_path = b.get("icon_sprite_path") or ""
    icon_file = icon_path.split("/")[-1] if icon_path else ""
    img_url = f"{ICON_DIR}/{icon_file}.png" if icon_file else ""
    max_lv = b.get("max_level", 0)
    has_sub_levels = any(isinstance(lvl.get("level"), float) and not lvl["level"].is_integer() for lvl in b.get("levels", []))
    step = "0.1" if has_sub_levels else "1"
    hint = ('<div class="meta-line">Lv.30+ has sub-stages: use 30.1/30.2/30.3/30.4 for 30-1..30-4</div>'
            if has_sub_levels else "")

    img_html = (f'<img src="{html.escape(img_url)}" onerror="this.classList.add(&quot;missing&quot;);this.replaceWith(document.createTextNode(&quot;(no icon)&quot;));" alt="{html.escape(display)}">'
                if img_url else '<div class="missing">(no icon)</div>')

    return f"""
    <div class="tile" data-key="{html.escape(name_key)}">
      {img_html}
      <div class="name">{html.escape(display)}</div>
      {hint}
      <div class="lvl-row">
        <label>Level:</label>
        <button type="button" class="lvl-step" data-key="{html.escape(name_key)}" data-dir="-1">−</button>
        <input class="lvl-input" type="number" min="0" max="{max_lv}" step="{step}" data-key="{html.escape(name_key)}" data-max="{max_lv}" />
        <button type="button" class="lvl-step" data-key="{html.escape(name_key)}" data-dir="1">+</button>
        <label>/ {max_lv}</label>
      </div>
      <div class="remaining remaining-slot"></div>
      <button class="details-toggle" onclick="toggleDetails(this)">Show level-by-level details ▼</button>
      <div class="level-breakdown"></div>
    </div>
    """


def main():
    building_by_key = {}
    for b in BD["buildings"]:
        nk = b.get("name_key") or f"build_type_{b['build_type']}"
        building_by_key[nk] = {
            "max_level": b.get("max_level", 0),
            "levels": [
                {
                    "level": lvl.get("level"),
                    "level_label": lvl.get("level_label") or str(lvl.get("level")),
                    "cost": lvl.get("cost") or {},
                    "up_time_seconds": lvl.get("up_time_seconds", 0),
                    "prerequisite_buildings": [
                        {
                            "build_type": p.get("build_type"),
                            "name_key": p.get("name_key"),
                            "display_name": p.get("display_name"),
                            "at_level": p.get("at_level"),
                        }
                        for p in (lvl.get("prerequisite_buildings") or [])
                    ],
                }
                for lvl in b.get("levels", [])
            ],
        }

    parts = []
    parts.append('<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"><title>Palmon Building Upgrade Calculator</title>')
    parts.append(f"<style>{CSS}</style></head><body>")
    parts.append('<div class="site-header"><div class="site-brand">'
                 '<img class="site-logo" src="Logo.png" alt="Logo" onerror="this.style.display=&quot;none&quot;">'
                 '<div class="site-credit">By MewLuy and Tetsu @S35</div>'
                 '</div></div>')
    parts.append('<div class="controls">')
    parts.append('<h1>Palmon Survival — Building Upgrade Calculator</h1>')
    parts.append('<div class="meta">Enter your CURRENT level for each building. Totals show what\'s still needed to reach max level. Saved automatically in your browser.</div>')
    parts.append('<div id="grand-totals" class="totals"></div>')
    parts.append('<div class="modifiers">')
    parts.append('<h3>Global Modifiers</h3>')
    parts.append('<label><input type="checkbox" id="mod-dev-maxed" class="mod-input"> Development maxed (+20% Building Speed, -2.5% Resource Cost)</label>')
    parts.append('<label>Title: <select id="mod-title" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="60">Warden (+60% Building Speed)</option>'
                 '<option value="50">Architect (+50% Building Speed)</option>'
                 '</select></label>')
    parts.append('<label>Construction Aid: <select id="mod-construction-aid" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="10">+10% Building Speed</option>'
                 '<option value="20">+20% Building Speed</option>'
                 '</select></label>')
    parts.append('<label>VIP Level: <select id="mod-vip" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="5">VIP 3 (+5% Building Speed)</option>'
                 '<option value="10">VIP 5 (+10% Building Speed)</option>'
                 '<option value="20">VIP 6 (+20% Building Speed)</option>'
                 '<option value="30">VIP 8 (+30% Building Speed)</option>'
                 '<option value="50">VIP 9 (+50% Building Speed)</option>'
                 '</select></label>')
    parts.append('<label><input type="checkbox" id="mod-lifetime-pass" class="mod-input"> Lifetime Pass (+30% Building Speed)</label>')
    parts.append('<label><input type="checkbox" id="mod-monthly-pass" class="mod-input"> Monthly Pass (+10% Building Speed)</label>')
    parts.append('<label>Builder Class Buff: <select id="mod-builder-class" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="1">-1% resource cost</option>'
                 '<option value="2">-2% resource cost</option>'
                 '<option value="3">-3% resource cost</option>'
                 '<option value="4">-4% resource cost</option>'
                 '<option value="5">-5% resource cost</option>'
                 '</select></label>')
    parts.append('<label>Master Builder: <select id="mod-master-builder" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="5">-5% Build Time</option>'
                 '<option value="10">-10% Build Time</option>'
                 '<option value="15">-15% Build Time</option>'
                 '<option value="20">-20% Build Time</option>'
                 '<option value="25">-25% Build Time</option>'
                 '</select></label>')
    parts.append('<div class="note">Building-speed sources (Development maxed, Title, Construction Aid, VIP, Lifetime Pass, Monthly Pass) compound sequentially/multiplicatively into a single time factor (verified against real in-game timers). Master Builder reduces build time directly (up to -25%) on top of that, it does NOT discount resource cost. Development maxed and Builder Class Buff discount resource cost and stack additively. Note: Desert-tech research that reduces Desert-building time/resource cost is not yet factored into this calculator.</div>')
    parts.append('</div>')
    parts.append('<button onclick="exportLevels()">Export levels → JSON</button>')
    parts.append('<button class="secondary" onclick="importLevels()">Import JSON</button>')
    parts.append('<button class="secondary" onclick="resetAll()">Reset all to 0</button>')
    parts.append('<button class="secondary" onclick="maxAll()">Set all to max</button>')
    parts.append('</div>')

    parts.append('<div class="grid">')
    for b in sorted(BD["buildings"], key=lambda x: x["build_type"]):
        parts.append(render_tile(b))
    parts.append('</div>')

    data_json = json.dumps({"buildingByKey": building_by_key}, ensure_ascii=False)
    js = JS_TEMPLATE.replace("__DATA__", data_json)
    parts.append(f"<script>{js}</script>")
    parts.append("</body></html>")

    out_path = ROOT / "buildings_calculator.html"
    out_path.write_text("".join(parts), encoding="utf-8")
    print(f"source data: {SRC.name}")
    print(f"wrote {out_path.name}  ({out_path.stat().st_size:,} bytes)")
    print("open it directly in a browser — no server needed.")


if __name__ == "__main__":
    main()
