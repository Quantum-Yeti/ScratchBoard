import json
import os

import sqlite3
import uuid
import random
from datetime import datetime

from domain.autocomplete.note_index import NoteIndex
from services.exp_imp_service import ImportExportService

PASTEL_COLORS = ["#FFEBEE", "#FFF3E0", "#E8F5E9", "#E3F2FD", "#F3E5F5"]

class NoteModel:
    """
    A class to manage notes, contacts, reference links, and categories.
    Provides CRUD operations, search, and import/export functionality.
    Uses SQLite as the backend database.
    """
    def __init__(self, db_path=None):
        """
        Initialize the NoteModel instance.
        Creates the database and tables if they do not exist.

        Args:
            db_path (str):
                        Path to SQLite database file.
                        Defaults to "sb_data/db/notes.db".
        """
        if db_path is None:
            os.makedirs("sb_data/db", exist_ok=True)
            db_path = os.path.join("sb_data/db", "notes.db")

        self.conn = sqlite3.connect(db_path)

        # Enable dictionary access to rows
        self.conn.row_factory = sqlite3.Row
        self._setup_db()

        self.import_export = ImportExportService(self)

        # Initialize the Trie algo for autocomplete
        self.index = NoteIndex()
        self._build_autocomplete_index()

    def _setup_db(self):
        """
        Create tables and default categories if they don't exist.
        Handles notes, contacts, reference_links, and categories.
        Adds necessary indexes for performance.
        """
        cur = self.conn.cursor()

        # Categories table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );
        """)

        # Notes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                category_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                color TEXT,
                image_path TEXT,
                tags TEXT,
                created TEXT NOT NULL,
                updated TEXT NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            );
        """)

        # FTS5 Note Search
        cur.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                    note_id,
                    title,
                    content,
                    tags
                );
            """)

        #cur = self.conn.cursor()

        # Backwards compatibility
        try:
            cur.execute("ALTER TABLE notes ADD COLUMN tags TEXT;")
        except sqlite3.OperationalError:
            # Column already exists
            pass

        self.conn.commit()

        # Contacts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                category_id INTEGER,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                website TEXT,
                created TEXT NOT NULL,
                updated TEXT NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            );
        """)

        # Quick Links/References table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "reference_links" (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                created TEXT NOT NULL,
                updated TEXT NOT NULL
            );
        """)
        cur.execute('CREATE INDEX IF NOT EXISTS idx_reference_links_title ON reference_links(title)')

        # --- Default categories
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Notes')")
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Contacts')")

        # --- Indexes ---
        cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_cat ON notes(category_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_contacts_cat ON contacts(category_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated)")

        cur.execute("""
            INSERT INTO notes_fts(note_id, title, content, tags)
            SELECT id, title, content, tags FROM notes
            WHERE id NOT IN (SELECT note_id FROM notes_fts);
        """)

        self.conn.commit()

    ### CATEGORY METHODS ###
    def add_category(self, name):
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
        cur.execute("SELECT id FROM categories WHERE name=?", (name,))
        row = cur.fetchone()
        return row["id"] if row else None

    def get_all_categories(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM categories ORDER BY name ASC")
        return [row["name"] for row in cur.fetchall()]

    ### NOTES METHODS ###
    def add_note(self, category_name, title, content, image_path=None, tags=None):
        note_id = str(uuid.uuid4())
        color = random.choice(PASTEL_COLORS)
        now = datetime.now().isoformat()
        category_id = self.add_category(category_name)

        if tags and isinstance(tags, str):
            tags = [tags]
        tags_json = json.dumps(tags) if tags else None

        self.conn.execute("""
            INSERT INTO notes (id, category_id, title, content, color, image_path, tags, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (note_id, category_id, title, content, color, image_path, tags_json, now, now))

        self.conn.execute("""
            INSERT INTO notes_fts(note_id, title, content, tags)
            VALUES (?, ?, ?, ?)
        """, (note_id, title, content, tags_json))

        self.index.index_note(
            note_id=note_id,
            title=title,
            content=content,
            tags=tags
        )

        self.conn.commit()
        return note_id

    def get_notes(self, category_name=None, search=None, order_by="updated DESC"):
        cur = self.conn.cursor()
        params = []
        # --- FTS search path ---
        if search:
            query = """
                   SELECT notes.*, categories.name AS category_name
                   FROM notes
                   JOIN notes_fts ON notes_fts.note_id = notes.id
                   LEFT JOIN categories ON notes.category_id = categories.id
                   WHERE notes_fts MATCH ?
               """
            params.append(search)

            if category_name and category_name != "All Categories":
                query += " AND categories.name = ?"
                params.append(category_name)

            query += f" ORDER BY {order_by}"

            cur.execute(query, params)
            return cur.fetchall()

        # --- Non-search (normal listing) path ---
        query = """
               SELECT notes.*, categories.name AS category_name
               FROM notes
               LEFT JOIN categories ON notes.category_id = categories.id
               WHERE 1=1
           """

        if category_name and category_name != "All Categories":
            query += " AND categories.name = ?"
            params.append(category_name)
        query += f" ORDER BY {order_by}"
        cur.execute(query, params)
        return cur.fetchall()

    def get_note_by_id(self, note_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT notes.*, categories.name as category_name
            FROM notes
            LEFT JOIN categories ON notes.category_id = categories.id
            WHERE notes.id=?
        """, (note_id,))
        return cur.fetchone()

    def edit_note(self, note_id, title=None, content=None, category_name=None, image_path=None, tags=None):
        note = self.get_note_by_id(note_id)
        if not note:
            return False

        fields, params = [], []
        if title is not None:
            fields.append("title=?")
            params.append(title)
        if content is not None:
            fields.append("content=?")
            params.append(content)
        if category_name is not None:
            category_id = self.add_category(category_name)
            fields.append("category_id=?")
            params.append(category_id)
        if image_path is not None:
            fields.append("image_path=?")
            params.append(image_path)
        if tags is not None:
            if isinstance(tags, str):
                tags = [tags]
            fields.append("tags=?")
            params.append(json.dumps(tags))

        fields.append("updated=?")
        params.append(datetime.now().isoformat())
        params.append(note_id)

        query = f"UPDATE notes SET {', '.join(fields)} WHERE id=?"
        self.conn.execute(query, params)

        # --- FTS sync ---
        self.conn.execute("""
            DELETE FROM notes_fts WHERE note_id = ?
        """, (note_id,))

        self.conn.execute("""
            INSERT INTO notes_fts(note_id, title, content, tags)
            SELECT id, title, content, tags
            FROM notes
            WHERE id = ?
        """, (note_id,))

        self.index.remove_note(note_id)

        self.index.index_note(
            note_id=note_id,
            title=title or note["title"],
            content=content or note["content"],
            tags=tags or note["tags"]
        )

        self.conn.commit()
        return True

    def delete_note(self, note_id):
        self.conn.execute("DELETE FROM notes_fts WHERE note_id=?", (note_id,))
        self.conn.execute("DELETE FROM notes WHERE id=?", (note_id,))

        self.index.remove_note(note_id)

        self.conn.commit()
        return True

    ### CONTACTS METHODS ###
    def add_contact(self, category_name, name, phone=None, email=None, website=None):
        contact_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        category_id = self.add_category(category_name)
        self.conn.execute("""
            INSERT INTO contacts (id, category_id, name, phone, email, website, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (contact_id, category_id, name, phone, email, website, now, now))
        self.conn.commit()
        return contact_id

    def get_contacts(self, category_name=None):
        cur = self.conn.cursor()
        params = []
        query = """
            SELECT contacts.*, categories.name as category_name
            FROM contacts
            LEFT JOIN categories ON contacts.category_id = categories.id
            WHERE 1=1
        """
        if category_name and category_name != "All Categories":
            query += " AND categories.name=?"
            params.append(category_name)
        cur.execute(query, params)
        return cur.fetchall()

    def get_contact_by_id(self, contact_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT contacts.*, categories.name as category_name
            FROM contacts
            LEFT JOIN categories ON contacts.category_id = categories.id
            WHERE contacts.id=?
        """, (contact_id,))
        return cur.fetchone()

    def edit_contact(self, contact_id, name=None, phone=None, email=None, website=None):
        contact = self.get_contact_by_id(contact_id)
        if not contact:
            return False

        fields, params = [], []
        if name is not None:
            fields.append("name=?")
            params.append(name)
        if phone is not None:
            fields.append("phone=?")
            params.append(phone)
        if email is not None:
            fields.append("email=?")
            params.append(email)
        if website is not None:
            fields.append("website=?")
            params.append(website)

        fields.append("updated=?")
        params.append(datetime.now().isoformat())
        params.append(contact_id)

        query = f"UPDATE contacts SET {', '.join(fields)} WHERE id=?"
        self.conn.execute(query, params)
        self.conn.commit()
        return True

    def delete_contact(self, contact_id):
        self.conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
        self.conn.commit()
        return True

    ### REFERENCE WIDGET METHODS ###
    def add_reference(self, title, url):
        ref_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        self.conn.execute(
            'INSERT INTO reference_links (id, title, url, created, updated) VALUES (?, ?, ?, ?, ?)',
            (ref_id, title, url, now, now)
        )
        self.conn.commit()
        return ref_id

    def get_references(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM reference_links ORDER BY title ASC')
        return cur.fetchall()

    def edit_reference(self, ref_id, title=None, url=None):
        ref = self.get_reference_by_id(ref_id)
        if not ref:
            return False
        fields, params = [], []
        if title is not None:
            fields.append("title=?")
            params.append(title)
        if url is not None:
            fields.append("url=?")
            params.append(url)
        fields.append("updated=?")
        params.append(datetime.now().isoformat())
        params.append(ref_id)
        query = f"UPDATE reference_links SET {', '.join(fields)} WHERE id=?"
        self.conn.execute(query, params)
        self.conn.commit()
        return True

    def delete_reference(self, ref_id):
        self.conn.execute("DELETE FROM reference_links WHERE id=?", (ref_id,))
        self.conn.commit()
        return True

    def get_reference_by_id(self, ref_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM reference_links WHERE id=?", (ref_id,))
        return cur.fetchone()

    ### MISCELLANEOUS METHODS ###
    def search_notes(self, term, category_name=None):
        return self.get_notes(search=term, category_name=category_name)

    def get_most_recent_note(self):
        categories = self.get_all_categories()
        notes = []
        for cat in categories:
            notes.extend(self.get_notes(category_name=cat))
        if not notes:
            return None
        notes.sort(key=lambda n: n["created"], reverse=True)
        return notes[0]

    def get_contacts_up_to(self, target_date):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) AS count
            FROM contacts
            WHERE date(created) <= ?
        """, (target_date.isoformat(),))
        return cur.fetchone()["count"]

    def get_references_up_to(self, target_date):
        """
            Returns the count of references (links) created up to the target_date.
            Ensures the date comparison is only on the date portion.
            """
        cur = self.conn.cursor()
        # Ensure that target_date is in 'YYYY-MM-DD' format for comparison
        target_date_str = target_date.strftime('%Y-%m-%d')

        # Use DATE() function to ensure comparison is done on date part only (ignoring time)
        cur.execute("""
                SELECT COUNT(*) AS count
                FROM reference_links
                WHERE DATE(created) <= ?
            """, (target_date_str,))

        # Fetch the count of references
        return cur.fetchone()["count"]

    def close(self):
        self.conn.close()

    def _build_autocomplete_index(self):
        """
        Build Trie + inverted index from all existing notes.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, content, tags FROM notes")

        for row in cur.fetchall():
            tags = row["tags"]
            if tags:
                try:
                    tags = json.loads(tags)
                except json.JSONDecodeError:
                    tags = [tags]

            self.index.index_note(
                note_id=row["id"],
                title=row["title"],
                content=row["content"],
                tags=tags
            )

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        return self.index.autocomplete(prefix, limit)

    def search_by_prefix(self, prefix: str):
        """
        Autocomplete → resolve to notes
        """
        results = []
        seen = set()

        for word in self.index.autocomplete(prefix):
            for note_id in self.index.notes_for_word(word):
                if note_id in seen:
                    continue
                seen.add(note_id)

                note = self.get_note_by_id(note_id)
                if note:
                    results.append(note)

        return results

    # Method to return export to zip
    def export_to_zip(self, zip_path: str):
        return self.import_export.export_to_zip(zip_path)

    # Method to return import from zip
    def import_from_zip(self, zip_path: str):
        return self.import_export.import_from_zip(zip_path)