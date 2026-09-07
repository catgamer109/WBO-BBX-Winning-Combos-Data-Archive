const lines = require('fs').readFileSync('junk_combos.txt','utf8').split('\n');
const maybeLegit = [];
const realJunk = [];
for (const line of lines) {
  if (!line.trim()) continue;
  const m = line.match(/"(.+?)"/);
  if (!m) continue;
  const combo = m[1];
  // Patterns that look like valid combos with non-standard ratchets
  if (combo.match(/M-\d+/i) || combo.match(/Heavy|Dual|Free|Assault/i)) {
    maybeLegit.push(combo);
  } else {
    realJunk.push(combo);
  }
}
console.log('=== Possibly legit new-format combos (' + maybeLegit.length + ') ===');
maybeLegit.forEach(c => console.log('  ' + c));
console.log('\n=== Definite junk (' + realJunk.length + ') ===');
realJunk.forEach(c => console.log('  ' + c));
