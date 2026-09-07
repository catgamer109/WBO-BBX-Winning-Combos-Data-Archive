(function () {
  'use strict';

  const DATA_PATH = '../compiled_data/extracted_data.json';
  const PARTS_PATH = '../wbo_bbx_parts.json';

  const $ = (sel) => document.querySelector(sel);

  const els = {
    viewMode: $('#viewMode'),
    placementFilter: $('#placementFilter'),
    rankedFilter: $('#rankedFilter'),
    topN: $('#topN'),
    searchInput: $('#searchInput'),
    rankingList: $('#rankingList'),
    sidebarStats: $('#sidebarStats'),
  };

  let rawData = [];

  // Lookup maps built from wbo_bbx_parts.json
  // Maps full bit name (lowercase) -> abbreviation
  let bitNameToAbbr = {};
  // Maps blade alias (lowercase) -> canonical Name
  let bladeAliasToName = {};

  async function init() {
    try {
      const [dataResp, partsResp] = await Promise.all([
        fetch(DATA_PATH),
        fetch(PARTS_PATH),
      ]);
      if (!dataResp.ok) throw new Error(`Data: HTTP ${dataResp.status}`);
      if (!partsResp.ok) throw new Error(`Parts: HTTP ${partsResp.status}`);

      rawData = await dataResp.json();
      const parts = await partsResp.json();
      buildLookups(parts);
      wireUp();
      update();
    } catch (err) {
      els.rankingList.innerHTML = `<li style="padding:20px;color:#f66;">Failed to load data: ${err.message}</li>`;
    }
  }

  function buildLookups(parts) {
    // Bits: full name -> abbreviation
    if (parts.Bits) {
      for (const bit of parts.Bits) {
        bitNameToAbbr[bit.Name.toLowerCase()] = bit.Abbreviation;
      }
    }

    // Blades: alias -> canonical Name
    if (parts.Blades) {
      for (const blade of parts.Blades) {
        // Map the Name to itself
        bladeAliasToName[blade.Name.toLowerCase()] = blade.Name;
        // Map each alias to the canonical Name
        if (blade.Aliases) {
          for (const alias of blade.Aliases) {
            bladeAliasToName[alias.toLowerCase()] = blade.Name;
          }
        }
      }
    }
  }

  /**
   * Abbreviate a full combo string like "DranSword 3-60Flat" -> "DranSword 3-60F"
   * or "Wizard Arrow 4-80Ball" -> "WizardArrow 4-80B"
   */
  function abbreviateCombo(str) {
    str = str.trim();

    // Find the ratchet pattern (digits-digits) to split blade from ratchet+bit
    const ratchetMatch = str.match(/^(.+?)\s+(\d+-\d+)(.*)$/);
    if (!ratchetMatch) return str;

    let bladeRaw = ratchetMatch[1].trim();
    const ratchet = ratchetMatch[2];
    let bitRaw = ratchetMatch[3].trim();

    // Abbreviate the blade: look up alias -> canonical name
    const bladeLower = bladeRaw.toLowerCase();
    if (bladeAliasToName[bladeLower]) {
      bladeRaw = bladeAliasToName[bladeLower];
    }

    // Abbreviate the bit: look up full name -> abbreviation
    if (bitRaw) {
      const bitLower = bitRaw.toLowerCase();
      if (bitNameToAbbr[bitLower]) {
        bitRaw = bitNameToAbbr[bitLower];
      }
    }

    return `${bladeRaw} ${ratchet}${bitRaw}`;
  }

  function wireUp() {
    [els.viewMode, els.placementFilter, els.rankedFilter, els.topN].forEach(
      (el) => el.addEventListener('change', update)
    );
    let t;
    els.searchInput.addEventListener('input', () => { clearTimeout(t); t = setTimeout(update, 150); });
  }

  function parseCombo(str) {
    str = str.trim();
    const m = str.match(/^(.+?)\s+(\d+-\d+)(.+)$/);
    if (!m) return { blade: str, ratchet: '', bit: '', full: str };
    return { blade: m[1].trim(), ratchet: m[2].trim(), bit: m[3].trim(), full: str };
  }

  function update() {
    const mode = els.viewMode.value;
    const placement = els.placementFilter.value;
    const ranked = els.rankedFilter.value;
    const topN = parseInt(els.topN.value, 10);
    const search = els.searchInput.value.trim().toLowerCase();

    // Count
    const counts = {};
    let totalEntries = 0;

    for (const event of rawData) {
      if (ranked !== 'all' && event.ranked_status !== ranked) continue;
      if (!event.placements) continue;
      for (const p of event.placements) {
        if (placement !== 'all' && p.rank !== placement) continue;
        if (!p.combos || !Array.isArray(p.combos)) continue;
        for (const combo of p.combos) {
          // Abbreviate first, then parse
          const abbreviated = abbreviateCombo(combo);
          const parsed = parseCombo(abbreviated);
          let key;
          switch (mode) {
            case 'blades': key = parsed.blade; break;
            case 'ratchets': key = parsed.ratchet; break;
            case 'bits': key = parsed.bit; break;
            default: key = parsed.full;
          }
          if (!key) continue;
          counts[key] = (counts[key] || 0) + 1;
          totalEntries++;
        }
      }
    }

    // Sort & filter
    let items = Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);

    if (search) {
      items = items.filter((d) => d.name.toLowerCase().includes(search));
    }

    const totalUnique = items.length;
    if (topN > 0) items = items.slice(0, topN);

    const maxCount = items.length > 0 ? items[0].count : 1;

    // Render list
    els.rankingList.innerHTML = items.map((d, i) => {
      const rank = i + 1;
      const barPct = ((d.count / maxCount) * 100).toFixed(1);
      let rankClass = '';
      if (rank === 1) rankClass = 'rank-item__rank--1';
      else if (rank === 2) rankClass = 'rank-item__rank--2';
      else if (rank === 3) rankClass = 'rank-item__rank--3';

      return `<li class="rank-item">
        <span class="rank-item__rank ${rankClass}">${rank}</span>
        <span class="rank-item__name" title="${esc(d.name)}">${esc(d.name)}</span>
        <span class="rank-item__count">${d.count}</span>
        <span class="rank-item__bar-wrap"><div class="rank-item__bar"><div class="rank-item__bar-fill" style="width:${barPct}%"></div></div></span>
      </li>`;
    }).join('');

    // Stats
    els.sidebarStats.innerHTML = `
      <strong>${rawData.length}</strong> events<br>
      <strong>${totalEntries}</strong> total entries<br>
      <strong>${totalUnique}</strong> unique items
    `;
  }

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  document.addEventListener('DOMContentLoaded', init);
})();
