import os
import shutil
import subprocess
import webbrowser


def detect_runtime(runtime_type, configured_path="auto"):
    """Find the runtime executable path."""
    if configured_path and configured_path != "auto":
        return configured_path

    runtime_names = {
        "python": ["python", "python3"],
        "node": ["node"],
        "npm": ["npm"],
    }

    names = runtime_names.get(runtime_type, [])
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def build_launch_command(program_type, entry_point, program_path, runtime_overrides=None):
    """Build the command to launch a program. Returns list of args or None for browser-based."""
    overrides = runtime_overrides or {}

    if program_type == "python":
        runtime = detect_runtime("python", overrides.get("python", "auto"))
        return [runtime or "python", entry_point]

    elif program_type == "node":
        runtime = detect_runtime("node", overrides.get("node", "auto"))
        return [runtime or "node", entry_point]

    elif program_type == "html":
        return None  # Handled via webbrowser.open

    elif program_type == "exe":
        return [os.path.join(program_path, entry_point)]

    elif program_type == "batch":
        return ["cmd", "/c", entry_point]

    elif program_type == "powershell":
        return ["powershell", "-ExecutionPolicy", "Bypass", "-File", entry_point]

    elif program_type == "npm":
        runtime = detect_runtime("npm", overrides.get("npm", "auto"))
        return [runtime or "npm", "start"]

    return None


def launch_program(program_type, entry_point, program_path, runtime_overrides=None):
    """Launch a program and return the process PID or None."""
    if program_type == "html":
        full_path = os.path.join(program_path, entry_point)
        if os.path.isfile(program_path):
            full_path = program_path
        webbrowser.open(f"file:///{os.path.abspath(full_path)}")
        return None

    cmd = build_launch_command(program_type, entry_point, program_path, runtime_overrides)
    if not cmd:
        return None

    # Determine working directory
    if os.path.isfile(program_path):
        cwd = os.path.dirname(program_path)
    else:
        cwd = program_path

    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        return process.pid
    except Exception as e:
        raise RuntimeError(f"Failed to launch: {e}")


def is_process_running(pid):
    """Check if a process with the given PID is still running."""
    if pid is None:
        return False
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            exit_code = ctypes.c_ulong()
            kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            kernel32.CloseHandle(handle)
            return exit_code.value == 259  # STILL_ACTIVE
        return False
    except Exception:
        return False


def stop_process(pid):
    """Stop a running process by PID."""
    if pid is None:
        return False
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, False, pid)
        if handle:
            kernel32.TerminateProcess(handle, 0)
            kernel32.CloseHandle(handle)
            return True
        return False
    except Exception:
        return False
