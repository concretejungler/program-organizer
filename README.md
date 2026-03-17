# Program Organizer

A desktop application manager for organizing and launching your programs. Drop your project folders into a watched directory, and Program Organizer gives you a clean UI to browse, search, tag, and one-click launch them all.

Built for anyone who creates lots of small programs and needs a central hub to manage them.

## Features

- **Auto-Detection** — Scans your programs folder and detects entry points (Python, Node.js, HTML, executables, batch scripts, PowerShell, NPM projects)
- **One-Click Launch** — Automatically uses the correct runtime to launch each program
- **Tags & Categories** — Create tags and organize your programs however you like
- **Search & Sort** — Instant search by name/description, sort by name, date, or usage
- **Favorites** — Pin your most-used programs to the top
- **Running Indicator** — See which programs are currently running with a live status dot
- **Grid & List Views** — Switch between card grid and compact list
- **System Tray** — Minimize to tray, always accessible
- **Configurable** — Change the watched folder, override runtime paths, customize your workflow
- **Dark Theme** — Easy on the eyes

## Installation

### Download Installer
1. Download `ProgramOrganizer_Setup_1.0.0.exe` from [Releases](../../releases)
2. Run the installer and follow the setup wizard
3. Launch from Start Menu or desktop shortcut

### Run from Source
```bash
# Clone the repo
git clone https://github.com/yourusername/program-organizer.git
cd program-organizer

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

## Usage

1. **Add programs** — Drop your project folders into the `programs/` folder (or change the watched folder in Settings)
2. **Launch** — Click the green Launch button on any program card
3. **Organize** — Add descriptions, create tags, mark favorites
4. **Search** — Use the search bar or filter by tags in the sidebar

See [TUTORIAL.md](TUTORIAL.md) for the full usage guide.

## Building from Source

### Build the Executable
```bash
python build.py
```
Output goes to `dist/ProgramOrganizer/`.

### Build the Installer
1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Run `build.py` first to create the executable
3. Open `installer.iss` in Inno Setup
4. Click Build → Compile
5. Installer is created in `installer_output/`

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Database:** SQLite
- **File Watching:** Watchdog
- **System Tray:** pystray + Pillow
- **Packaging:** PyInstaller
- **Installer:** Inno Setup

## Supported Program Types

| Type | Entry Points | Launch Method |
|------|-------------|---------------|
| Python | `main.py`, `app.py`, `run.py`, `*.py` | `python <file>` |
| Node.js | `index.js`, `app.js`, `server.js` | `node <file>` |
| Web App | `index.html` | Opens in browser |
| NPM | `package.json` (with start script) | `npm start` |
| Executable | `*.exe` | Direct execution |
| Batch | `*.bat`, `*.cmd` | `cmd /c <file>` |
| PowerShell | `*.ps1` | `powershell -File <file>` |

## License

MIT License — see [LICENSE](LICENSE) for details.
