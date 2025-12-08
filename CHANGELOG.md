# Changelog

All notable changes to this project will be documented in this file.

## [1.5.1] - 2025-12-08

### Added / Improved
- **Image caching for notes:** Introduced `PopulateNotesThread` to preload and cache scaled pixmaps, reducing UI freezes and improving scroll responsiveness.
- **Performance optimizations:** Faster note loading and smoother toggling between grid and list views, particularly with high-resolution or many images.

### Fixed / Refactored
- **Memory and scaling improvements:** Large images are resized once and stored as pixmaps, preventing repeated disk reads and redundant scaling.
- **Code cleanup:** Minor refactors and removal of legacy blocking image loads for a cleaner codebase.


## [1.5] - 2025-12-02

### Added
- **Tag Input for Notes:** Added tag input support in `editor_view.py`, `note_controller.py`, and `note_model.py`.  
- **Third-Party Acknowledgments:** Updated README to include acknowledgments for PySide6 and other third-party resources.  
- **Licensing Updates:** Improved LICENSE.md formatting and added attribution for Google Material Icons.  

### Fixed
- **Unused Code Removal:** Removed unused code from `main.py`.  
- **Documentation Cleanup:** Removed `build.txt` from repository and refined README language for installing dependencies.  
- **Splash Screen:** Refined progress bar behavior in `splash_screen.py`.  
- **Sidebar UI:** Improved separator display between Copilot and streaming categories in `sidebar_widget.py`.  

### Changed / Refactored
- **Notepad Layout:** Refactored `notepad` layout and font handling for better readability and consistency.  
- **Versioning:** Incremented version to 1.5.0 for release.  
- **Documentation:** Removed duplicate lines in README’s main tools section.

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