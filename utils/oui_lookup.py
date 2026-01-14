import os
import csv
from utils.resource_path import resource_path

class OUILookup:
    """
    Helper utility class that parses the included IEEE OUI csv file.
    """
    def __init__(self, csv_path="resources/ieee_oui.csv"):
        self.csv_path = resource_path(csv_path)
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"OUI CSV not found: {self.csv_path}")

        self.oui_24 = {}  # MA-L
        self.oui_28 = {}  # MA-M
        self.oui_36 = {}  # MA-S

        self.load_oui_data()

    def load_oui_data(self):
        with open(self.csv_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Normal 24-bit OUI ("XX-XX-XX")
                assignment = row.get("Assignment", "").replace("-", "").upper()
                if len(assignment) == 6:
                    name = row.get("Organization Name", "Unknown").strip()
                    address = row.get("Organization Address", "").strip()
                    self.oui_24[assignment] = (name, address)

                # MA-M → 28-bit (7 hex chars)
                mam = row.get("MA-M", "").replace("-", "").upper()
                if len(mam) == 7:
                    name = row.get("Organization Name", "Unknown").strip()
                    address = row.get("Organization Address", "").strip()
                    self.oui_28[mam] = (name, address)

                # MA-S → 36-bit (9 hex chars)
                mas = row.get("MA-S", "").replace("-", "").upper()
                if len(mas) == 9:
                    name = row.get("Organization Name", "Unknown").strip()
                    address = row.get("Organization Address", "").strip()
                    self.oui_36[mas] = (name, address)

    def lookup(self, mac: str) -> tuple[str, str, str]:
        """
        Function that returns: (Vendor Name, Address, Assignment Type) from the included IEEE oui csv.
        """
        mac = mac.replace(":", "").replace("-", "").replace(".", "").upper()

        if len(mac) < 6:
            return "Invalid MAC", "", ""

        # MA-S: longest match first (36 bit)
        prefix_36 = mac[:9]
        if prefix_36 in self.oui_36:
            name, address = self.oui_36[prefix_36]
            return name, address, "MA-S (36-bit)"

        # MA-M: next longest match (28 bit)
        prefix_28 = mac[:7]
        if prefix_28 in self.oui_28:
            name, address = self.oui_28[prefix_28]
            return name, address, "MA-M (28-bit)"

        # MA-L: fallback (24 bit)
        prefix_24 = mac[:6]
        if prefix_24 in self.oui_24:
            name, address = self.oui_24[prefix_24]
            return name, address, "MA-L (24-bit)"

        return "Unknown Vendor", "Unknown", ""
