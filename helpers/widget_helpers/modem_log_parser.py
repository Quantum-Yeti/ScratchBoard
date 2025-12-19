import re
from datetime import datetime

class ModemEvent:
    def __init__(self, timestamp, message, category, severity, explanation, steps=None):
        self.timestamp = timestamp
        self.message = message
        self.category = category
        self.severity = severity
        self.explanation = explanation
        self.steps = steps or []

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "message": self.message,
            "category": self.category,
            "severity": self.severity,
            "explanation": self.explanation,
            "steps": self.steps
        }


class ModemLogParser:

    # Patterns grouped by DOCSIS issue type
    RULES = [
        # Upstream Problems
        (
            r"T3 time-out|No Ranging Response|Ranging Request",
            "Upstream / Noise",
            "High",
            "Modem is not reliably hearing the CMTS. Usually upstream noise, bad connector, splitter, or plant issue.",
            [
                "Check all coax connections and splitters for tightness and corrosion",
                "Inspect coax cable for physical damage",
                "Remove any unnecessary splitters in the line",
                "Verify upstream signal levels in modem stats",
                "Check for known ISP service outages in your area"
            ]
        ),
        (
            r"T4 timeout",
            "Upstream Failure",
            "Critical",
            "Modem has completely lost upstream connectivity. Often a service outage or severe upstream noise.",
            [
                "Restart the modem",
                "Check upstream power levels via modem interface",
                "Inspect cabling for loose connections",
                "Contact ISP to verify upstream node status"
            ]
        ),

        # Downstream Problems
        (
            r"MDD Timeout|Loss of Sync|SYNC Timing",
            "Downstream / SNR",
            "High",
            "Modem lost downstream lock. Indicates low SNR, loose coax, bad drop, or plant noise.",
            [
                "Check downstream signal levels and SNR in modem stats",
                "Inspect coax for loose connections",
                "Ensure no damaged splitters or cable drops",
                "Monitor for repeated loss; may indicate ISP-side issues"
            ]
        ),
        (
            r"OFDMA? Profile|Correctables|Uncorrectables",
            "Downstream OFDM",
            "Medium",
            "OFDM channel issues—signal distortion, low MER, poor coax or splitter loss.",
            [
                "Check OFDM channel statistics in modem",
                "Inspect coax connections and splitters",
                "Avoid long runs of damaged or low-quality cable",
                "Contact ISP if persistent or high uncorrectable counts"
            ]
        ),

        # Provisioning / IP
        (
            r"DHCP|No Offer|Discover sent",
            "Provisioning / IP",
            "High",
            "Modem cannot obtain an IP address. Usually an outage, CMTS unreachable, or upstream noise.",
            [
                "Power cycle modem",
                "Verify DHCP server reachability",
                "Check upstream signal levels",
                "Contact ISP if IP not assigned after retries"
            ]
        ),
        (
            r"TOD Failure",
            "Provisioning / Time-of-Day",
            "Low",
            "Time-of-day server unreachable—not service impacting unless persistent.",
            [
                "Check modem's system time",
                "Ensure modem firmware is up to date",
                "Verify network connectivity to NTP/TOD server",
                "Usually safe to ignore if connectivity is otherwise normal"
            ]
        ),

        # Customer-side / Device
        (
            r"Power Reset|Reboot|Cold Start",
            "Device Reboot",
            "Info",
            "Modem rebooted. Could be customer reboot or power instability.",
            [
                "Check power supply and UPS",
                "Ensure modem is not overheating",
                "Inspect for power outages",
                "Check event frequency to rule out hardware issue"
            ]
        ),
        (
            r"LAN|WiFi|WLAN",
            "LAN/WiFi",
            "Low",
            "LAN/WiFi subsystem event—normally not service impacting.",
            [
                "Check LAN/WiFi connections",
                "Restart WiFi if needed",
                "Inspect for interference or IP conflicts",
                "Generally informational only"
            ]
        ),
    ]

    # Timestamp patterns
    TIMESTAMP_PATTERNS = [
        r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]",  # [2025-11-20 08:15:23]
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",      # 2025-11-20 08:15:23
        r"(\d+/\d+/\d+ \d+:\d+:\d+)",                  # 11/20/2025 08:15:23
    ]

    CATEGORY_SEVERITY_PATTERN = re.compile(r"\((?P<category>[^/]+)/(?P<severity>[^)]+)\)")

    GENERIC_KEYWORDS = {
        "upstream": ("Upstream / Noise", "High"),
        "downstream": ("Downstream / SNR", "High"),
        "dhcp": ("Provisioning / IP", "High"),
        "reboot": ("Device Reboot", "Info"),
        "lan": ("LAN/WiFi", "Low"),
        "wifi": ("LAN/WiFi", "Low"),
    }

    def parse(self, raw_text):
        events = []

        lines = raw_text.splitlines()
        for line in lines:
            clean = line.strip()
            if not clean:
                continue

            timestamp = self._extract_timestamp(clean)

            category = "General"
            severity = "Info"
            explanation = "No detailed rule matched."
            steps = []  # default empty list

            for pattern, cat, sev, expl, rule_steps in self.RULES:
                if re.search(pattern, clean, re.IGNORECASE):
                    category, severity, explanation, steps = cat, sev, expl, rule_steps
                    break

            events.append(
                ModemEvent(timestamp, clean, category, severity, explanation, steps)
            )

        return events

    def _match_rules(self, line):
        # Check explicit RULES
        for pattern, cat, sev, expl in self.RULES:
            if re.search(pattern, line, re.IGNORECASE):
                return cat, sev, expl

        # Check if line has (CATEGORY/SEVERITY)
        cs_match = self.CATEGORY_SEVERITY_PATTERN.search(line)
        if cs_match:
            cat = cs_match.group("category")
            sev = cs_match.group("severity")
            return cat, sev, "Matched via explicit category/severity in log."

        # Fallback
        for kw, (cat, sev) in self.GENERIC_KEYWORDS.items():
            if kw.lower() in line.lower():
                return cat, sev, f"Matched keyword '{kw}' for fallback categorization."

        # No rule matched
        return "General", "Info", "No detailed rule matched."

    def summarize(self, events):
        summary = {}
        for ev in events:
            key = ev.category
            summary.setdefault(key, {"count": 0, "severity": ev.severity})
            summary[key]["count"] += 1
        return summary

    def _extract_timestamp(self, line):
        for pattern in self.TIMESTAMP_PATTERNS:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return "Unknown"
