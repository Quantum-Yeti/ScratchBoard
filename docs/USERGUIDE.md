# Scratch Board - User Guide

**Author:** Quantum Yeti  
**Repository:** [Scratch Board GitHub](https://github.com/quantum-yeti/scratchboard)  

---

## Table of Contents

1. [Product Overview](#product-overview)  
2. [Key Features](#key-features)  
3. [User Interface & Navigation](#user-interface--navigation)  
4. [Data Storage & Exporting](#data-storage--exporting)  
5. [Installation Options](#installation-options)  
6. [Core Application Features](#core-application-features)  
   - [Dashboard](#dashboard)  
   - [Sticky Notes](#sticky-notes)  
   - [Notepad](#notepad)  
   - [Contacts](#contacts)  
   - [Password Generator](#password-generator)  
   - [Information Charts](#information-charts)  
   - [Note Editor/Preview](#note-editorpreview)  
7. [Tools & Libraries](#tools--libraries)  
8. [Development Tools](#development-tools)  
9. [Support](#support)

---

## Product Overview

Scratch Board is a lightweight desktop productivity application designed for CSRs and ISP support staff to capture, organize, and explore information efficiently. It combines note-taking, sticky notes, and advanced tools like MAC address lookups and DOCSIS log parsing into a single intuitive workspace.

---

## Key Features

- **Scratch Notes:** Create colorful, draggable, and resizable sticky notes that auto-save.  
- **Custom Links:** Quickly add or delete links to helpful resources.  
- **Modem Log Parser:** Analyze DOCSIS modem logs to troubleshoot network issues.  
- **Execute Batch Files:** Run Windows batch files for task automation.  
- **Notepad:** Integrated text editor for plain-text files.  
- **MAC Vendor Lookup:** Query MAC addresses using the IEEE OUI database.  
- **Password Generator:** Generate secure passwords with customizable entropy.  
- **Charts:** View signal strength, bandwidth, and network statistics.  

---

## User Interface & Navigation

- **Dashboard:** Displays statistics, multi-line charts, and widgets in real-time.  
- **Sidebar Navigation:** Quickly switch between views and tools.  
- **Contacts Rolodex:** Add, edit, or delete contacts.  
- **Note Categories:** Organize notes under categories like Internet, Email, Phone, Video, Streaming, Notes, Ideas.  

---

## Data Storage & Exporting

- **Local Database Storage:** Scratch Board uses SQLite for storing notes, contacts, and categorized data.  
- **Database Folder:** All app data is stored in `%LOCALAPPDATA%\ScratchBoardData`.  
- **Export/Import:** Export the database to JSON for portability and import it back when needed.  

---

## Installation Options

Scratch Board can be installed either as a standalone executable or via the Microsoft Store. Both methods are simple and require minimal setup.

### 1. Standalone EXE Installation

1. Download the latest **ScratchBoard.exe** from the [GitHub Repository](https://github.com/quantum-yeti/scratchboard) under **Assets**.  
2. Place it on your Desktop. The app will automatically create the `ScratchBoardData` folder inside `%LOCALAPPDATA%` on first run.  
3. Double-click `ScratchBoard.exe` to launch.  
4. If Windows SmartScreen appears:  
   - Click **More info → Run anyway**.  
5. To reopen the app later, just double-click `ScratchBoard.exe`.  
6. No installation or extra configuration is required; the app is portable.  

*Note:* You do **not** need to manually create the `ScratchBoardData` folder; the app handles it automatically.

---

### 2. Microsoft Store Installation

1. Open the **Microsoft Store** on your Windows device.  
2. Search for **Scratch Board** (or visit the store link once your app is published).  
3. Click **Get / Install**. The app will automatically install and create the `%LOCALAPPDATA%\ScratchBoardData` folder.  
4. Launch the app from the Start menu or pinned shortcut.  
5. Updates will be delivered automatically through the Microsoft Store.  

*Note:* Data stored in `%LOCALAPPDATA%\ScratchBoardData` is preserved across app updates.  
*Note:* You do **not** need to manually create the `ScratchBoardData` folder; the app handles it automatically.

---

## Core Application Features

### Dashboard

The dashboard shows key stats, multi-line charts, a MAC vendor lookup tool, and a custom link widget. It also provides a quick note-taking area.  

*![Dashboard Screenshot](/screenshots/screenshotdash.png)*

---

### Sticky Notes

- Create, edit, drag, and resize notes.  
- Auto-save ensures notes are never lost.  
- Simple manager window to add or view all sticky notes.  

*![Sticky Notes Screenshot](/screenshots/sticky_notes.png)*  

---

### Notepad

- Full-featured plain-text editor.  
- Create, edit, save, and open files without leaving the app.  

*![Notepad Screenshot](/screenshots/notepad.png)*

---

### Contacts

- Add, edit, and remove contacts.  
- Store name, email, phone, and website.  

*![Contacts Screenshot](/screenshots/contacts.png)*  

---

### Password Generator

- Three modes of password generation.  
- Customize length, complexity, and entropy.  

*![Password Generator Screenshot](/screenshots/passgen.png)*  

---

### Information Charts

- Visualize DOCSIS signals, fiber signals, bandwidth, and other metrics.  
- Supports troubleshooting and decision-making.  

*![Charts Screenshot](/screenshots/charts.png)*  

---

### Note Editor/Preview

- Integrated editor for rich-text notes.  
- Supports images, bullet points, and headings.  

*![Note Editor Screenshot](/screenshots/note_editor.png)*  

---

## Tools & Libraries

**Key Libraries:**

- `altgraph`, `pyinstaller`, `pyinstaller-hooks-contrib` – for packaging  
- `PyQt5-Qt5`, `PyQt5_sip`, `PySide6` – GUI framework  
- `python-dateutil`, `pytz` – date and timezone handling  
- `pywin32-ctypes` – Windows API integration  
- `PyYAML`, `Markdown`, `markdown2` – data processing and text parsing  
- `Pillow` – image manipulation

*(Full library list in requirements.txt)*  

---

## Development Tools

- **Python** – main language  
- **PyCharm** – IDE for development
- **PyQt/PySide** - GUI Framework
- **Git / GitHub** – version control  
- **pytest** – testing  
- **Flake8** – code style enforcement  
- **Virtualenv & pip** – environment and dependency management  

---

## Support

- Submit an issue: [GitHub Issues](https://github.com/quantum-yeti/scratchboard/issues)  
- For general questions: email **quantumyetii [at] outlook [dot] com** 
- Check the FAQ for common troubleshooting  

---

*End of User Guide*