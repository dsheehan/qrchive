import os
import subprocess
import pytest
import tempfile

PARSER_SCRIPT = os.path.join("scripts", "parse_junit.sh")

def run_parser(xml_content, label="Tests"):
    """Helper to run the parser script against provided XML content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tf:
        if xml_content is not None:
            tf.write(xml_content)
        temp_file_path = tf.name
    
    try:
        # On Windows, we need to run it via bash/sh.
        # We try to find where git bash might be or just use "sh" if available in PATH
        # In this environment, we previously used a full path to sh.exe
        sh_path = r"C:\Program Files\Git\bin\sh.exe"
        shell = sh_path if os.path.exists(sh_path) else "bash"
        
        if xml_content is None:
            # Simulate a missing file using a predictable relative path
            target_path = "non_existent_results.xml"
            if os.path.exists(target_path):
                os.remove(target_path)
        else:
            target_path = temp_file_path
            
        command = [shell, PARSER_SCRIPT, target_path, label]
        
        result = subprocess.run(command, capture_output=True, text=True)
        return (result.stdout + result.stderr).strip(), result.returncode
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@pytest.mark.parametrize("name, xml, label, expected_output, expected_status", [
    # Python (pytest) format: attributes in <testsuite>
    ("Pytest: All passed", '<testsuite tests="2" failures="0" errors="0"></testsuite>', "Python", "Python: 2 passed, 0 failures, 0 errors", 0),
    ("Pytest: Some failures", '<testsuite tests="2" failures="1" errors="0"></testsuite>', "Python", "Python: 1 passed, 1 failures, 0 errors", 1),
    
    # Node.js format: count tags
    ("Node.js: All passed", '<testsuites><testcase name="t1" /><testcase name="t2" /></testsuites>', "JS", "JS: 2 passed, 0 failures, 0 errors", 0),
    ("Node.js: Some failures", '<testsuites><testcase name="t1" /><testcase name="t2"><failure message="fail" /></testcase></testsuites>', "JS", "JS: 1 passed, 1 failures, 0 errors", 1),
    ("Node.js: Some errors", '<testsuites><testcase name="t1" /><testcase name="t2"><error message="err" /></testcase></testsuites>', "JS", "JS: 1 passed, 0 failures, 1 errors", 1),
    
    # Edge cases
    ("Missing file", None, "Tests", "0 passed, 0 failures, 0 errors (result file not found)", 1),
    ("Empty file", "", "Tests", "Tests: 0 passed, 0 failures, 0 errors", 1),
    ("Zero tests", '<testsuite tests="0" failures="0" errors="0"></testsuite>', "Tests", "Tests: 0 passed, 0 failures, 0 errors", 1),
    ("Failure with message containing tags", '<testsuites><testcase name="t1"><failure message="Expected <failure> but got <something else>" /></testcase></testsuites>', "JS", "JS: 0 passed, 1 failures, 0 errors", 1),
])
def test_parse_junit_sh(name, xml, label, expected_output, expected_status):
    output, status = run_parser(xml, label)
    assert expected_output in output, f"Test {name} failed: expected output to contain '{expected_output}', but got '{output}'"
    assert status == expected_status, f"Test {name} failed: expected status {expected_status}, but got {status}"
