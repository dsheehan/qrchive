const test = require('node:test');
const assert = require('node:assert');
const { isNewerVersion } = require('../src/static/js/utils.js');

// Mock window.APP_CONFIG
global.window = {
    APP_CONFIG: {
        version: '0.6.2',
        githubRepo: 'dsheehan/qrchive'
    }
};

// Mock document for DOM manipulation
global.document = {
    body: {
        getAttribute: (attr) => {
            if (attr === 'data-version') return '0.6.2';
            if (attr === 'data-github-repo') return 'dsheehan/qrchive';
            return null;
        }
    },
    getElementById: (id) => {
        return {
            innerText: '',
            innerHTML: '',
            style: { display: 'none' },
            href: ''
        };
    }
};

// Mock fetch response for GitHub API
const mockApiResponse = {
    ok: true,
    json: async () => ({
        tag_name: "v0.7.0",
        body_html: "<h3>What's New</h3><ul><li>Fixed bugs</li></ul>",
        html_url: "https://github.com/dsheehan/qrchive/releases/tag/v0.7.0"
    })
};

test('testFetchLatestRelease correctly identifies newer releases', async (t) => {
    // Simulating what happens in matter.js
    const data = await mockApiResponse.json();
    const latestTag = data.tag_name || "0.0.0";
    const result = {
        current_version: window.APP_CONFIG.version,
        latest_version: latestTag,
        is_newer: isNewerVersion(latestTag, window.APP_CONFIG.version),
        release_notes_html: data.body_html,
        html_url: data.html_url
    };

    assert.strictEqual(result.latest_version, "v0.7.0", "latest_version should be v0.7.0");
    assert.strictEqual(result.is_newer, true, "is_newer should be true");
    assert.strictEqual(result.release_notes_html, "<h3>What's New</h3><ul><li>Fixed bugs</li></ul>", "release_notes_html mismatch");
});
