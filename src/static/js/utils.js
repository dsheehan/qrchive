/**
 * Utility functions shared between the application and tests.
 */

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

// Node.js export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { isNewerVersion };
}
