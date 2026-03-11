#!/bin/bash

# scripts/parse_junit.sh
# Usage: ./parse_junit.sh <junit-file> <label>

FILE_PATH="${1:-results.xml}"
LABEL="${2:-Tests}"

if [ ! -f "$FILE_PATH" ]; then
    echo "$LABEL: 0 passed, 0 failures, 0 errors (result file not found)"
    exit 1
fi

# We use grep and sed to extract the counts from <testsuite> or <testsuites>
# Note: Node.js 20 JUnit reporter might NOT have attributes in <testsuites> or <testsuite>
# so we count tags as in parse_junit.js if attributes are missing or 0.

# 1. Try to get summary from attributes (common in pytest)
# We look for the first <testsuite> or <testsuites> that has tests="..."
TOTAL_TESTS=$(grep -o 'tests="[0-9]\+"' "$FILE_PATH" | head -1 | sed 's/[^0-9]//g' || echo 0)
FAILURES=$(grep -o 'failures="[0-9]\+"' "$FILE_PATH" | head -1 | sed 's/[^0-9]//g' || echo 0)
ERRORS=$(grep -o 'errors="[0-9]\+"' "$FILE_PATH" | head -1 | sed 's/[^0-9]//g' || echo 0)

# 2. If TOTAL_TESTS is 0 or empty, it might be the Node.js format where we must count tags
if [ -z "$TOTAL_TESTS" ] || [ "$TOTAL_TESTS" -eq 0 ]; then
    # Sanitize XML: remove attributes to avoid matching tags inside strings (like failure messages)
    # Then count <testcase>, <failure>, <error>
    # Note: this is a bit rough in shell compared to JS regex, but should work for most JUnit XMLs
    SANITISED=$(sed 's/[a-zA-Z0-9-]\+=\"[^\"]*\"//g' "$FILE_PATH")
    TOTAL_TESTS=$(echo "$SANITISED" | grep -o '<testcase' | wc -l)
    FAILURES=$(echo "$SANITISED" | grep -o '<failure' | wc -l)
    ERRORS=$(echo "$SANITISED" | grep -o '<error' | wc -l)
fi

# Ensure they are numeric
TOTAL_TESTS=${TOTAL_TESTS:-0}
FAILURES=${FAILURES:-0}
ERRORS=${ERRORS:-0}

PASSED=$((TOTAL_TESTS - FAILURES - ERRORS))
if [ $PASSED -lt 0 ]; then PASSED=0; fi

SUMMARY="$LABEL: $PASSED passed, $FAILURES failures, $ERRORS errors"
echo "$SUMMARY"

if [ "$PASSED" -eq 0 ] || [ "$FAILURES" -gt 0 ] || [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

exit 0
