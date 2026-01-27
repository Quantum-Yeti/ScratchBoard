import math
from datetime import datetime, timedelta

from PySide6.QtGui import QTextDocument


def calculate_stats(model):
    """
    Returns a dict of statistics for the multi-line chart calculated relative to a target date.
    Respects `override_date_for_stats` for charting over time.
    """

    ### --- Target date ---###
    target_date = getattr(model, "override_date_for_stats", None) or datetime.now().date()

    ### --- Contacts / References ---###
    num_contacts = model.get_contacts_up_to(target_date)  # number of contacts
    num_links = model.get_references_up_to(target_date)  # number of custom links

    ### --- Collect notes ---###
    categories = model.get_all_categories()
    all_notes = [
        note
        for category in categories
        for note in model.get_notes(category_name=category)
    ]

    ### --- Pre-filtered note views ---###
    notes_up_to_date = []
    notes_today = []
    notes_yesterday = []

    for n in all_notes:
        created_date = datetime.fromisoformat(n["created"]).date()

        if created_date <= target_date:
            notes_up_to_date.append(n)

        if created_date == target_date:
            notes_today.append(n)

        elif created_date == target_date - timedelta(days=1):
            notes_yesterday.append(n)

    ### --- Note counts ---###
    total_notes = len(notes_up_to_date)
    notes_today_count = len(notes_today)
    notes_yesterday_count = len(notes_yesterday)

    notes_this_month = sum(
        1 for n in notes_up_to_date
        if datetime.fromisoformat(n["created"]).year == target_date.year
        and datetime.fromisoformat(n["created"]).month == target_date.month
    )

    if notes_yesterday_count > 0:
        daily_notes_growth = (notes_today_count - notes_yesterday_count) / notes_yesterday_count * 100
    else:
        daily_notes_growth = 0  # If there were no notes yesterday, set growth to 0

    # Ensure that `daily_notes_growth` is not negative
    daily_notes_growth = max(0, daily_notes_growth)

    ### --- Category distribution & entropy --- ###
    category_counts = {}

    for category in categories:
        category_counts[category] = sum(
            1 for n in notes_up_to_date
            if "category" in n and n["category"] == category
        )

    total_categorized = sum(category_counts.values())

    category_entropy = 0.0

    if total_categorized > 0:
        for count in category_counts.values():
            if count > 0:
                p = count / total_categorized
                category_entropy -= p * math.log(p)

    # Normalize entropy to 0–1 range
    max_entropy = math.log(len(category_counts)) if len(category_counts) > 1 else 1
    category_entropy_norm = category_entropy / max_entropy

    ### --- Word statistics ---###
    def clean_text(html: str) -> str:
        """Convert HTML/RTF-like content to plain text for accurate word counts."""
        if not html:
            return ""
        doc = QTextDocument()
        doc.setHtml(html)  # Automatically strips HTML tags
        return doc.toPlainText().strip()

    ### --- Word statistics ---###
    word_counts = []
    daily_words = 0

    for n in notes_up_to_date:
        content = clean_text(n["content"])
        if not content:
            continue

        words = len(content.split())
        word_counts.append(words)

        # Count words for today separately
        created_date = datetime.fromisoformat(n["created"]).date()
        if created_date == target_date:
            daily_words += words

    avg_words = round(sum(word_counts) / len(word_counts), 1) if word_counts else 0
    longest_note = max(word_counts, default=0)
    shortest_note = min(word_counts, default=0)

    ### --- Daily edits ---###
    daily_edits = sum(
        1
        for n in notes_today
        if "modified" in n
        and datetime.fromisoformat(n["modified"]).date() == target_date
    )

    ### --- Rolling 7-day stats ---###
    rolling_days = 7

    rolling_notes = sum(
        1
        for n in notes_up_to_date
        if 0 <= (target_date - datetime.fromisoformat(n["created"]).date()).days < rolling_days
    ) / rolling_days

    rolling_notes_in_window = [
        n for n in notes_up_to_date
        if 0 <= (target_date - datetime.fromisoformat(n["created"]).date()).days < rolling_days
    ]

    if rolling_notes_in_window:
        rolling_words = sum(len(n["content"].split()) for n in rolling_notes_in_window if n["content"]) \
                        / len(rolling_notes_in_window)  # mean words per note
    else:
        rolling_words = 0

    # Ensure `rolling_notes` and `rolling_words` are not negative
    rolling_notes = max(0, int(rolling_notes))
    rolling_words = max(0, rolling_words)

    ### --- Derived ratios ---###
    total_ratio = notes_today_count / max(1, total_notes)
    notes_per_category = total_notes / max(1, len(categories))
    words_per_note = sum(word_counts) / max(1, total_notes)

    ### --- Weekly & cumulative --- ###
    words_this_week = sum(
        len(n["content"].split())
        for n in notes_up_to_date
        if 0 <= (target_date - datetime.fromisoformat(n["created"]).date()).days < 7
        and n["content"]
    )

    cumulative_words = sum(word_counts)
    cumulative_wave = math.sin(cumulative_words / 100.0)

    # Return stats with safeguards to ensure no negative values
    return {
        # Dashboard
        "total": total_notes,
        "monthly": notes_this_month,
        "avg_words": avg_words,
        "longest_note": longest_note,
        "shortest_note": shortest_note,
        "today": notes_today_count,

        # Chart stats
        "daily_notes": notes_today_count,
        "daily_notes_growth": round(daily_notes_growth, 2),
        "daily_words": daily_words,
        "daily_edits": daily_edits,
        "total_ratio": total_ratio,
        "rolling_notes": rolling_notes,
        "rolling_words": rolling_words,
        "notes_per_category": notes_per_category,
        "words_per_note": words_per_note,
        "words_this_week": words_this_week,
        "cumulative_wave": cumulative_wave,
        "category_entropy": round(category_entropy, 4),
        "category_entropy_norm": round(category_entropy_norm, 4),
        "contacts": num_contacts,
        "links": num_links,
    }
