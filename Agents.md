### Increase Project Version Prompt

**Role**: You are a release manager assistant for the `qrcodex` project.

**Task**: Increase the project version number in all relevant files to prepare for a new release.

**Workflow**:
1. **Identify Version Files**: Find all files that contain the current project version. Based on the project structure, these are typically:
   - `pyproject.toml` (at `[project].version`)
   - `package.json` (at `"version"`)
2. **Determine New Version**:
   - Ask the user if they want a **major**, **minor**, or **patch** update (following Semantic Versioning: `MAJOR.MINOR.PATCH`).
   - If the user doesn't specify, default to a **patch** update.
3. **Apply Changes**:
   - Update the version string in `pyproject.toml`.
   - Update the version string in `package.json`.
4. **Update Changelog (Optional)**:
   - If `CHANGELOG.md` exists, add a new section for the new version with the current date and a placeholder for changes.
5. **Verification**:
   - Verify that all modified files contain the correct new version.
   - Run existing tests to ensure no regressions were introduced by version changes (especially if the version is used in the app, e.g., in `src/app.py`).

**Success Criteria**:
- `pyproject.toml` and `package.json` have the same, incremented version number.
- The application (if it displays the version) correctly reflects the update.
- No other code logic is modified.
