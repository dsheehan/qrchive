// Testing the isNewerVersion logic used in src/static/js/matter.js

// Load functions from matter.js
const { isNewerVersion } = require('../src/static/js/utils.js');

// Test cases: [latest, current, expected]
const testCases = [
    ['0.6.3', '0.6.2', true],
    ['0.7.0', '0.6.2', true],
    ['1.0.0', '0.6.2', true],
    ['v0.6.3', '0.6.2', true],
    ['0.6.3', 'v0.6.2', true],
    ['v0.6.3', 'v0.6.2', true],
    ['0.6.2', '0.6.2', false],
    ['0.6.1', '0.6.2', false],
    ['0.6.2', '0.6.3', false],
    ['0.6', '0.6.2', false],
    ['0.6.2', '0.6', true],
    ['1.0', '0.9.9', true],
    ['Invalid', '0.6.2', false],
    ['0.6.2', 'Invalid', false],
    ['1.2.3.4', '1.2.3', true],
    ['1.2.3', '1.2.3.4', false]
];

let passed = 0;
let failed = 0;

console.log("Running isNewerVersion tests...");
testCases.forEach(([latest, current, expected]) => {
    const result = isNewerVersion(latest, current);
    if (result === expected) {
        console.log(`✅ PASS: isNewerVersion('${latest}', '${current}') === ${expected}`);
        passed++;
    } else {
        console.error(`❌ FAIL: isNewerVersion('${latest}', '${current}') expected ${expected}, but got ${result}`);
        failed++;
    }
});

console.log(`\nTests completed: ${passed} passed, ${failed} failed.`);

if (failed > 0) {
    process.exit(1);
}
