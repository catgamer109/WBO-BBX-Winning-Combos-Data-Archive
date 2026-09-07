const fs = require('fs');

const DATA_PATH = './compiled_data/extracted_data.json';
const PARTS_PATH = './wbo_bbx_parts.json';

const rawData = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
const parts = JSON.parse(fs.readFileSync(PARTS_PATH, 'utf8'));

// Build valid sets for all parts (Name + Aliases + Abbreviations)
const validParts = {
  LockChips: new Set(),
  Blades: new Set(),
  OverBlades: new Set(),
  AssistBlades: new Set(),
  Ratchets: new Set(),
  Bits: new Set()
};

const bitAbbrs = new Set();
const bladeAliasToName = {};

function populateSet(category, dataList) {
  if (!dataList) return;
  for (const item of dataList) {
    if (item.Name) validParts[category].add(item.Name.toLowerCase());
    if (item.Abbreviation) validParts[category].add(item.Abbreviation.toLowerCase());
    if (item.Aliases) {
      for (const alias of item.Aliases) {
        validParts[category].add(alias.toLowerCase());
        if (category === 'Blades') {
          bladeAliasToName[alias.toLowerCase()] = item.Name;
        }
      }
    }
    if (category === 'Bits' && item.Abbreviation) {
      bitAbbrs.add(item.Abbreviation.toLowerCase());
    }
  }
}

populateSet('LockChips', parts.LockChips);
populateSet('Blades', parts.Blades);
populateSet('OverBlades', parts.OverBlades);
populateSet('AssistBlades', parts.AssistBlades);
populateSet('Ratchets', parts.Ratchets);
populateSet('Bits', parts.Bits);

// Copied from app.js with regex (?:\d+|M|m)
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

  if (bladeRaw.includes(' ') && !validParts.Blades.has(bladeRaw.toLowerCase()) && !bladeAliasToName[bladeRaw.toLowerCase()]) {
    const spaceParts = bladeRaw.split(' ');
    if (spaceParts.length === 2) {
      const part1 = spaceParts[0];
      const part2 = spaceParts[1];
      
      let foundAssist = parts.AssistBlades && parts.AssistBlades.find(ab => part2.toLowerCase().endsWith(ab.Name.toLowerCase()) || (ab.Abbreviation && part2.toUpperCase().endsWith(ab.Abbreviation.toUpperCase())));
      if (foundAssist) {
        assistBlade = foundAssist.Name;
        let suffixLength = part2.toLowerCase().endsWith(foundAssist.Name.toLowerCase()) ? foundAssist.Name.length : foundAssist.Abbreviation.length;
        let remainderOver = part2.slice(0, part2.length - suffixLength);
        
        let foundOver = parts.OverBlades && parts.OverBlades.find(ob => remainderOver.toLowerCase() === ob.Name.toLowerCase() || (ob.Abbreviation && remainderOver.toUpperCase() === ob.Abbreviation.toUpperCase()));
        if (foundOver) {
          overBlade = foundOver.Name;
        }
      } else {
        let foundOver = parts.OverBlades && parts.OverBlades.find(ob => part2.toLowerCase() === ob.Name.toLowerCase() || (ob.Abbreviation && part2.toUpperCase() === ob.Abbreviation.toUpperCase()));
        if (foundOver) {
          overBlade = foundOver.Name;
        }
      }
      
      let foundLockChip = parts.LockChips && parts.LockChips.find(lc => part1.toLowerCase().startsWith(lc.Name.toLowerCase()));
      if (foundLockChip) {
        lockChip = foundLockChip.Name;
        finalBlade = part1.slice(lockChip.length);
      } else {
        finalBlade = part1;
      }
    }
  }

  return { bladeRaw, ratchet, bit, lockChip, overBlade, assistBlade, finalBlade, full: str };
}

const unmappedCombos = new Set();

for (const event of rawData) {
  if (event.placements) {
    for (const p of event.placements) {
      if (p.combos && Array.isArray(p.combos)) {
        for (const comboStr of p.combos) {
          const parsed = parseCombo(comboStr);
          
          let hasUnmapped = false;
          let issues = [];

          // Check Ratchet
          if (parsed.ratchet && !validParts.Ratchets.has(parsed.ratchet.toLowerCase())) {
            hasUnmapped = true;
            issues.push(`Ratchet: ${parsed.ratchet}`);
          }
          
          // Check Bit
          if (parsed.bit && !validParts.Bits.has(parsed.bit.toLowerCase())) {
            hasUnmapped = true;
            issues.push(`Bit: ${parsed.bit}`);
          }
          
          // Check Blade
          if (parsed.lockChip || parsed.overBlade || parsed.assistBlade) {
            // It's a CX combo
            if (parsed.lockChip && !validParts.LockChips.has(parsed.lockChip.toLowerCase())) {
              hasUnmapped = true; issues.push(`LockChip: ${parsed.lockChip}`);
            }
            if (parsed.finalBlade && !validParts.Blades.has(parsed.finalBlade.toLowerCase())) {
              hasUnmapped = true; issues.push(`Blade: ${parsed.finalBlade}`);
            }
            if (parsed.overBlade && !validParts.OverBlades.has(parsed.overBlade.toLowerCase())) {
              hasUnmapped = true; issues.push(`OverBlade: ${parsed.overBlade}`);
            }
            if (parsed.assistBlade && !validParts.AssistBlades.has(parsed.assistBlade.toLowerCase())) {
              hasUnmapped = true; issues.push(`AssistBlade: ${parsed.assistBlade}`);
            }
          } else {
            // Standard combo
            if (parsed.bladeRaw && !validParts.Blades.has(parsed.bladeRaw.toLowerCase())) {
              hasUnmapped = true; issues.push(`Blade: ${parsed.bladeRaw}`);
            }
          }

          if (hasUnmapped) {
            unmappedCombos.add(`- \`${comboStr}\` (Unmapped: ${issues.join(', ')})`);
          }
        }
      }
    }
  }
}

const result = Array.from(unmappedCombos).sort();
fs.writeFileSync('C:/Users/Evan/.gemini/antigravity-ide/brain/70ec51d7-60d5-4629-9edc-4f7451d8cb88/unmapped_combos.md', `# Unmapped Combos Report\n\nFound ${result.length} unique combos with unmapped parts:\n\n${result.join('\n')}`);
console.log(`Report generated with ${result.length} unmapped combos.`);
