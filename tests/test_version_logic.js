const test = require('node:test');
const assert = require('node:assert');
const { isNewerVersion } = require('../src/static/js/utils.js');

test('isNewerVersion handles various version strings correctly', (t) => {
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

    testCases.forEach(([latest, current, expected]) => {
        const result = isNewerVersion(latest, current);
        assert.strictEqual(result, expected, `isNewerVersion('${latest}', '${current}') should be ${expected}`);
    });
});
