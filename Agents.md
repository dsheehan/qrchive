# 🤖 AI Agent Prompts

This file contains pre-defined prompts for AI agents (like GitHub Copilot, ChatGPT, or JetBrains Junie) to help with project maintenance tasks.

## 🚀 Releasing

### Increase Project Version Prompt

**Role**: You are a release manager assistant for the `QRchive` project.

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
4. **Update Changelog**:
   - In the `CHANGELOG.md`, if an `[Unreleased]` section exists, it should be renamed to the new version number and the current date.
   - Otherwise, create a new section with a placeholder for the new version number and the current date.
   - Review the git log since the last release to ensure all relevant changes are accurately reflected in the changelog.
5. **Verification**:
   - Verify that all modified files contain the correct new version.
   - Run existing tests to ensure no regressions were introduced by version changes (especially if the version is used in the app, e.g., in `src/app.py`).
6. **Git Tagging**:
   - Commit the changes if they are not already committed (e.g., `git commit -m "Bump version to X.Y.Z"`). DO NOT use the `--trailer` flag in the commit message.
   - Create a git tag for the new version (e.g., `git tag vX.Y.Z`).
   - Push the tag and the current branch to the remote repository (e.g., `git push origin vX.Y.Z` and `git push origin main`).

**Success Criteria**:
- `pyproject.toml` and `package.json` have the same, incremented version number.
- The application (if it displays the version) correctly reflects the update.
- No other code logic is modified.
- A git tag (e.g., `v0.3.1`) has been created and pushed to the remote repository.
- The `CHANGELOG.md` has been updated to reflect the new version, and no `[Unreleased]` exists

### Update CHANGELOG.md Prompt

**Task**: After successfully completing a set of changes, update the `[Unreleased]` section in `CHANGELOG.md`.

**Workflow**:
1. **Locate Unreleased Section**: Find the `## [Unreleased]` section at the top of `CHANGELOG.md`. If it doesn't exist, create it below the header.
2. **Summarize Changes**: Add a concise summary of the changes made, following the "Keep a Changelog" format (e.g., `### Added`, `### Changed`, `### Fixed`).
3. **Refine Notes**: It's okay to update existing notes in the `[Unreleased]` section. Interim commits might refer to a work in progress that is subsequently completed; ensure the final entry reflects the completed work.

**Success Criteria**:
- `CHANGELOG.md` has an up-to-date `[Unreleased]` section reflecting the latest changes.
- The summary is clear and accurately describes the modifications.
