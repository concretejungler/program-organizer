import os
import json

ENTRY_POINT_PRIORITY = [
    ("*.exe", "exe"),
    ("main.py", "python"),
    ("app.py", "python"),
    ("run.py", "python"),
    ("index.html", "html"),
    ("index.js", "node"),
    ("app.js", "node"),
    ("server.js", "node"),
    ("package.json", "npm"),
    ("*.bat", "batch"),
    ("*.cmd", "batch"),
    ("*.ps1", "powershell"),
]

EXTENSION_TYPE_MAP = {
    ".py": "python",
    ".js": "node",
    ".html": "html",
    ".htm": "html",
    ".exe": "exe",
    ".bat": "batch",
    ".cmd": "batch",
    ".ps1": "powershell",
}


def detect_program_type(filename):
    _, ext = os.path.splitext(filename.lower())
    return EXTENSION_TYPE_MAP.get(ext, "unknown")


def _check_package_json(folder_path, fname):
    """Check if package.json has a start script."""
    pkg_path = os.path.join(folder_path, fname)
    try:
        with open(pkg_path, "r") as f:
            pkg = json.load(f)
        return "scripts" in pkg and "start" in pkg["scripts"]
    except (json.JSONDecodeError, IOError):
        return False


def detect_entry_point(folder_path):
    """Detect the entry point file and program type for a folder."""
    files = os.listdir(folder_path)
    files_lower = {f.lower(): f for f in files}

    for pattern, ptype in ENTRY_POINT_PRIORITY:
        if pattern.startswith("*"):
            ext = pattern[1:]
            for fname in files:
                if fname.lower().endswith(ext):
                    if fname.lower() == "package.json":
                        if _check_package_json(folder_path, fname):
                            return fname, ptype
                    else:
                        return fname, ptype
        else:
            if pattern.lower() in files_lower:
                actual_name = files_lower[pattern.lower()]
                if pattern.lower() == "package.json":
                    if _check_package_json(folder_path, actual_name):
                        return actual_name, ptype
                else:
                    return actual_name, ptype

    # Fallback: single runnable file
    runnable = [f for f in files if detect_program_type(f) != "unknown"]
    if len(runnable) == 1:
        return runnable[0], detect_program_type(runnable[0])

    return None, None


def scan_folder(folder_path):
    """Scan a folder and return a list of detected programs."""
    if not os.path.isdir(folder_path):
        return []

    programs = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isdir(item_path):
            if item.startswith("."):
                continue
            entry, ptype = detect_entry_point(item_path)
            if entry:
                programs.append(
                    {
                        "name": item,
                        "path": item_path,
                        "entry_point": entry,
                        "program_type": ptype,
                    }
                )
        elif os.path.isfile(item_path):
            ptype = detect_program_type(item)
            if ptype != "unknown":
                name = os.path.splitext(item)[0]
                programs.append(
                    {
                        "name": name,
                        "path": item_path,
                        "entry_point": item,
                        "program_type": ptype,
                    }
                )

    return programs
