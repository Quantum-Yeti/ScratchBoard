import json
import os
import shutil
import sqlite3
import uuid
import random
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

from utils.image_io import save_file_drop

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

        cur = self.conn.cursor()
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
                website TEXT,
                email TEXT,
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
        self.conn.commit()
        return note_id

    def get_notes(self, category_name=None, search=None, order_by="updated DESC"):
        cur = self.conn.cursor()
        params = []
        query = """
            SELECT notes.*, categories.name as category_name
            FROM notes
            LEFT JOIN categories ON notes.category_id = categories.id
            WHERE 1=1
        """
        if category_name and category_name != "All Categories":
            query += " AND categories.name=?"
            params.append(category_name)
        if search:
            term = f"%{search}%"
            query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
            params.extend([term, term, term])
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
        self.conn.commit()
        return True

    def delete_note(self, note_id):
        self.conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.conn.commit()
        return True

    ### CONTACTS METHODS ###
    def add_contact(self, category_name, name, phone=None, website=None, email=None):
        contact_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        category_id = self.add_category(category_name)
        self.conn.execute("""
            INSERT INTO contacts (id, category_id, name, phone, website, email, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (contact_id, category_id, name, phone, website, email, now, now))
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

    def edit_contact(self, contact_id, name=None, phone=None, website=None, email=None):
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
        if website is not None:
            fields.append("website=?")
            params.append(website)
        if email is not None:
            fields.append("email=?")
            params.append(email)

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
    def search_notes(self, term):
        return self.get_notes(search=term)

    def get_most_recent_note(self):
        categories = self.get_all_categories()
        notes = []
        for cat in categories:
            notes.extend(self.get_notes(category_name=cat))
        if not notes:
            return None
        notes.sort(key=lambda n: n["created"], reverse=True)
        return notes[0]

    def close(self):
        self.conn.close()

    # Import / Export Database
    def export_to_zip(self, zip_path: str):
        """
        Export all data (notes, contacts, references, categories) and images
        into a single ZIP file.
        """
        temp_dir = Path("sb_temp_export")
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Copy images to a temp folder
        images_dir = temp_dir / "images"
        images_dir.mkdir(exist_ok=True)

        export_data = {
            "categories": self.get_all_categories(),
            "notes": [],
            "contacts": [],
            "references": []
        }

        # Export notes
        for note in self.get_notes():
            note_dict = dict(note)

            # Always resolve through real image directory
            img_path = note_dict.get("image_path")

            if not img_path:
                # No image → just add note and continue
                export_data["notes"].append(note_dict)
                continue

            # Normalize path
            src = Path(img_path)

            # If broken/relative path → try sb_data/images
            if not src.is_file():
                candidate = Path("sb_data/images") / src.name
                if candidate.is_file():
                    src = candidate
                else:
                    print(f"[EXPORT WARNING] Image not found: {img_path}")
                    # keep note but remove image reference
                    note_dict.pop("image_path", None)
                    export_data["notes"].append(note_dict)
                    continue

            # Copy file to temp/images
            dst_name = f"{uuid.uuid4()}_{src.name}"
            dst = images_dir / dst_name
            shutil.copy(src, dst)

            # Update note's path relative to ZIP
            note_dict["image_path"] = f"images/{dst_name}"

            export_data["notes"].append(note_dict)

        # Copy image folder
        sb_images = Path("sb_data/images")
        if sb_images.is_dir():
            for file in sb_images.glob("*.*"):
                # Avoid name collisions: only copy if filename not already used
                dst = images_dir / file.name
                if not dst.exists():
                    shutil.copy(file, dst)

        # Copy notepad folder
        sb_notepad = Path("sb_data/notepad")
        notepad_dst = temp_dir / "notepad"
        notepad_dst.mkdir(exist_ok=True)

        if sb_notepad.exists():
            for txt_file in sb_notepad.glob("*.txt"):
                shutil.copy(txt_file, notepad_dst / txt_file.name)

        # Export contacts
        for contact in self.get_contacts():
            export_data["contacts"].append(dict(contact))

        # Export references
        for ref in self.get_references():
            export_data["references"].append(dict(ref))

        # Write JSON
        json_path = temp_dir / "notes_export.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        # Create ZIP
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as zipf:
            # Add JSON file
            zipf.write(json_path, arcname="notes_export.json")

            # Add images
            for img_file in images_dir.glob("*.*"):
                zipf.write(img_file, arcname=f"images/{img_file.name}")

            # Add notepad txt files
            for txt_file in notepad_dst.glob("*.txt"):
                zipf.write(txt_file, arcname=f"notepad/{txt_file.name}")

        # Clean up temp folder
        shutil.rmtree(temp_dir)
        print(f"Data exported to {zip_path}")

    def import_from_zip(self, zip_path: str):
        """
        Import notes, contacts, references, and images from a ZIP export.
        Images are copied to the local image folder.
        """
        import_dir = Path("sb_temp_import")
        import_dir.mkdir(parents=True, exist_ok=True)

        with ZipFile(zip_path, "r") as zipf:
            zipf.extractall(import_dir)

        src_images = import_dir / "images"
        dst_images = Path("sb_data/images")
        dst_images.mkdir(parents=True, exist_ok=True)

        if src_images.exists():
            for file in src_images.glob("*.*"):
                try:
                    shutil.copy(file, dst_images / file.name)
                except Exception as e:
                    print("Failed copying image:", file, e)

        src_notepad = import_dir / "notepad"
        dst_notepad = Path("sb_data/notepad")
        dst_notepad.mkdir(parents=True, exist_ok=True)

        if src_notepad.exists():
            for txt_file in src_notepad.glob("*.txt"):
                shutil.copy(txt_file, dst_notepad / txt_file.name)

        # Load JSON
        json_path = import_dir / "notes_export.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Import categories
        for category_name in data.get("categories", []):
            self.add_category(category_name)

        # Import notes
        for note in data.get("notes", []):

            img_path = note.get("image_path")
            if img_path:
                src = import_dir / img_path
                if src.is_file():
                    # Copies image to local folder and returns relative path
                    new_path = save_file_drop(str(src))
                    note["image_path"] = new_path

            tags = note.get("tags")
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except json.JSONDecodeError:
                    tags = [tags]  # fallback if not valid JSON
            self.add_note(
                category_name=note.get("category_name", "Notes"),
                title=note["title"],
                content=note["content"],
                image_path=note.get("image_path"),
                tags=tags
            )

        # Import contacts
        for contact in data.get("contacts", []):
            self.add_contact(
                category_name=contact.get("category_name", "Contacts"),
                name=contact["name"],
                phone=contact.get("phone"),
                website=contact.get("website"),
                email=contact.get("email")
            )

        # Import references
        for ref in data.get("references", []):
            title = ref.get("title")
            url = ref.get("url")

            if not title or not url:
                print("Skipping reference: missing title or url →", ref)
                continue

            try:
                self.add_reference(title, url)
            except Exception as e:
                print("Reference import error:", e)

        # Clean up temp folder
        shutil.rmtree(import_dir)
        print(f"Data imported from {zip_path}")

    # DANGER ZONE: DELETE DATABASE FROM FILE MENU
    def nuke_everything(self):
        try:
            self.conn.close()
        except Exception:
            pass

        # Remove sb_data directory
        sb_data = Path("sb_data")
        if sb_data.exists():
            shutil.rmtree(sb_data)

        # Recreate file structure
        (sb_data / "db").mkdir(parents=True, exist_ok=True)
        (sb_data / "images").mkdir(parents=True, exist_ok=True)
        (sb_data / "notepad").mkdir(parents=True, exist_ok=True)

        # Recreate database connection
        db_path = sb_data / "db" / "notes.db"
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        # Recreate schema + defaults
        self._setup_db()

        print("All assets have been nuked.")

