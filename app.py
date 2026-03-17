import os
import sys
import socket
import threading
import webbrowser
from flask import Flask, jsonify, request, send_from_directory, send_file

from database import Database
from scanner import scan_folder
from launcher import launch_program, is_process_running, stop_process, detect_runtime
from watcher import FolderWatcher

db = None
watcher = None


def get_base_dir():
    """Get the base directory (works for both dev and PyInstaller)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir():
    """Get the directory where bundled resources (static/) live."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def do_scan():
    """Scan the watched folder and sync with database."""
    global db
    watched = db.get_setting("watched_folder")
    if not os.path.isabs(watched):
        watched = os.path.join(get_base_dir(), watched)
    watched = os.path.normpath(watched)

    if not os.path.isdir(watched):
        os.makedirs(watched, exist_ok=True)
        return []

    found = scan_folder(watched)
    existing_paths = {p["path"] for p in db.list_programs()}

    for prog in found:
        if prog["path"] not in existing_paths:
            db.add_program(
                name=prog["name"],
                path=prog["path"],
                entry_point=prog["entry_point"],
                program_type=prog["program_type"],
            )

    return found


def create_app(db_path=None, programs_dir=None, testing=False):
    global db, watcher

    resource_dir = get_resource_dir()
    static_dir = os.path.join(resource_dir, "static")
    app = Flask(__name__, static_folder=static_dir, static_url_path="")

    base_dir = get_base_dir()
    if db_path is None:
        db_path = os.path.join(base_dir, "programs.db")

    db = Database(db_path)
    db.init()

    if programs_dir:
        db.set_setting("watched_folder", programs_dir)

    # Initial scan
    do_scan()

    if not testing:
        # Start folder watcher
        watched = db.get_setting("watched_folder")
        if not os.path.isabs(watched):
            watched = os.path.join(base_dir, watched)
        watched = os.path.normpath(watched)
        os.makedirs(watched, exist_ok=True)
        watcher = FolderWatcher(watched, lambda: do_scan())
        watcher.start()

    # --- Routes ---

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/favicon.ico")
    def favicon():
        icon_path = os.path.join(get_base_dir(), "icon.ico")
        if os.path.exists(icon_path):
            return send_file(icon_path, mimetype="image/x-icon")
        return "", 204

    # Programs API
    @app.route("/api/programs")
    def list_programs():
        search = request.args.get("search")
        tag = request.args.get("tag")
        sort = request.args.get("sort", "name")
        favorites = request.args.get("favorites") == "true"
        programs = db.list_programs(
            search=search, tag=tag, sort=sort, favorites_only=favorites
        )
        for p in programs:
            p["running"] = is_process_running(p.get("pid"))
            p["tags"] = db.get_program_tags(p["id"])
        return jsonify(programs)

    @app.route("/api/programs/<int:prog_id>")
    def get_program(prog_id):
        prog = db.get_program(prog_id)
        if not prog:
            return jsonify({"error": "Not found"}), 404
        prog["running"] = is_process_running(prog.get("pid"))
        prog["tags"] = db.get_program_tags(prog_id)
        return jsonify(prog)

    @app.route("/api/programs/<int:prog_id>", methods=["PUT"])
    def update_program(prog_id):
        data = request.json
        tag_ids = data.pop("tag_ids", None)
        db.update_program(prog_id, **data)
        if tag_ids is not None:
            current = {t["id"] for t in db.get_program_tags(prog_id)}
            new = set(tag_ids)
            for tid in new - current:
                db.add_program_tag(prog_id, tid)
            for tid in current - new:
                db.remove_program_tag(prog_id, tid)
        return jsonify({"status": "ok"})

    @app.route("/api/programs/<int:prog_id>", methods=["DELETE"])
    def delete_program(prog_id):
        db.delete_program(prog_id)
        return jsonify({"status": "ok"})

    @app.route("/api/programs/<int:prog_id>/launch", methods=["POST"])
    def launch(prog_id):
        prog = db.get_program(prog_id)
        if not prog:
            return jsonify({"error": "Not found"}), 404

        settings = db.get_all_settings()
        overrides = {
            "python": settings.get("runtime_python", "auto"),
            "node": settings.get("runtime_node", "auto"),
        }

        try:
            pid = launch_program(
                prog["program_type"],
                prog["entry_point"],
                prog["path"],
                runtime_overrides=overrides,
            )
            db.record_launch(prog_id)
            if pid:
                db.update_program(prog_id, pid=pid)
            return jsonify({"status": "launched", "pid": pid})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/programs/<int:prog_id>/stop", methods=["POST"])
    def stop(prog_id):
        prog = db.get_program(prog_id)
        if not prog:
            return jsonify({"error": "Not found"}), 404
        if prog.get("pid"):
            stop_process(prog["pid"])
            db.update_program(prog_id, pid=None)
        return jsonify({"status": "stopped"})

    @app.route("/api/programs/<int:prog_id>/status")
    def status(prog_id):
        prog = db.get_program(prog_id)
        if not prog:
            return jsonify({"error": "Not found"}), 404
        running = is_process_running(prog.get("pid"))
        return jsonify({"running": running})

    # Tags API
    @app.route("/api/tags")
    def list_tags():
        return jsonify(db.list_tags())

    @app.route("/api/tags", methods=["POST"])
    def create_tag():
        name = request.json.get("name", "").strip()
        if not name:
            return jsonify({"error": "Name required"}), 400
        tag_id = db.add_tag(name)
        return jsonify({"id": tag_id, "name": name}), 201

    @app.route("/api/tags/<int:tag_id>", methods=["DELETE"])
    def delete_tag(tag_id):
        db.delete_tag(tag_id)
        return jsonify({"status": "ok"})

    # Settings API
    @app.route("/api/settings")
    def get_settings():
        return jsonify(db.get_all_settings())

    @app.route("/api/settings", methods=["PUT"])
    def update_settings():
        global watcher
        data = request.json
        for key, value in data.items():
            db.set_setting(key, value)

        if "watched_folder" in data and watcher:
            new_path = data["watched_folder"]
            if not os.path.isabs(new_path):
                new_path = os.path.join(get_base_dir(), new_path)
            new_path = os.path.normpath(new_path)
            os.makedirs(new_path, exist_ok=True)
            watcher.update_folder(new_path)
            do_scan()

        return jsonify({"status": "ok"})

    # System API
    @app.route("/api/scan", methods=["POST"])
    def scan():
        do_scan()
        return jsonify({"status": "ok"})

    @app.route("/api/runtimes")
    def runtimes():
        settings = db.get_all_settings()
        return jsonify(
            {
                "python": detect_runtime(
                    "python", settings.get("runtime_python", "auto")
                ),
                "node": detect_runtime("node", settings.get("runtime_node", "auto")),
                "npm": detect_runtime("npm", "auto"),
            }
        )

    return app


def main():
    port = find_free_port()
    app = create_app()

    # Start system tray
    from tray import SystemTray

    def on_quit():
        global watcher
        if watcher:
            watcher.stop()
        os._exit(0)

    tray = SystemTray(port, on_quit)
    tray.start()

    # Open browser
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()

    print(f"Program Organizer running at http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
