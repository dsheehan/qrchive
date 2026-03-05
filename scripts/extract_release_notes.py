import sys
import re
import os

def extract_release_notes(version, changelog_path='CHANGELOG.md'):
    if not os.path.exists(changelog_path):
        return f"Warning: {changelog_path} not found."

    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The format in CHANGELOG.md is: ## [0.5.0] - 2026-03-04
    pattern = rf'## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}\n(.*?)(?=\n## \[|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        return match.group(1).strip()
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_release_notes.py <version> [image_name]")
        sys.exit(1)

    version_to_find = sys.argv[1]
    image_name = sys.argv[2] if len(sys.argv) > 2 else None
    notes = extract_release_notes(version_to_find)

    output_file = 'release_notes.txt'
    if notes:
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(notes)
            if image_name:
                out.write("\n\n### Docker Image\n")
                out.write(f"```bash\ndocker pull {image_name}:{version_to_find}\n```")
    else:
        print(f'Warning: Version {version_to_find} not found in CHANGELOG.md')
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write('No release notes found in CHANGELOG.md for this version.')
