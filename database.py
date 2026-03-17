import sqlite3
from datetime import datetime

DEFAULT_SETTINGS = {
    "watched_folder": "./programs/",
    "runtime_python": "auto",
    "runtime_node": "auto",
    "view_mode": "grid",
    "scan_interval": "5",
}


class Database:
    def __init__(self, db_path="programs.db"):
        self.db_path = db_path
        self.conn = None

    def init(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()
        self._init_default_settings()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                entry_point TEXT,
                program_type TEXT,
                description TEXT DEFAULT '',
                icon TEXT,
                favorite BOOLEAN DEFAULT 0,
                launch_count INTEGER DEFAULT 0,
                last_launched DATETIME,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                pid INTEGER
            );

            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS program_tags (
                program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
                tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (program_id, tag_id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self.conn.commit()

    def _init_default_settings(self):
        for key, value in DEFAULT_SETTINGS.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        self.conn.commit()

    def execute(self, sql, params=()):
        return self.conn.execute(sql, params)

    def close(self):
        if self.conn:
            self.conn.close()

    # Programs
    def add_program(self, name, path, entry_point, program_type, description=""):
        cur = self.conn.execute(
            "INSERT INTO programs (name, path, entry_point, program_type, description) VALUES (?, ?, ?, ?, ?)",
            (name, path, entry_point, program_type, description),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_program(self, prog_id):
        row = self.conn.execute(
            "SELECT * FROM programs WHERE id = ?", (prog_id,)
        ).fetchone()
        return dict(row) if row else None

    def update_program(self, prog_id, **kwargs):
        allowed = {
            "name",
            "description",
            "entry_point",
            "icon",
            "favorite",
            "pid",
            "program_type",
        }
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [prog_id]
        self.conn.execute(
            f"UPDATE programs SET {set_clause} WHERE id = ?", values
        )
        self.conn.commit()

    def delete_program(self, prog_id):
        self.conn.execute("DELETE FROM programs WHERE id = ?", (prog_id,))
        self.conn.commit()

    def list_programs(self, search=None, tag=None, sort="name", favorites_only=False):
        query = "SELECT DISTINCT p.* FROM programs p"
        params = []
        joins = []
        conditions = []

        if tag:
            joins.append(
                "JOIN program_tags pt ON p.id = pt.program_id JOIN tags t ON pt.tag_id = t.id"
            )
            conditions.append("t.name = ?")
            params.append(tag)

        if search:
            conditions.append("(p.name LIKE ? OR p.description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        if favorites_only:
            conditions.append("p.favorite = 1")

        query += " " + " ".join(joins)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        sort_map = {
            "name": "p.name ASC",
            "date_added": "p.date_added DESC",
            "last_launched": "p.last_launched DESC",
            "launch_count": "p.launch_count DESC",
        }
        query += f" ORDER BY p.favorite DESC, {sort_map.get(sort, 'p.name ASC')}"

        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def record_launch(self, prog_id):
        self.conn.execute(
            "UPDATE programs SET launch_count = launch_count + 1, last_launched = ? WHERE id = ?",
            (datetime.now().isoformat(), prog_id),
        )
        self.conn.commit()

    def program_exists_by_path(self, path):
        row = self.conn.execute(
            "SELECT id FROM programs WHERE path = ?", (path,)
        ).fetchone()
        return dict(row)["id"] if row else None

    # Tags
    def add_tag(self, name):
        cur = self.conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
        self.conn.commit()
        return cur.lastrowid

    def list_tags(self):
        rows = self.conn.execute("SELECT * FROM tags ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def delete_tag(self, tag_id):
        self.conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        self.conn.commit()

    def add_program_tag(self, program_id, tag_id):
        self.conn.execute(
            "INSERT OR IGNORE INTO program_tags (program_id, tag_id) VALUES (?, ?)",
            (program_id, tag_id),
        )
        self.conn.commit()

    def remove_program_tag(self, program_id, tag_id):
        self.conn.execute(
            "DELETE FROM program_tags WHERE program_id = ? AND tag_id = ?",
            (program_id, tag_id),
        )
        self.conn.commit()

    def get_program_tags(self, program_id):
        rows = self.conn.execute(
            "SELECT t.* FROM tags t JOIN program_tags pt ON t.id = pt.tag_id WHERE pt.program_id = ?",
            (program_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # Settings
    def get_setting(self, key):
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def set_setting(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        self.conn.commit()

    def get_all_settings(self):
        rows = self.conn.execute("SELECT * FROM settings").fetchall()
        return {row["key"]: row["value"] for row in rows}
