(function (root) {
    let nodeParse;
    if (typeof module !== 'undefined' && module.exports) {
        try {
            nodeParse = require('@spaceavocado/librarian').parse;
        } catch (e) {
            nodeParse = null;
        }
    }

    const expressionCache = new Map();

    /**
     * Returns the parse function to use for query evaluation.
     * Prefers the custom function, then the global LIBRARIAN_PARSE, then the Node.js module.
     * @param {Function|undefined} customParseFn - Optional custom parse function.
     * @returns {Function|null} The resolved parse function, or null if none is available.
     */
    function getParseFn(customParseFn) {
        if (typeof customParseFn === 'function') return customParseFn;
        if (typeof root.LIBRARIAN_PARSE === 'function') return root.LIBRARIAN_PARSE;
        return nodeParse;
    }

    /**
     * Normalizes a field name by trimming whitespace and converting to lowercase.
     * @param {*} fieldName - The field name to normalize.
     * @returns {string} The normalized field name.
     */
    function normalizeFieldName(fieldName) {
        return (fieldName || '').toString().trim().toLowerCase();
    }

    /**
     * Escapes special RegExp characters in a string.
     * @param {string} value - The string to escape.
     * @returns {string} The escaped string safe for use in a RegExp.
     */
    function escapeRegExp(value) {
        return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Returns true if the query is a simple quoted global term (e.g. `"hello"`) with no wildcards.
     * @param {*} rawQuery - The raw query string.
     * @returns {boolean}
     */
    function isSimpleQuotedGlobalTerm(rawQuery) {
        const query = (rawQuery || '').toString().trim();
        if (!/^"[^"]+"$/.test(query)) return false;
        const unwrapped = query.slice(1, -1);
        return !/[*?]/.test(unwrapped);
    }

    /**
     * Returns true if the query is a single bare word with no special characters, operators, or wildcards.
     * @param {*} rawQuery - The raw query string.
     * @returns {boolean}
     */
    function isSimpleBareGlobalTerm(rawQuery) {
        const query = (rawQuery || '').toString().trim();
        if (!query) return false;
        if (/[()="]/g.test(query)) return false;
        if (/\b(AND|OR|NOT|XOR|NOR)\b/i.test(query)) return false;
        if (/[*?]/.test(query)) return false;
        return !/\s/.test(query);
    }

    /**
     * Returns true if the query is a single word containing wildcard characters (`*` or `?`) but no other special syntax.
     * @param {*} rawQuery - The raw query string.
     * @returns {boolean}
     */
    function isSimpleWildcardGlobalTerm(rawQuery) {
        const query = (rawQuery || '').toString().trim();
        if (!query) return false;
        if (/[()="]/g.test(query)) return false;
        if (/\b(AND|OR|NOT|XOR|NOR)\b/i.test(query)) return false;
        if (/\s/.test(query)) return false;
        return /[*?]/.test(query);
    }

    /**
     * Checks whether a record matches a quoted exact-term query using whole-word matching.
     * @param {Object} record - The data record to test.
     * @param {*} rawQuery - The quoted query string (e.g. `"hello"`).
     * @returns {boolean}
     */
    function matchesExactGlobalTerm(record, rawQuery) {
        const term = (rawQuery || '').toString().trim().slice(1, -1).toLowerCase();
        if (!term) return true;
        const valuesContext = Object.values(record || {})
            .map((value) => (value || '').toString().toLowerCase())
            .join(' ');
        return new RegExp(`\\b${escapeRegExp(term)}\\b`, 'i').test(valuesContext);
    }

    /**
     * Checks whether a record matches a bare (unquoted, no wildcards) query term using substring matching.
     * @param {Object} record - The data record to test.
     * @param {*} rawQuery - The bare query string.
     * @returns {boolean}
     */
    function matchesBareGlobalTerm(record, rawQuery) {
        const term = (rawQuery || '').toString().trim().toLowerCase();
        if (!term) return true;
        const valuesContext = Object.values(record || {})
            .map((value) => (value || '').toString().toLowerCase())
            .join(' ');
        return valuesContext.includes(term);
    }

    /**
     * Checks whether any token in a record matches a wildcard query (`*` and `?` supported).
     * @param {Object} record - The data record to test.
     * @param {*} rawQuery - The wildcard query string.
     * @returns {boolean}
     */
    function matchesWildcardGlobalTerm(record, rawQuery) {
        const term = (rawQuery || '').toString().trim();
        if (!term) return true;

        const regexPattern = escapeRegExp(term)
            .replace(/\\\*/g, '.*')
            .replace(/\\\?/g, '.');
        const endsWithWildcard = term.endsWith('*');
        const startsWithWildcard = term.startsWith('*');

        const startAnchor = startsWithWildcard ? '' : '^';
        // Leading wildcard is treated as regex-like prefix wildcard where `*`
        // can consume zero length and does not force a token-end boundary.
        const endAnchor = startsWithWildcard || endsWithWildcard ? '' : '$';
        const tokenRegex = new RegExp(`${startAnchor}${regexPattern}${endAnchor}`, 'i');

        const tokens = Object.values(record || {})
            .flatMap((value) => (value || '').toString().split(/[^\w]+/))
            .map((token) => token.trim())
            .filter(Boolean);

        return tokens.some((token) => tokenRegex.test(token));
    }

    /**
     * Normalizes a raw query string into a format suitable for the Librarian parser.
     * Converts field=value syntax, wraps bare tokens in quotes, and handles boolean operators.
     * @param {*} rawQuery - The raw query string.
     * @returns {string} The normalized query string.
     */
    function normalizeQuery(rawQuery) {
        const query = (rawQuery || '').toString().trim();
        if (!query) return '';

        let normalized = query.replace(/([A-Za-z_][A-Za-z0-9_-]*)\s*=\s*("[^"]*"|[^\s()]+)/g, (_, field, value) => {
            let unwrapped = value;
            if (unwrapped.startsWith('"') && unwrapped.endsWith('"')) {
                unwrapped = unwrapped.slice(1, -1);
            }
            return `"${normalizeFieldName(field)}:${unwrapped}"`;
        });

        const hasBoolean = /\b(AND|OR|NOT|XOR|NOR)\b/.test(normalized);
        const hasParens = /[()]/.test(normalized);
        const hasQuotes = /"/.test(normalized);

        if (hasBoolean || hasParens) {
            normalized = normalized
                .split(/("[^"]*")/g)
                .map((part) => {
                    if (!part || part.startsWith('"')) return part;
                    return part.replace(/\b([^\s()"]+)\b/g, (token) => {
                        if (/^(AND|OR|NOT|XOR|NOR)$/i.test(token)) return token;
                        return `"${token}"`;
                    });
                })
                .join('');
        }

        if (!hasBoolean && !hasParens && !hasQuotes) {
            normalized = `"${normalized}"`;
        }

        return normalized;
    }

    /**
     * Builds a flat search context string from a record's key-value pairs.
     * Includes raw values, a compact (non-word-stripped) version, and field-prefixed tokens.
     * @param {Object} record - The data record to build context from.
     * @returns {string} A single string representing the searchable content of the record.
     */
    function buildSearchContext(record) {
        const values = [];
        const fields = [];
        Object.entries(record || {}).forEach(([key, value]) => {
            const normalizedKey = normalizeFieldName(key);
            const textValue = (value || '').toString();
            values.push(textValue);
            if (normalizedKey) {
                fields.push(`${normalizedKey}:${textValue}`);
                textValue
                    .split(/\s+/)
                    .map((part) => part.trim())
                    .filter(Boolean)
                    .forEach((part) => {
                        fields.push(`${normalizedKey}:${part}`);
                    });
            }
        });
        const joinedValues = values.join(' ');
        const compactValues = joinedValues.replace(/[^\w]+/g, '');
        return `${joinedValues} ${compactValues} ${fields.join(' ')}`.trim();
    }

    /**
     * Evaluates a query against a context string using the Librarian parser.
     * Returns null if no parse function is available.
     * @param {*} rawQuery - The raw query string.
     * @param {string} context - The search context string to test against.
     * @param {Function|undefined} customParseFn - Optional custom parse function.
     * @returns {boolean|null} The match result, or null if Librarian is unavailable.
     */
    function evaluateWithLibrarian(rawQuery, context, customParseFn) {
        const parseFn = getParseFn(customParseFn);
        if (!parseFn) return null;

        const normalized = normalizeQuery(rawQuery);
        if (!normalized) return true;

        let expression = expressionCache.get(normalized);
        if (!expression) {
            expression = parseFn(normalized);
            expressionCache.set(normalized, expression);
        }
        return expression.test(context);
    }

    /**
     * Fallback query evaluator used when Librarian is unavailable or throws.
     * Splits the query into words and requires all of them to appear in the context.
     * @param {*} rawQuery - The raw query string.
     * @param {string} context - The search context string to test against.
     * @returns {boolean}
     */
    function fallbackEvaluate(rawQuery, context) {
        const query = (rawQuery || '').toLowerCase().trim();
        if (!query) return true;
        const words = query.split(/\s+/).filter(Boolean);
        return words.every((word) => context.includes(word));
    }

    /**
     * Determines whether a record matches the given query.
     * Dispatches to the appropriate fast-path matcher for simple queries, or uses
     * Librarian (with fallback) for complex boolean/field expressions.
     * @param {Object} record - The data record to test.
     * @param {*} rawQuery - The raw query string.
     * @param {Function|undefined} customParseFn - Optional custom parse function for Librarian.
     * @returns {boolean} True if the record matches the query.
     */
    function matchesRecord(record, rawQuery, customParseFn) {
        if (isSimpleQuotedGlobalTerm(rawQuery)) {
            return matchesExactGlobalTerm(record, rawQuery);
        }

        if (isSimpleWildcardGlobalTerm(rawQuery)) {
            return matchesWildcardGlobalTerm(record, rawQuery);
        }

        if (isSimpleBareGlobalTerm(rawQuery)) {
            return matchesBareGlobalTerm(record, rawQuery);
        }

        const context = buildSearchContext(record).toLowerCase();
        try {
            const librarianResult = evaluateWithLibrarian(rawQuery, context, customParseFn);
            if (librarianResult !== null) {
                return librarianResult;
            }
        } catch (e) {
            // Ignore parse errors and fallback to legacy matching.
        }
        return fallbackEvaluate(rawQuery, context);
    }

    const api = {
        normalizeQuery,
        buildSearchContext,
        matchesRecord,
    };

    root.FilterQuery = api;

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : window);
