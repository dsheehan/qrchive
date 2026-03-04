# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
