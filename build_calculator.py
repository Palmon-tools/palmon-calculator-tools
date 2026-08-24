#!/usr/bin/env python3
"""
Build an interactive HTML calculator: enter your CURRENT level for every tech,
it sums up how much Gold/Lumber/Steel/Electricity/TriumphBadge and how much
time is still needed to bring everything to max level.

Reads techtrees_final.json (display names merged in) if present, else falls
back to techtrees_v2.json (raw name_keys). Tech level data is embedded
directly into the HTML so it works by double-click, no server needed.

Output: techtrees_calculator.html
"""
from __future__ import annotations
import json, html
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "techtrees_final.json"
if not SRC.exists():
    SRC = ROOT / "techtrees_v2.json"
TT = json.loads(SRC.read_text(encoding="utf-8"))
ICON_DIR = "tech_icons"

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, sans-serif; }
body { background: #1a1a1e; color: #ddd; padding: 24px; }
.site-header { display: flex; justify-content: flex-end; margin-bottom: 4px; }
.site-brand { text-align: center; }
.site-logo { width: 56px; height: 56px; object-fit: contain; display: block; margin: 0 auto 4px; opacity: 0.9; }
.site-credit { font-size: 11px; color: #888; }
h1 { color: #fff; margin-bottom: 6px; }
h2 { color: #6ee7b7; margin-top: 32px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #333; }
.meta { color: #888; font-size: 13px; margin-bottom: 20px; }
.layer-heading { color: #fbbf24; font-size: 13px; font-weight: 600; margin-top: 18px; margin-bottom: 2px; }
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
.controls { position: sticky; top: 0; background: #1a1a1e; padding: 10px 0; z-index: 10; margin-bottom: 12px; border-bottom: 1px solid #333; }
button { padding: 8px 16px; background: #6ee7b7; color: #111; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; margin-right: 8px; margin-top: 6px; }
button:hover { background: #34d399; }
button.secondary { background: #444; color: #ddd; }
.tree-max-btn { font-size: 12px; padding: 4px 10px; margin-left: 12px; vertical-align: middle; }
.toc a { color: #8ff0d5; text-decoration: none; margin-right: 12px; }
.toc a:hover { text-decoration: underline; }
.totals { display: flex; flex-wrap: wrap; gap: 18px; font-size: 20px; font-weight: 700; margin: 10px 0; }
.totals div span.label { display: block; font-size: 11px; font-weight: 400; color: #888; }
.totals div span.raw { display: block; font-size: 10px; font-weight: 400; color: #666; }
.tree-subtotal { font-size: 12px; color: #999; margin-bottom: 8px; }
.modifiers { background: #24242a; border: 1px solid #3a3a42; border-radius: 6px; padding: 10px 14px; margin: 10px 0; font-size: 13px; }
.modifiers h3 { color: #fbbf24; font-size: 13px; margin-bottom: 8px; }
.modifiers label { display: inline-flex; align-items: center; gap: 6px; margin-right: 18px; margin-bottom: 6px; color: #ccc; }
.modifiers select, .modifiers input[type=number] { background: #16161a; border: 1px solid #444; border-radius: 4px; color: #fff; padding: 3px 6px; }
.modifiers .note { color: #888; font-size: 11px; margin-top: 4px; }
.tree-toggle { cursor: pointer; user-select: none; display: inline-block; width: 16px; color: #6ee7b7; }
.tree-body.collapsed { display: none; }

@media (max-width: 640px) {
  .controls { position: static; }
  body { padding: 10px; }
  h1 { font-size: 18px; }
  h2 { font-size: 15px; margin-top: 22px; }
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
  .tree-max-btn { width: auto; margin-top: 6px; display: block; }
  .toc a { display: inline-block; margin-bottom: 6px; }
  .site-header { justify-content: center; margin-bottom: 8px; }
  .site-logo { width: 40px; height: 40px; }
}
"""

JS_TEMPLATE = """
const LS_KEY = 'palmon_current_levels_v1';
const LS_KEY_MOD = 'palmon_modifiers_v1';
const DATA = __DATA__;

function loadLevels() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); }
  catch(e) { return {}; }
}
function saveLevels(store) {
  localStorage.setItem(LS_KEY, JSON.stringify(store));
}
function loadModifiers() {
  const defaults = { devMaxed: false, title: 0, researchAid: 0, vip: 0, lifetimePass: false, fieldlabSpeedPct1: 0, fieldlabSpeedPct2: 0, helper: '00:00:00', builderClassPct: 0, alliance1: 0, alliance3: 0, alliance4: 0, limudroidPct: 0 };
  try { return { ...defaults, ...JSON.parse(localStorage.getItem(LS_KEY_MOD) || '{}') }; }
  catch(e) { return defaults; }
}
function saveModifiers(mod) {
  localStorage.setItem(LS_KEY_MOD, JSON.stringify(mod));
}
function parseHMS(str) {
  const m = /^(\\d+):(\\d{1,2}):(\\d{1,2})$/.exec((str || '').trim());
  if (!m) return 0;
  return (parseInt(m[1], 10) * 3600) + (parseInt(m[2], 10) * 60) + parseInt(m[3], 10);
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

// remaining cost from (currentLevel+1) to max_level, inclusive
function remainingCost(tech, currentLevel) {
  const totals = {};
  const levelTimes = [];
  for (const lvl of tech.levels) {
    if (lvl.level <= currentLevel || lvl.level === 0) continue;
    for (const [k, v] of Object.entries(lvl.cost || {})) totals[k] = (totals[k] || 0) + v;
    levelTimes.push(lvl.up_time_seconds || 0);
  }
  const time = levelTimes.reduce((a, b) => a + b, 0);
  return { totals, time, levelTimes };
}

// Fieldlab helper Palmon give a flat time reduction per single upgrade (not a %), floored at 0.
function adjustedTimeFromLevels(levelTimes, timeFactor, helperSeconds) {
  return levelTimes.reduce((sum, t) => sum + Math.max(0, t * timeFactor - helperSeconds), 0);
}

// TriumphBadge is not a reducible "resource" — the -2.5% buff never applies to it.
const isReducible = (k) => !k.startsWith('TriumphBadge');

// Gold/Lumber/Steel and Electricity have been observed to receive different discount rates in-game,
// so each resource group gets its own combined factor instead of one shared resFactor.
function factorForResource(k, materialFactor, electricityFactor) {
  if (!isReducible(k)) return 1;
  return k.startsWith('Electricity') ? electricityFactor : materialFactor;
}

function fmtAdjustedResource(k, raw, materialFactor, electricityFactor) {
  const factor = factorForResource(k, materialFactor, electricityFactor);
  const adj = raw * factor;
  const suffix = factor !== 1 ? ` <span class="raw">(raw ${fmtNum(raw)})</span>` : '';
  return `<div class="${resClass(k)}">${k}: ${fmtNum(adj)}${suffix}</div>`;
}
function fmtAdjustedTime(raw, adj) {
  const suffix = adj !== raw ? ` <span class="raw">(raw ${fmtTime(raw)})</span>` : '';
  return `<div class="res-time">Time: ${fmtTime(adj)}${suffix}</div>`;
}

function renderTileRemaining(remaining, materialFactor, electricityFactor, timeFactor, helperSeconds) {
  const entries = Object.entries(remaining.totals);
  if (!entries.length && !remaining.time) return '<div class="row0">max level reached</div>';
  let html = entries.map(([k, v]) => fmtAdjustedResource(k, v, materialFactor, electricityFactor)).join('');
  const adjTime = adjustedTimeFromLevels(remaining.levelTimes, timeFactor, helperSeconds);
  html += fmtAdjustedTime(remaining.time, adjTime);
  return html;
}

function recalcAll() {
  const levels = loadLevels();
  const mod = loadModifiers();
  const resourceReductionPct = (mod.devMaxed ? 2.5 : 0) + (mod.builderClassPct || 0);
  // Verified against real in-game before/after-Warden data: research-speed sources sum ADDITIVELY
  // into one total %, then a single factor is applied — multiplicative per-source compounding
  // was tested and produces impossible (negative) results once many bonuses stack.
  // Development maxed grants its 4 built-in Research Speed techs (4 x +5% = +20% additive).
  // Alliance Tech Buffs (Class 1/3/4) do NOT stack with each other in-game — only the highest applies.
  const allianceBonus = Math.max(mod.alliance1 || 0, mod.alliance3 || 0, mod.alliance4 || 0);
  const speedBonusSum = (mod.devMaxed ? 20 : 0)
    + (mod.vip || 0)
    + (mod.title || 0)
    + (mod.researchAid || 0)
    + (mod.lifetimePass ? 30 : 0)
    + (mod.fieldlabSpeedPct1 || 0)
    + (mod.fieldlabSpeedPct2 || 0)
    + allianceBonus
    + (mod.limudroidPct || 0);
  const baseResFactor = 1 - resourceReductionPct / 100;
  // Electricity is confirmed NOT covered by the -2.5% Development-maxed reduction, but IS covered
  // by other resource-cost reductions such as the Builder Class Buff.
  const materialFactor = baseResFactor;
  const electricityFactor = 1 - (mod.builderClassPct || 0) / 100;
  const timeFactor = 1 / (1 + speedBonusSum / 100);
  const speedBonusPct = Math.round(speedBonusSum * 10) / 10;
  const helperSeconds = parseHMS(mod.helper);
  const grand = { totals: {}, rawTime: 0, adjTime: 0 };
  const treeSubtotals = {};

  document.querySelectorAll('.tile[data-key]').forEach(tile => {
    const key = tile.dataset.key;
    const tech = DATA.techByKey[key];
    const cur = levels[key] ?? 0;
    const rem = remainingCost(tech, cur);
    const adjTime = adjustedTimeFromLevels(rem.levelTimes, timeFactor, helperSeconds);
    tile.querySelector('.remaining-slot').innerHTML = renderTileRemaining(rem, materialFactor, electricityFactor, timeFactor, helperSeconds);
    tile.classList.toggle('done', cur >= tech.max_level);

    for (const [k, v] of Object.entries(rem.totals)) grand.totals[k] = (grand.totals[k] || 0) + v;
    grand.rawTime += rem.time;
    grand.adjTime += adjTime;
    const tl = tile.dataset.tree;
    if (!treeSubtotals[tl]) treeSubtotals[tl] = { totals: {}, rawTime: 0, adjTime: 0 };
    for (const [k, v] of Object.entries(rem.totals)) treeSubtotals[tl].totals[k] = (treeSubtotals[tl].totals[k] || 0) + v;
    treeSubtotals[tl].rawTime += rem.time;
    treeSubtotals[tl].adjTime += adjTime;
  });

  const grandEl = document.getElementById('grand-totals');
  const order = ['Gold', 'Lumber', 'Steel', 'Electricity'];
  const otherKeys = Object.keys(grand.totals).filter(k => !order.includes(k));
  const allKeys = [...order.filter(k => k in grand.totals), ...otherKeys];
  grandEl.innerHTML = allKeys.map(k => {
    const raw = grand.totals[k];
    const factor = factorForResource(k, materialFactor, electricityFactor);
    const adj = raw * factor;
    const rawNote = (factor !== 1) ? `<span class="raw">raw: ${fmtNum(raw)}</span>` : '';
    return `<div><span class="${resClass(k)}">${fmtNum(adj)}</span><span class="label">${k}</span>${rawNote}</div>`;
  }).join('') + (() => {
    const rawTime = grand.rawTime;
    const adjTime = grand.adjTime;
    const rawNote = adjTime !== rawTime ? `<span class="raw">raw: ${fmtTime(rawTime)}</span>` : '';
    return `<div><span class="res-time">${fmtTime(adjTime)}</span><span class="label">Total time (${speedBonusPct}% faster)</span>${rawNote}</div>`;
  })();

  document.querySelectorAll('.tree-subtotal[data-tree]').forEach(el => {
    const tl = el.dataset.tree;
    const st = treeSubtotals[tl] || { totals: {}, rawTime: 0, adjTime: 0 };
    const parts = Object.entries(st.totals).map(([k, v]) => {
      const factor = factorForResource(k, materialFactor, electricityFactor);
      return `${k}: ${fmtNum(v * factor)}`;
    }).join(' · ');
    el.textContent = (parts ? parts + ' · ' : '') + 'Time: ' + fmtTime(st.adjTime);
  });
}

function setLevel(key, value, max) {
  const levels = loadLevels();
  let v = parseInt(value, 10);
  if (isNaN(v) || v < 0) v = 0;
  if (v > max) v = max;
  levels[key] = v;
  saveLevels(levels);
  return v;
}

function stepLevel(key, dir, max) {
  const levels = loadLevels();
  let v = (levels[key] ?? 0) + dir;
  if (v < 0) v = 0;
  if (v > max) v = max;
  levels[key] = v;
  saveLevels(levels);
  return v;
}

function resetAll() {
  if (!confirm('Reset ALL current levels to 0?')) return;
  localStorage.removeItem(LS_KEY);
  location.reload();
}
function maxAll() {
  if (!confirm('Set ALL techs to their max level (nothing left to calculate)?')) return;
  const levels = {};
  for (const key in DATA.techByKey) levels[key] = DATA.techByKey[key].max_level;
  saveLevels(levels);
  location.reload();
}
function maxTree(treeLabel) {
  if (!confirm('Set ALL techs in this tree to their max level?')) return;
  const levels = loadLevels();
  document.querySelectorAll(`.tile[data-tree="${treeLabel}"]`).forEach(tile => {
    const key = tile.dataset.key;
    levels[key] = DATA.techByKey[key].max_level;
  });
  saveLevels(levels);
  location.reload();
}

const LS_KEY_COLLAPSED = 'palmon_collapsed_trees_v1';
function loadCollapsed() {
  try { return JSON.parse(localStorage.getItem(LS_KEY_COLLAPSED) || '{}'); }
  catch(e) { return {}; }
}
function saveCollapsed(state) {
  localStorage.setItem(LS_KEY_COLLAPSED, JSON.stringify(state));
}
function setTreeCollapsed(treeLabel, collapsed) {
  document.querySelector(`.tree-body[data-tree-body="${treeLabel}"]`).classList.toggle('collapsed', collapsed);
  document.querySelector(`.tree-toggle[data-tree-toggle="${treeLabel}"]`).textContent = collapsed ? '\u25b6' : '\u25bc';
  const state = loadCollapsed();
  state[treeLabel] = collapsed;
  saveCollapsed(state);
}
function toggleTree(treeLabel) {
  const body = document.querySelector(`.tree-body[data-tree-body="${treeLabel}"]`);
  setTreeCollapsed(treeLabel, !body.classList.contains('collapsed'));
}
function collapseAllTrees() {
  document.querySelectorAll('.tree-body[data-tree-body]').forEach(body => setTreeCollapsed(body.dataset.treeBody, true));
}
function expandAllTrees() {
  document.querySelectorAll('.tree-body[data-tree-body]').forEach(body => setTreeCollapsed(body.dataset.treeBody, false));
}
function exportLevels() {
  const data = JSON.stringify(loadLevels(), null, 2);
  const blob = new Blob([data], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'current_levels.json';
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
  document.getElementById('mod-research-aid').value = mod.researchAid;
  document.getElementById('mod-vip').value = mod.vip;
  document.getElementById('mod-lifetime-pass').checked = mod.lifetimePass;
  document.getElementById('mod-fieldlab-speed1').value = mod.fieldlabSpeedPct1;
  document.getElementById('mod-fieldlab-speed2').value = mod.fieldlabSpeedPct2;
  document.getElementById('mod-helper').value = mod.helper;
  document.getElementById('mod-builder-class').value = mod.builderClassPct;
  document.getElementById('mod-alliance-1').value = mod.alliance1;
  document.getElementById('mod-alliance-3').value = mod.alliance3;
  document.getElementById('mod-alliance-4').value = mod.alliance4;
  document.getElementById('mod-limudroid').value = mod.limudroidPct;
  document.querySelectorAll('.mod-input').forEach(el => {
    el.addEventListener('input', () => {
      const m = loadModifiers();
      m.devMaxed = document.getElementById('mod-dev-maxed').checked;
      m.title = parseInt(document.getElementById('mod-title').value, 10) || 0;
      m.researchAid = parseInt(document.getElementById('mod-research-aid').value, 10) || 0;
      m.vip = parseInt(document.getElementById('mod-vip').value, 10) || 0;
      m.lifetimePass = document.getElementById('mod-lifetime-pass').checked;
      m.fieldlabSpeedPct1 = parseFloat(document.getElementById('mod-fieldlab-speed1').value) || 0;
      m.fieldlabSpeedPct2 = parseFloat(document.getElementById('mod-fieldlab-speed2').value) || 0;
      m.helper = document.getElementById('mod-helper').value;
      m.builderClassPct = parseInt(document.getElementById('mod-builder-class').value, 10) || 0;
      m.alliance1 = parseInt(document.getElementById('mod-alliance-1').value, 10) || 0;
      m.alliance3 = parseInt(document.getElementById('mod-alliance-3').value, 10) || 0;
      m.alliance4 = parseInt(document.getElementById('mod-alliance-4').value, 10) || 0;
      m.limudroidPct = parseFloat(document.getElementById('mod-limudroid').value) || 0;
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
      const max = parseInt(el.dataset.max, 10);
      const v = stepLevel(key, dir, max);
      const input = document.querySelector(`.lvl-input[data-key="${key}"]`);
      if (input) input.value = v;
      recalcAll();
    });
  });
  const collapsed = loadCollapsed();
  document.querySelectorAll('.tree-body[data-tree-body]').forEach(body => {
    if (collapsed[body.dataset.treeBody]) setTreeCollapsed(body.dataset.treeBody, true);
  });
  recalcAll();
});
"""


def render_tile(tech: dict, tree_label: str) -> str:
    name_key = tech.get("name_key") or "—"
    display = tech.get("display_name") or name_key
    icon_path = tech.get("icon_sprite_path") or ""
    icon_file = icon_path.split("/")[-1] if icon_path else ""
    img_url = f"{ICON_DIR}/{icon_file}.png" if icon_file else ""
    max_lv = tech.get("max_level", 0)

    img_html = (f'<img src="{html.escape(img_url)}" onerror="this.classList.add(&quot;missing&quot;);this.replaceWith(document.createTextNode(&quot;(no icon)&quot;));" alt="{html.escape(display)}">'
                if img_url else '<div class="missing">(no icon)</div>')

    return f"""
    <div class="tile" data-key="{html.escape(name_key)}" data-tree="{html.escape(tree_label)}">
      {img_html}
      <div class="name">{html.escape(display)}</div>
      <div class="lvl-row">
        <label>Level:</label>
        <button type="button" class="lvl-step" data-key="{html.escape(name_key)}" data-dir="-1" data-max="{max_lv}">−</button>
        <input class="lvl-input" type="number" min="0" max="{max_lv}" data-key="{html.escape(name_key)}" data-max="{max_lv}" />
        <button type="button" class="lvl-step" data-key="{html.escape(name_key)}" data-dir="1" data-max="{max_lv}">+</button>
        <label>/ {max_lv}</label>
      </div>
      <div class="remaining remaining-slot"></div>
    </div>
    """


def main():
    tech_by_key = {}
    for tree in TT["trees"]:
        for tech in tree["techs"]:
            nk = tech.get("name_key")
            if not nk:
                continue
            tech_by_key[nk] = {
                "max_level": tech.get("max_level", 0),
                "levels": [
                    {"level": lvl.get("level"), "cost": lvl.get("cost") or {}, "up_time_seconds": lvl.get("up_time_seconds", 0)}
                    for lvl in tech.get("levels", [])
                ],
            }

    parts = []
    parts.append('<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"><title>Palmon Tech Upgrade Calculator</title>')
    parts.append(f"<style>{CSS}</style></head><body>")
    parts.append('<div class="site-header"><div class="site-brand">'
                 '<img class="site-logo" src="Logo.png" alt="Logo" onerror="this.style.display=&quot;none&quot;">'
                 '<div class="site-credit">By MewLuy and Tetsu @S35</div>'
                 '</div></div>')
    parts.append('<div class="controls">')
    parts.append('<h1>Palmon Survival — Tech Upgrade Calculator</h1>')
    parts.append('<div class="meta">Enter your CURRENT level for each tech. Totals show what\'s still needed to reach max level. Saved automatically in your browser.</div>')
    parts.append('<div id="grand-totals" class="totals"></div>')
    parts.append('<div class="modifiers">')
    parts.append('<h3>Global Modifiers</h3>')
    parts.append('<label><input type="checkbox" id="mod-dev-maxed" class="mod-input"> Development tree fully maxed (-2.5% resource cost, +20% Research Speed from its 4 built-in speed techs)</label>')
    parts.append('<label>Title: <select id="mod-title" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="50">Scientist (+50% Research Speed)</option>'
                 '<option value="60">Scientist / Warden — Event (+60% Research Speed)</option>'
                 '</select></label>')
    parts.append('<label>Research Aid: <select id="mod-research-aid" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="10">+10% Research Speed</option>'
                 '<option value="20">+20% Research Speed</option>'
                 '</select></label>')
    parts.append('<label>VIP Level: <select id="mod-vip" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="5">VIP 7 (+5% Research Speed)</option>'
                 '<option value="10">VIP 10 (+10% Research Speed)</option>'
                 '<option value="15">VIP 11 (+15% Research Speed)</option>'
                 '<option value="20">VIP 12 (+20% Research Speed)</option>'
                 '</select></label>')
    parts.append('<label>Fieldlab Helpers total (HH:MM:SS reduction): '
                 '<input type="text" id="mod-helper" class="mod-input" pattern="\\d+:\\d{2}:\\d{2}" placeholder="00:00:00" style="width:90px"></label>')
    parts.append('<label>Limudroid Research Speed Bonus % (depends on Skill Level + Star Level, check its skill tooltip in-game): '
                 '<input type="number" id="mod-limudroid" class="mod-input" min="0" max="100" step="0.01" style="width:70px"></label>')
    parts.append('<label><input type="checkbox" id="mod-lifetime-pass" class="mod-input"> Lifetime Pass (+30% Research Speed)</label>')
    parts.append('<label>Fieldlab 1 speed bonus %: '
                 '<input type="number" id="mod-fieldlab-speed1" class="mod-input" min="0" max="100" step="0.01" style="width:70px"></label>')
    parts.append('<label>Fieldlab 2 speed bonus %: '
                 '<input type="number" id="mod-fieldlab-speed2" class="mod-input" min="0" max="100" step="0.01" style="width:70px"></label>')
    parts.append('<label>Alliance Tech Buff (Class 1, Research Speed): <select id="mod-alliance-1" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="1">+1% Research Speed</option>'
                 '<option value="2">+2% Research Speed</option>'
                 '</select></label>')
    parts.append('<label>Alliance Tech Buff (Class 3, Research Speed): <select id="mod-alliance-3" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="1">+1% Research Speed</option>'
                 '<option value="2">+2% Research Speed</option>'
                 '</select></label>')
    parts.append('<label>Alliance Tech Buff (Class 4, Research Speed): <select id="mod-alliance-4" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="1">+1% Research Speed</option>'
                 '<option value="2">+2% Research Speed</option>'
                 '<option value="3">+3% Research Speed</option>'
                 '</select></label>')
    parts.append('<label>Builder Class Buff: <select id="mod-builder-class" class="mod-input">'
                 '<option value="0">None</option>'
                 '<option value="1">-1% resource cost</option>'
                 '<option value="2">-2% resource cost</option>'
                 '<option value="3">-3% resource cost</option>'
                 '<option value="4">-4% resource cost</option>'
                 '<option value="5">-5% resource cost</option>'
                 '</select></label>')
    parts.append('<div class="note">Research-speed sources sum additively into one total %, then a single time factor is applied (verified against real before/after-Warden in-game data; multiplicative per-source compounding produced impossible results). Electricity is confirmed NOT covered by the -2.5% Development-maxed reduction, but IS covered by other resource-cost discounts like the Builder Class Buff. Both Fieldlab buildings have their own level-dependent speed bonus — enter each in-game value manually. Builder Class Buff is an additional Gold/Lumber/Steel/Electricity cost discount (-1% to -5%) that stacks with the -2.5% Development-maxed reduction (on Gold/Lumber/Steel only). Fieldlab helper reductions are flat and applied per individual upgrade (not per total), after the speed factor, floored at 0.</div>')
    parts.append('</div>')
    parts.append('<button onclick="exportLevels()">Export levels → JSON</button>')
    parts.append('<button class="secondary" onclick="importLevels()">Import JSON</button>')
    parts.append('<button class="secondary" onclick="resetAll()">Reset all to 0</button>')
    parts.append('<button class="secondary" onclick="maxAll()">Set all to max</button>')
    parts.append('<button class="secondary" onclick="collapseAllTrees()">Collapse all</button>')
    parts.append('<button class="secondary" onclick="expandAllTrees()">Expand all</button>')
    parts.append('<div class="toc" style="margin-top:10px;">')
    for tree in TT["trees"]:
        parts.append(f'<a href="#tree_{tree["index"]}">{html.escape(tree.get("display_name") or tree["label"])} ({tree["tech_count"]})</a>')
    parts.append('</div></div>')

    for tree in TT["trees"]:
        label = tree.get("display_name") or tree["label"]
        tree_label_esc = html.escape(tree["label"])
        parts.append(f'<h2 id="tree_{tree["index"]}">'
                     f'<span class="tree-toggle" onclick="toggleTree(\'{tree_label_esc}\')" data-tree-toggle="{tree_label_esc}">\u25bc</span> '
                     f'{tree["index"]}. {html.escape(label)} '
                     f'<button class="secondary tree-max-btn" onclick="maxTree(\'{tree_label_esc}\')">Set tree to max</button></h2>')
        parts.append(f'<div class="tree-subtotal" data-tree="{tree_label_esc}"></div>')
        parts.append(f'<div class="tree-body" data-tree-body="{tree_label_esc}">')

        techs_sorted = sorted(tree["techs"], key=lambda t: (t.get("layers") if t.get("layers") is not None else 999, t.get("tech_type", 0)))
        current_layer = None
        for tech in techs_sorted:
            layer = tech.get("layers")
            if layer != current_layer:
                if current_layer is not None:
                    parts.append('</div>')
                parts.append(f'<div class="layer-heading">Layer {layer}</div>' if layer is not None else '<div class="layer-heading">(no layer)</div>')
                parts.append('<div class="grid">')
                current_layer = layer
            parts.append(render_tile(tech, tree["label"]))
        parts.append('</div>')
        parts.append('</div>')

    js = JS_TEMPLATE.replace("__DATA__", json.dumps({"techByKey": tech_by_key}, ensure_ascii=False))
    parts.append(f"<script>{js}</script></body></html>")

    out_path = ROOT / "techtrees_calculator.html"
    out_path.write_text("".join(parts), encoding="utf-8")
    print(f"source data: {SRC.name}")
    print(f"wrote {out_path.name}  ({out_path.stat().st_size:,} bytes)")
    print(f"open it directly in a browser — no server needed.")


if __name__ == "__main__":
    main()
