# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-11-24
### Added
- **About dialog** now checks for updates in a background thread.
  - Introduced `UpdateCheckWorker` to fetch latest GitHub release asynchronously.
  - Display update status in AboutWidget without blocking the UI.
  - Show "Get Update" button when a new version is available.
  - Updates About dialog version label when check completes.

### Fixed
- Version comparison logic in AboutWidget.
  - Strips leading 'v' from tags for accurate comparison.
  - Correctly marks app as up-to-date when latest version equals current version.

### Changed / Refactored
- About dialog UI alignment and spacing.
  - Centered app icon, title, version label, copyright.
  - Improved overall layout with consistent vertical spacing.

### Documentation
- Initial `CHANGELOG.md` entries start with v1.1 summarizing new features and fixes.