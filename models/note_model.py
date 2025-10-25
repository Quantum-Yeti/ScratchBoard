import sqlite3
import uuid
import random
from datetime import datetime

PASTEL_COLORS = ["#FFEBEE", "#FFF3E0", "#E8F5E9", "#E3F2FD", "#F3E5F5"]

class NoteModel:
    def __init__(self, db_path="notes.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._setup_db()

    def _setup_db(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                category_id INTEGER,
                title TEXT,
                content TEXT,
                color TEXT,
                image_path TEXT,
                created TEXT,
                updated TEXT,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        """)
        self.conn.commit()

    # --- Categories ---
    def add_category(self, name):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
        cur.execute("SELECT id FROM categories WHERE name=?", (name,))
        return cur.fetchone()["id"]

    def get_all_categories(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM categories ORDER BY name")
        return [row["name"] for row in cur.fetchall()]

    def get_note_count_by_category(self, category_name):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM notes
            WHERE category_id=(SELECT id FROM categories WHERE name=?)
        """, (category_name,))
        return cur.fetchone()[0]

    # --- Notes ---
    def add_note(self, category_name, title, content, image_path=None):
        note_id = str(uuid.uuid4())
        color = random.choice(PASTEL_COLORS)
        now = datetime.now().isoformat()
        category_id = self.add_category(category_name)

        self.conn.execute("""
            INSERT INTO notes (id, category_id, title, content, color, image_path, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (note_id, category_id, title, content, color, image_path, now, now))
        self.conn.commit()
        return note_id

    def get_notes(self, category_name=None, search=None, order_by="updated DESC"):
        cur = self.conn.cursor()
        params = []
        query = "SELECT notes.*, categories.name as category_name FROM notes " \
                "LEFT JOIN categories ON notes.category_id = categories.id WHERE 1=1"
        if category_name:
            query += " AND categories.name=?"
            params.append(category_name)
        if search:
            query += " AND (title LIKE ? OR content LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term])
        query += f" ORDER BY {order_by}"
        cur.execute(query, params)
        return cur.fetchall()

    def get_note_by_id(self, note_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT notes.*, categories.name as category_name
            FROM notes LEFT JOIN categories ON notes.category_id = categories.id
            WHERE notes.id=?
        """, (note_id,))
        return cur.fetchone()

    def edit_note(self, note_id, title=None, content=None, category_name=None, image_path=None):
        note = self.get_note_by_id(note_id)
        if not note:
            return False
        fields, params = [], []
        if title is not None: fields.append("title=?"); params.append(title)
        if content is not None: fields.append("content=?"); params.append(content)
        if category_name is not None:
            category_id = self.add_category(category_name)
            fields.append("category_id=?"); params.append(category_id)
        if image_path is not None: fields.append("image_path=?"); params.append(image_path)
        fields.append("updated=?"); params.append(datetime.now().isoformat())
        params.append(note_id)
        query = f"UPDATE notes SET {', '.join(fields)} WHERE id=?"
        self.conn.execute(query, params)
        self.conn.commit()
        return True

    def delete_note(self, note_id):
        self.conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.conn.commit()

    def search_notes(self, term):
        return self.get_notes(search=term)

    def close(self):
        self.conn.close()
