# Import / Export Database
import json
import shutil
import uuid
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from utils.image_io import save_file_drop

class ImportExportService:
    def __init__(self, note_model):
        """
        note_model is injected to reuse:
        - get_notes()
        - get_contacts()
        - get_references()
        - add_note()
        - add_contact()
        - add_reference()
        """
        self.note_model = note_model
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
                "categories": self.note_model.get_all_categories(),
                "notes": [],
                "contacts": [],
                "references": []
            }

            # Export notes
            for note in self.note_model.get_notes():
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
            for contact in self.note_model.get_contacts():
                export_data["contacts"].append(dict(contact))

            # Export references
            for ref in self.note_model.get_references():
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
            self.note_model.add_category(category_name)

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
            self.note_model.add_note(
                category_name=note.get("category_name", "Notes"),
                title=note["title"],
                content=note["content"],
                image_path=note.get("image_path"),
                tags=tags
            )

        # Import contacts
        for contact in data.get("contacts", []):
            self.note_model.add_contact(
                category_name=contact.get("category_name", "Contacts"),
                name=contact["name"],
                phone=contact.get("phone"),
                email=contact.get("email"),
                website=contact.get("website")
            )

        # Import references
        for ref in data.get("references", []):
            title = ref.get("title")
            url = ref.get("url")

            if not title or not url:
                print("Skipping reference: missing title or url →", ref)
                continue

            try:
                self.note_model.add_reference(title, url)
            except Exception as e:
                print("Reference import error:", e)

        # Clean up temp folder
        shutil.rmtree(import_dir)
        print(f"Data imported from {zip_path}")

    def close(self):
        self.note_model = None