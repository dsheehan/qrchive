const test = require('node:test');
const assert = require('node:assert');
const { matchesRecord, normalizeQuery } = require('../../src/static/js/filter_query.js');

const records = [
    {
        name: 'Alice Johnson',
        status: 'active',
        role: 'admin',
        department: 'engineering',
        title: 'The Art of War'
    },
    {
        name: 'Bob Smith',
        status: 'active',
        role: 'user',
        department: 'guest',
        title: 'The End of War'
    },
    {
        name: 'Jason Brown',
        status: 'inactive',
        role: 'admin',
        department: 'ops',
        title: 'The Book of Peace'
    }
];

function filterNames(query) {
    return records.filter((record) => matchesRecord(record, query)).map((record) => record.name);
}

test('global search across all fields: alice', () => {
    assert.deepStrictEqual(filterNames('alice'), ['Alice Johnson']);
});

test('global unquoted term implies wildcard matching', () => {
    assert.strictEqual(
        matchesRecord({ description: 'Kitchen Potlights' }, 'light'),
        true
    );
});

test('global quoted term does not imply wildcard matching', () => {
    assert.strictEqual(
        matchesRecord({ description: 'Kitchen Potlights' }, '"light"'),
        false
    );
});

test('global wildcard term without leading wildcard does not match infix text', () => {
    assert.strictEqual(
        matchesRecord({ description: 'Kitchen Potlights' }, 'light*'),
        false
    );
});

test('global wildcard term with leading wildcard matches infix text', () => {
    assert.strictEqual(
        matchesRecord({ description: 'Kitchen Potlights' }, '*light*'),
        true
    );
});

test('global wildcard term with leading wildcard allows zero-length match before term', () => {
    assert.strictEqual(
        matchesRecord({ description: 'Kitchen Potlights' }, '*K'),
        true
    );
});

test('field-specific filter: status=active', () => {
    assert.deepStrictEqual(filterNames('status=active'), ['Alice Johnson', 'Bob Smith']);
});

test('boolean combination: status=active AND role=admin', () => {
    assert.deepStrictEqual(filterNames('status=active AND role=admin'), ['Alice Johnson']);
});

test('wildcard in field search: name=J*son', () => {
    assert.deepStrictEqual(filterNames('name=J*son'), ['Alice Johnson', 'Jason Brown']);
});

test('wildcard in global search: "*smith*"', () => {
    assert.deepStrictEqual(filterNames('"*smith*"'), ['Bob Smith']);
});

test('complex expression with parentheses and NOT', () => {
    assert.deepStrictEqual(
        filterNames('(status=active OR role=admin) AND NOT department=guest'),
        ['Alice Johnson', 'Jason Brown']
    );
});

test('boolean NOT with unquoted global term: NOT alice', () => {
    assert.deepStrictEqual(filterNames('NOT alice'), ['Bob Smith', 'Jason Brown']);
});

test('quoted exact phrase with wildcard: title="The * of War"', () => {
    assert.deepStrictEqual(
        filterNames('title="The * of War"'),
        ['Alice Johnson', 'Bob Smith']
    );
});

test('normalization converts field syntax to librarian-compatible terms', () => {
    assert.strictEqual(
        normalizeQuery('status=active AND role=admin'),
        '"status:active" AND "role:admin"'
    );
});

test('normalization quotes bare terms in boolean expressions', () => {
    assert.strictEqual(normalizeQuery('NOT alice'), 'NOT "alice"');
});

test('normalization keeps a bare global term quoted for librarian parsing', () => {
    assert.strictEqual(normalizeQuery('light'), '"light"');
});
