# Changelog

All **_notable_** changes to this project will be documented in this file.

## [2.2.0] – 2026-01-06

### Features
- **Batch Manager:** Added a batch manager screen to perform various functions such as terminating a process.

### Enhancements
- **Multi-Line Chart:** New statistics to display visually.
- **Info Charts:** Info charts include more information and are more readable.

### UI Fix
- **Button Sizing:** Fixes button sizes for the custom links and mac query dashboard widgets.

**Full Changelog**: https://github.com/Quantum-Yeti/ScratchBoard/compare/v2.1.2...v2.2.0

## [2.1.1] – 2026-01-01

### Fixed
- **Keyboard Shortcuts:**  
  - Removed duplicate keyboard shortcuts in `shortcuts_list.py` to avoid conflicts.

### Improved
- **UI/UX Refinements:**  
  - Refined various UI components across the app, including in `charts_widget.py` and `mac_widget.py`, to enhance consistency and visual appeal.  
  - Implemented tooltip style refinement for better user feedback.  
  - Improved sticky note manager window size for better usability.

### Refactored
- **Context Menu Overhaul:**  
  - Overridden and refined context menus in multiple modules, including `contacts_manager.py`, `sticky_view.py`, `notepad_view.py`, and more, to ensure consistent behavior and functionality across the app.  
  - Improved context menu action patterns in `custom_context_menu.py`.

- **Code Clean-Up:**  
  - Cleaned up and reorganized code in `contacts_view.py`, `contacts_manager.py`, `sticky_manager.py`, and `notepad_view.py` for better readability and maintainability.

### Features
- **Password Widget Quick Mode:**  
  - Implemented a new "quick mode" for password generation in `password_widget.py`, allowing for faster creation of strong passwords (word+number).

## [2.1.0] – 2025-12-27

### Added / Improved
- **Text Editing Enhancements:**  
  - Copied text in CustomQEdit now retains white color for consistency.
  - Performance improvements for text insertion and rendering.

### Fixed
- **UI Bugs:**  
  - Fixed text insertion color issue in CustomQEdit.

### Refactored
- Integrated FTS5 search for faster and more accurate text queries.
- General code cleanup and optimizations across modules.

## [2.0.1] – 2025-12-26

### Added / Improved
- **Rich Text Editing Enhancements:**  
  - Added support for additional rich text formatting in the note editor, including bold, italic, multiple header sizes, bulleted and numbered lists, and horizontal line insertion.  
  - Integrated link and image insertion buttons into the editor toolbar for a richer authoring experience.  
  - Added highlight and custom text color selection dialogs, letting users visually style note content.

- **Editor UI Improvements:**  
  - Expanded toolbar actions and updated layout to better support extended formatting options.  
  - Improved Markdown/HTML preview handling for consistent rendering of rich content.

### Fixed
- **Toolbar/Icon Issues:**  
  - Fixed missing or incorrect toolbar icon display by verifying resource paths and action setup.  
  - Resolved inconsistent hover/highlight behavior for bottom action buttons (Save, Delete, Cancel, Preview).

- **Text Persistence:**  
  - Confirmed that rich HTML content from the editor continues to be stored and retrieved correctly in the database.

### Refactored
- **Editor Logic Separation:**  
  - Moved formatting and helper logic into `EditorManager` to improve separation of UI and business logic and facilitate reuse.  
  - Cleaned up preview HTML preparation by centralizing style and path conversion logic.

### Notes
- Internal refactors and style updates help lay the groundwork for further rich text improvements in upcoming versions.


## [1.5.2] - 2025-12-09

### Added / Improved
- **Storage Unit Converter:** Replaced outage mode in `SimpleCalcView` with a storage unit converter (Bytes ↔ KB/MB/GB/TB). Supports dynamic "From" and "To" units selection via dropdowns.
- **Multi-Line Chart Enhancements:** Refined Y-axis range calculation for `create_multi_line_chart` to better fit all stat lines and avoid unnecessary padding.
- **Dashboard Chart Improvements:** General improvements to stacked bar and multi-line charts for better readability and tighter layouts.
- **Info Charts:** Added an internet protocol info chart and storage info chart.

### Fixed / Refactored
- **Calculator Refactor:** Removed outage mode from `SimpleCalcView` and cleaned up legacy UI elements.
- **Chart Axis Handling:** Ensured proper axis attachment and scaling for charts with dynamic data ranges.


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