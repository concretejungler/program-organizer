# Program Organizer - Tutorial

A step-by-step guide to using Program Organizer.

---

## 1. Installation

### From Installer (Recommended)
1. Download `ProgramOrganizer_Setup_1.0.0.exe`
2. Run the installer
3. Choose your install location (default is fine)
4. Optionally check "Create desktop icon"
5. Click **Install**
6. Click **Finish** to launch the app

### From Source
1. Make sure Python 3.9+ is installed
2. Open a terminal in the project folder
3. Run:
   ```
   pip install -r requirements.txt
   python app.py
   ```
4. The app opens in your browser automatically

---

## 2. First Launch

When you first open Program Organizer:
- A browser tab opens with the UI
- A system tray icon appears (blue circle with play button)
- The app watches the `programs/` folder inside the install directory by default

---

## 3. Adding Programs

### Method 1: Drop into the programs folder
1. Find your programs folder (default: `programs/` in the app directory)
2. Copy or move your program folders into it
3. The app automatically detects new programs within a few seconds
4. Click the **refresh button** (circular arrows) in the top bar to scan immediately

### What gets detected?
The app looks for these entry points in each folder (in priority order):
- `.exe` files
- `main.py`, `app.py`, `run.py`
- `index.html`
- `index.js`, `app.js`, `server.js`
- `package.json` (with a `start` script)
- `.bat`, `.cmd`, `.ps1` files

Loose files (not in subfolders) are also detected by their extension.

---

## 4. Launching Programs

1. Find the program you want to run
2. Click the green **Launch** button on its card
3. The app automatically uses the correct runtime:
   - Python scripts → runs with `python`
   - Node.js files → runs with `node`
   - HTML files → opens in your browser
   - Executables → runs directly
   - NPM projects → runs `npm start`

### Running Programs
- Running programs show a **green pulsing dot** on their card
- The **Launch** button changes to a red **Stop** button
- The sidebar shows a count of running programs under "Running"

---

## 5. Organizing Programs

### Adding Descriptions
1. Click on a program card to open the edit panel
2. Fill in the **Description** field
3. Click **Save**

### Creating Tags
1. Click the **+** button next to "Tags" in the sidebar
2. Enter a tag name (e.g., "game", "tool", "web app")
3. Click **Add Tag**

### Tagging Programs
1. Click a program card to open the edit panel
2. In the **Tags** section, click tags to select/deselect them
3. Click **Save**

### Filtering by Tag
- Click any tag in the sidebar to filter programs by that tag
- Click the same tag again to clear the filter

### Favorites
- Click the **star icon** on a program card to favorite it
- Favorites always appear at the top of the list
- Click "Favorites" in the sidebar to show only favorites

---

## 6. Searching and Sorting

### Search
- Use the search bar at the top to find programs by name or description
- Search is instant — results update as you type
- Keyboard shortcut: **Ctrl+F** to focus the search bar

### Sort
- Use the dropdown next to the search bar to sort by:
  - **Name** (alphabetical)
  - **Date Added** (newest first)
  - **Last Launched** (most recent first)
  - **Most Launched** (highest count first)

### View Modes
- Click the **grid/list toggle** button to switch between:
  - **Grid view**: Large cards with full details
  - **List view**: Compact rows for quick scanning

---

## 7. Changing the Watched Folder

1. Click the **gear icon** (Settings) in the top-right
2. Update the **Watched Folder** path to any folder on your system
3. Click **Save Settings**
4. The app immediately starts watching the new folder

---

## 8. Configuring Runtimes

By default, the app auto-detects Python and Node.js from your system PATH.

To use a specific version:
1. Open **Settings** (gear icon)
2. Enter the full path to the runtime in the Python or Node.js field
   - Example: `C:\Python311\python.exe`
3. Click **Save Settings**

Leave the field empty to use auto-detection.

---

## 9. System Tray

The app runs in the system tray (bottom-right of your taskbar):
- **Double-click** the tray icon to open the UI
- **Right-click** for a menu with:
  - Open Program Organizer
  - Quit

You can close the browser tab — the app keeps running in the tray. Just double-click the tray icon to reopen it.

---

## 10. Managing Programs

### Edit a Program
Click on any program card to:
- Change its display name
- Add or update the description
- Change the entry point file
- Add or remove tags
- View program info (path, launch count, dates)

### Delete a Program
1. Click the **trash icon** on a program card
2. Confirm the deletion
3. This only removes it from Program Organizer — your files are NOT deleted

### Open Program Folder
Click the **folder icon** on a program card to see the program's file path.

---

## 11. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Focus search bar |
| `Escape` | Close any open panel or modal |

---

## 12. Troubleshooting

### Programs not showing up?
- Make sure the program folder has a recognizable entry point (see Section 3)
- Click the refresh button to trigger a manual rescan
- Check that the watched folder path is correct in Settings

### Program won't launch?
- Check that the required runtime (Python, Node.js) is installed
- Verify the runtime path in Settings
- Make sure the entry point file exists and is correct

### App won't start?
- Check if another instance is already running (look for the tray icon)
- Try running from source: `python app.py`

### Port conflicts?
The app automatically picks a free port on each launch, so port conflicts should not occur.
