# Changelog

All notable changes to this project will be documented in this file.

## [1.4] - 2025-11-27

### Features
- **Password Generator:** Added a password generator with entropy meter, supporting quick and advanced generation modes.
### Fixed
- **UI Improvements:** 
  - Adjusted window sizes for the MarkDown Guide and Keyboard Shortcuts dialogs.
  - Removes numbering from Scratch Notes (sticky notes).
  - Changes click and drag icon on Scratch Notes.
  - Fixes mouse visibility based on Scratch Note background color.

### Release
- **Release**: Release of version 1.4.

## [1.3] - 2025-11-26  
### Fixed 
- **Versioning**: Ensures the version within the 'About Scratch Board' view loads the proper version from release and matches against version located in the version text file.

## [1.2] - 2025-11-25  
### Added  
- **Dashboard Navigation**: Automatically navigates to the dashboard after a successful note import.  
  - Emits the `dashboard_clicked` signal after importing notes from a ZIP file.  

### Fixed  
- **Dashboard Navigation Issue**: Ensured that the correct view (dashboard) is displayed after the import process completes successfully.

## [1.1] - 2025-11-24
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