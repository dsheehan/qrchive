# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added "Maintenance & Releases" section to `DEVELOPMENT.md` explaining the use of AI agent prompts.
- Added header and purpose description to `Agents.md`.

## [0.6.0] - 2026-03-04

### Changed
- Merged `release.yml` into single `docker-image.yml` workflow with conditional release steps.

## [0.5.4] - 2026-03-04

### Changed
- The `viewOnGithub` link in the "What's New" modal now uses the repository URL from `pyproject.toml`.
- Updated `README.md` to be more user-focused, highlighting Docker deployment and `docker-compose`.
- Moved developer-focused information (build from source, project structure) to `DEVELOPMENT.md`.

## [0.5.3] - 2026-03-04

### Changed
- Updated `Agents.md` to make CHANGELOG updates mandatory during version bump.
- Updated `Agents.md` to specify that `[Unreleased]` section should be converted to the new version number.
- Updated `Agents.md` to use `origin` instead of `upstream` as the default remote name for git tags.

## [0.5.2] - 2026-03-04

### Added
- Added Docker pull command to the release notes generated during the release process.
- Added "Update CHANGELOG.md Prompt" to `Agents.md` with instructional workflows for maintaining the `[Unreleased]` section.

### Changed
- Updated `scripts/extract_release_notes.py`: Added support for an optional `image_name` argument to append a `docker pull` command in a `### Docker Image` section.
- Updated `.github/workflows/release.yml`: Modified the `changelog_reader` step to pass the Docker registry and image name to the extraction script.

## [0.5.1] - 2026-03-04

### Added
- Created `scripts/extract_release_notes.py`: A cleaner, more maintainable script to parse `CHANGELOG.md` for a specific version.

### Changed
- Moved the release notes extraction logic from an inline Python script in `.github/workflows/release.yml` to a dedicated script in `scripts/extract_release_notes.py`.
- Updated `.github/workflows/release.yml`: Replaced the complex inline Python with a simple call to the new script, passing the version as an argument.

## [0.5.0] - 2026-03-04

### Added
- Increment version to 0.5.0.
- Rename project to QRchive

## [0.3.4] - 2026-03-04

### Fixed
- Fixed NameError in release workflow.
- Incremented version to 0.3.4.

## [0.3.3] - 2026-03-04

### Changed
- Incremented version to 0.3.3.

## [0.3.2] - 2026-03-04

### Fixed
- Increase project version in all relevant files.
- Updated release.yml to use CHANGELOG.md

## [0.3.1] - 2026-03-04

### Fixed
- Increase project version in all relevant files.
- Updated release preparation instructions.

## [0.3.0] - 2026-03-04

### Added
- Release and CI badges to README.
- Dynamic population of licenses from project metadata.
### Changed
- Refactored CSV handling logic into `services.py`.
- Updated project description.
- Optimized script loading and removed inline scripts.
- Cleaned up unit tests to use pytest style.
- Set navbar to navigate to home.
### Removed
- Unused qrcode page and script references.

## [0.2.0] - 2026-02-21

### Added
- Documentation for version incrementing workflow.

## [0.1.0] - 2026-02-21

### Added
- Initial implementation to show Matter devices in a table.
- Modal popup to display QR Codes.
- Support for adding, editing, and deleting device rows.
- CSV export/import feature for backup and restore.
- Support for scanning QR code data directly from the web browser.
- Open source licenses page.
- Health check endpoint returning the project version.
- Version display in the navbar and update checks against GitHub releases.
- Docker support with GitHub Container Registry (GHCR) integration.
- GitHub Actions workflow for automated releases.
- Responsive styling using the Halfmoon CSS framework.
- Initial project structure and documentation.
