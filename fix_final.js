const fs = require('fs');

const DATA_PATH = './compiled_data/extracted_data.json';
const rawData = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));

let modifiedCount = 0;

for (const event of rawData) {
  if (event.placements) {
    for (const p of event.placements) {
      if (p.combos && Array.isArray(p.combos)) {
        for (let i = 0; i < p.combos.length; i++) {
          if (p.combos[i] === 'ClockMirage M-85Under N') {
            p.combos[i] = 'ClockMirage M-85UN';
            modifiedCount++;
          }
        }
      }
    }
  }
}

if (modifiedCount > 0) {
  fs.writeFileSync(DATA_PATH, JSON.stringify(rawData, null, 2));
}
console.log(`Fixed ${modifiedCount} remaining combos.`);
