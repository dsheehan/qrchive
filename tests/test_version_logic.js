// Testing the isNewerVersion logic used in src/static/js/matter.js

function isNewerVersion(latest, current) {
    try {
        const parse = v => v.replace(/^v/, '').split('.').map(Number);
        const l = parse(latest);
        const c = parse(current);
        
        if (l.some(isNaN) || c.some(isNaN)) return false;

        for (let i = 0; i < Math.max(l.length, c.length); i++) {
            const lv = l[i] || 0;
            const cv = c[i] || 0;
            if (lv > cv) return true;
            if (lv < cv) return false;
        }
        return false;
    } catch (err) {
        return false;
    }
}

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
