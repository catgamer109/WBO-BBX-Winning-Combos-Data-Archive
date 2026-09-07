(function () {
  'use strict';

  const DATA_PATH = '../compiled_data/extracted_data.json';
  const PARTS_PATH = '../wbo_bbx_parts.json';

  const $ = (sel) => document.querySelector(sel);

  const els = {
    viewMode: $('#viewMode'),
    placementFilter: $('#placementFilter'),
    rankedFilter: $('#rankedFilter'),
    dateFilter: $('#dateFilter'),
    customDateGroup: $('#customDateGroup'),
    startDate: $('#startDate'),
    endDate: $('#endDate'),
    topN: $('#topN'),
    searchInput: $('#searchInput'),
    rankingList: $('#rankingList'),
    sidebarStats: $('#sidebarStats'),
  };

  let rawData = [];
  let allFilteredComboItems = [];

  // Lookup maps built from wbo_bbx_parts.json
  // Maps full bit name (lowercase) -> abbreviation
  let bitNameToAbbr = {};
  let bitAbbrs = new Set();
  // Maps blade alias (lowercase) -> canonical Name
  let bladeAliasToName = {};

  let lockChips = [];
  let overBlades = [];
  let assistBlades = [];

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
        bitAbbrs.add(bit.Abbreviation.toLowerCase());
        if (bit.Aliases) {
          for (const alias of bit.Aliases) {
            bitNameToAbbr[alias.toLowerCase()] = bit.Abbreviation;
          }
        }
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

    if (parts.LockChips) {
      lockChips = parts.LockChips.map(p => p.Name).sort((a, b) => b.length - a.length);
    }
    if (parts.OverBlades) {
      overBlades = parts.OverBlades.map(p => ({name: p.Name, abbr: p.Abbreviation}));
    }
    if (parts.AssistBlades) {
      assistBlades = parts.AssistBlades.map(p => ({name: p.Name, abbr: p.Abbreviation}));
    }
  }

  /**
   * Abbreviate a full combo string like "DranSword 3-60Flat" -> "DranSword 3-60F"
   * or "Wizard Arrow 4-80Ball" -> "WizardArrow 4-80B"
   */
  function abbreviateCombo(str) {
    str = str.trim();

    // Find the ratchet pattern to split blade from ratchet+bit
    const ratchetMatch = str.match(/^(.+?)(\s*)((?:\d+|M|m)[-–—−]\d+)\s*(.*)$/);
    if (!ratchetMatch) {
       // Check for Blade + Bit (no ratchet)
       const lastSpace = str.lastIndexOf(' ');
       if (lastSpace > 0) {
         let potentialBlade = str.slice(0, lastSpace);
         let potentialBit = str.slice(lastSpace + 1);
         
         const bitLower = potentialBit.toLowerCase();
         if (bitNameToAbbr[bitLower]) {
           potentialBit = bitNameToAbbr[bitLower];
           
           const bladeLower = potentialBlade.toLowerCase();
           if (bladeAliasToName[bladeLower]) {
             potentialBlade = bladeAliasToName[bladeLower];
           }
           
           return `${potentialBlade} ${potentialBit}`;
         }
       }
       return str;
    }

    let bladeRaw = ratchetMatch[1].trim();
    const spaceBeforeRatchet = ratchetMatch[2];
    const ratchet = ratchetMatch[3];
    let bitRaw = ratchetMatch[4].trim();

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

    return `${bladeRaw}${spaceBeforeRatchet}${ratchet}${bitRaw}`;
  }

  function wireUp() {
    [els.viewMode, els.placementFilter, els.rankedFilter, els.dateFilter, els.startDate, els.endDate, els.topN].forEach(
      (el) => el.addEventListener('change', update)
    );
    els.dateFilter.addEventListener('change', () => {
      if (els.dateFilter.value === 'custom') {
        els.customDateGroup.classList.remove('hidden');
      } else {
        els.customDateGroup.classList.add('hidden');
      }
    });
    let t;
    els.searchInput.addEventListener('input', () => { clearTimeout(t); t = setTimeout(update, 150); });

    els.rankingList.addEventListener('click', (e) => {
      const mode = els.viewMode.value;
      const li = e.target.closest('.rank-item');
      if (!li) return;
      
      const existingSubList = li.nextElementSibling;
      if (existingSubList && existingSubList.classList.contains('sub-combos-row')) {
          existingSubList.remove();
          li.classList.remove('expanded');
          return;
      }
      
      document.querySelectorAll('.sub-combos-row').forEach(el => el.remove());
      document.querySelectorAll('.rank-item.expanded').forEach(el => el.classList.remove('expanded'));

      const nameEl = li.querySelector('.rank-item__name');
      if (!nameEl) return;
      const clickedName = nameEl.textContent;
      
      let topCombos = [];
      let targetLabel = clickedName;
      
      if (mode === 'combos') {
          const parsedClicked = parseCombo(clickedName);
          const targetBlade = parsedClicked.blade;
          if (!targetBlade) return;
          targetLabel = targetBlade;
          
          topCombos = allFilteredComboItems.filter(item => {
              if (item.name === clickedName) return false;
              const parsed = parseCombo(item.name);
              return parsed.blade === targetBlade;
          });
      } else {
          topCombos = allFilteredComboItems.filter(item => {
              const parsed = parseCombo(item.name);
              switch (mode) {
                  case 'blades': return parsed.blade === clickedName;
                  case 'ratchets': return parsed.ratchet === clickedName;
                  case 'bits': return parsed.bit === clickedName;
                  case 'lock-chips': return parsed.lockChip === clickedName;
                  case 'over-blades': return parsed.overBlade === clickedName;
                  case 'assist-blades': return parsed.assistBlade === clickedName;
                  default: return false;
              }
          });
      }
      
      const otherCombos = topCombos.slice(0, 5);
      
      if (otherCombos.length === 0) return;
      
      li.classList.add('expanded');
      
      const subRow = document.createElement('li');
      subRow.className = 'sub-combos-row';
      
      const maxSubCount = otherCombos[0].count;
      
      const subListHTML = otherCombos.map(d => {
          const barPct = ((d.count / maxSubCount) * 100).toFixed(1);
          return `<div class="sub-combo-item">
              <span class="sub-combo-name" title="${esc(d.name)}">${esc(d.name)}</span>
              <span class="sub-combo-count">${d.count}</span>
              <div class="sub-combo-bar-wrap"><div class="sub-combo-bar"><div class="sub-combo-bar-fill" style="width:${barPct}%"></div></div></div>
          </div>`;
      }).join('');
      
      let titleText = `Top combos with <strong>${esc(targetLabel)}</strong>`;
      if (mode === 'combos') {
          titleText = `Top other <strong>${esc(targetLabel)}</strong> combos`;
      }
      
      subRow.innerHTML = `<div class="sub-combos-container">
          <div class="sub-combos-title">${titleText}</div>
          ${subListHTML}
      </div>`;
      
      li.insertAdjacentElement('afterend', subRow);
    });
  }

  function parseEventDate(event) {
    let dateStr = event.event_date || event.post_date;
    if (!dateStr) return null;
    // Remove "Sat. ", "Sun. " etc. if present at start
    dateStr = dateStr.replace(/^[A-Za-z]+\.\s*/, '');
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return null;
    return d;
  }

  function parseCombo(str) {
    str = str.trim();
    const m = str.match(/^(.+?)\s*((?:\d+|M|m)[-–—−]\d+)\s*(.*)$/);
    
    let bladeRaw = '';
    let ratchet = '';
    let bit = '';
    
    if (m) {
      bladeRaw = m[1].trim();
      ratchet = m[2].trim();
      bit = m[3].trim();
    } else {
      const lastSpace = str.lastIndexOf(' ');
      if (lastSpace > 0) {
        const potentialBlade = str.slice(0, lastSpace);
        const potentialBit = str.slice(lastSpace + 1);
        if (bitAbbrs.has(potentialBit.toLowerCase())) {
          bladeRaw = potentialBlade;
          ratchet = '';
          bit = potentialBit;
        } else {
          bladeRaw = str;
        }
      } else {
        bladeRaw = str;
      }
    }
    
    let lockChip = '';
    let overBlade = '';
    let assistBlade = '';
    let finalBlade = bladeRaw;

    // Detect CX combo format if it's not a known standard blade
    const bladeLower = bladeRaw.toLowerCase();
    if (!bladeAliasToName[bladeLower]) {
      if (bladeRaw.includes(' ')) {
        const parts = bladeRaw.split(' ');
        if (parts.length === 2) {
          const part1 = parts[0];
          const part2 = parts[1];
          
          let foundLock = lockChips.find(lc => part1.toLowerCase().startsWith(lc.toLowerCase()));
          if (foundLock) {
            lockChip = foundLock;
            let remainderBlade = part1.slice(foundLock.length);
            if (remainderBlade) finalBlade = remainderBlade;
            
            let foundAssist = assistBlades.find(ab => 
              part2.toLowerCase().endsWith(ab.name.toLowerCase()) || 
              (ab.abbr && part2.toUpperCase().endsWith(ab.abbr))
            );
            if (foundAssist) {
              assistBlade = foundAssist.name;
              let suffixLength = part2.toLowerCase().endsWith(foundAssist.name.toLowerCase()) ? foundAssist.name.length : foundAssist.abbr.length;
              let remainderOver = part2.slice(0, part2.length - suffixLength);
              
              let foundOver = overBlades.find(ob => 
                remainderOver.toLowerCase() === ob.name.toLowerCase() || 
                (ob.abbr && remainderOver.toUpperCase() === ob.abbr)
              );
              if (foundOver) {
                overBlade = foundOver.name;
              }
            }
          }
        }
      }
    }
    
    return { blade: finalBlade, ratchet, bit, lockChip, overBlade, assistBlade, full: str };
  }

  function update() {
    const mode = els.viewMode.value;
    const placement = els.placementFilter.value;
    const ranked = els.rankedFilter.value;
    const dateRange = els.dateFilter.value;
    const startVal = els.startDate.value;
    const endVal = els.endDate.value;
    const topN = parseInt(els.topN.value, 10);
    const search = els.searchInput.value.trim().toLowerCase();
    
    // Hardcode 'now' to a fixed point if needed, but Date.now() is fine for a live app.
    const now = new Date();

    // Count
    const counts = {};
    const comboCounts = {};
    let totalEntries = 0;

    for (const event of rawData) {
      if (ranked !== 'all' && event.ranked_status !== ranked) continue;
      
      const evtDate = parseEventDate(event);
      if (evtDate && dateRange !== 'all') {
        if (dateRange === 'past_week') {
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          if (evtDate < weekAgo) continue;
        } else if (dateRange === 'past_2_weeks') {
          const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
          if (evtDate < twoWeeksAgo) continue;
        } else if (dateRange === 'this_month') {
          if (evtDate.getMonth() !== now.getMonth() || evtDate.getFullYear() !== now.getFullYear()) continue;
        } else if (dateRange === 'custom') {
          if (startVal) {
            const startD = new Date(startVal);
            if (evtDate < startD) continue;
          }
          if (endVal) {
            const endD = new Date(endVal);
            endD.setHours(23, 59, 59, 999);
            if (evtDate > endD) continue;
          }
        }
      }

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
            case 'lock-chips': key = parsed.lockChip; break;
            case 'over-blades': key = parsed.overBlade; break;
            case 'assist-blades': key = parsed.assistBlade; break;
            default: key = parsed.full;
          }
          if (!key) continue;
          counts[key] = (counts[key] || 0) + 1;
          if (parsed.full) {
            comboCounts[parsed.full] = (comboCounts[parsed.full] || 0) + 1;
          }
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

    allFilteredComboItems = Object.entries(comboCounts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);

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
