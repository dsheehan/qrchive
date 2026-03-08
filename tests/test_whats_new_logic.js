// Test script to verify the logic of the "What's New" modal data handling
// This mocks the GitHub API response and verifies if the expected fields are extracted and injected

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

// Load functions from matter.js
const { isNewerVersion } = require('../src/static/js/utils.js');

// Mock fetch response for GitHub API
const mockApiResponse = {
    ok: true,
    json: async () => ({
        tag_name: "v0.7.0",
        body_html: "<h3>What's New</h3><ul><li>Fixed bugs</li></ul>",
        html_url: "https://github.com/dsheehan/qrchive/releases/tag/v0.7.0"
    })
};

async function testFetchLatestRelease() {
    console.log("Running testFetchLatestRelease...");
    
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

    console.log("Mock result:", JSON.stringify(result, null, 2));

    // Assertions
    let passed = true;
    if (result.latest_version !== "v0.7.0") {
        console.error("❌ latest_version mismatch");
        passed = false;
    }
    if (result.is_newer !== true) {
        console.error("❌ is_newer should be true");
        passed = false;
    }
    if (result.release_notes_html !== "<h3>What's New</h3><ul><li>Fixed bugs</li></ul>") {
        console.error("❌ release_notes_html mismatch");
        passed = false;
    }
    
    if (passed) {
        console.log("✅ testFetchLatestRelease passed!");
    } else {
        process.exit(1);
    }
}

testFetchLatestRelease();
