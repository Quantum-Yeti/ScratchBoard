import math
from datetime import datetime, timedelta

def calculate_stats(model):
    """
    Returns a dict of dashboard statistics:
    - total notes
    - notes created this month
    - average words per note
    - longest note (in words)
    - shortest note (in words)
    - notes created today (or target date if overridden)
    """

    # date override for charts
    date_override = getattr(model, "override_date_for_stats", None)

    if date_override is None:
        target_date = datetime.now().date()
    else:
        target_date = date_override

    categories = model.get_all_categories()
    all_notes = [
        note
        for category in categories
        for note in model.get_notes(category_name=category)
    ]

    total_notes = len(all_notes)

    # Notes this month
    now = datetime.now()
    notes_this_month = sum(
        1
        for n in all_notes
        if datetime.fromisoformat(n["created"]).month == now.month
           and datetime.fromisoformat(n["created"]).year == now.year
    )

    # notes_today uses target_date
    notes_today = sum(
        1
        for n in all_notes
        if datetime.fromisoformat(n["created"]).date() == target_date
    )

    # Word count statistics
    word_counts = [len(n["content"].split()) for n in all_notes if n["content"]]
    avg_words = round(sum(word_counts) / len(word_counts), 1) if word_counts else 0
    longest_note = max(word_counts) if word_counts else 0
    shortest_note = min(word_counts) if word_counts else 0

    # Daily notes created (already equals notes_today)
    daily_notes = notes_today

    # Daily words added
    daily_words = sum(
        len(n["content"].split())
        for n in all_notes
        if datetime.fromisoformat(n["created"]).date() == target_date
    )

    # Daily edits (count any note modified today)
    daily_edits = sum(
        1
        for n in all_notes
        if "modified" in n and datetime.fromisoformat(n["modified"]).date() == target_date
    )

    # Normalized cumulative total (safe even if total=0)
    total_norm = total_notes / max(total_notes, 1)

    # Rolling stats will be filled by caller (chart builder), so return placeholders:
    rolling_notes = daily_notes
    rolling_words = daily_words

    # Ratio of notes today / notes total
    today_ratio = notes_today / max(1, total_notes)

    # Notes per category (mean)
    notes_per_category = total_notes / max(1, len(categories))

    # Words per note
    words_per_note = sum(word_counts) / max(1, total_notes)

    # Words in the last week added
    words_this_week = sum(
        len(n["content"].split())
        for n in all_notes
        if (target_date - datetime.fromisoformat(n["created"]).date()).days < 7
    )

    # Cumulative words
    cumulative_words = sum(
        len(n["content"].split())
        for n in all_notes
        if datetime.fromisoformat(n["created"]).date() <= target_date
    )
    cumulative_wave = math.sin(cumulative_words / 100.0)

    return {
        #Dashboard stats
        "total": total_notes,
        "monthly": notes_this_month,
        "avg_words": avg_words,
        "longest_note": longest_note,
        "shortest_note": shortest_note,
        "today": notes_today,  # now "target_date"

        # Multi-line chart stats
        "daily_notes": daily_notes,
        "daily_words": daily_words,
        "daily_edits": daily_edits,
        "total_norm": total_norm,
        "rolling_notes": rolling_notes,
        "rolling_words": rolling_words,
        "total_ratio": today_ratio,
        "notes_per_category": notes_per_category,
        "words_per_note": words_per_note,
        "words_this_week": words_this_week,
        "cumulative_wave": cumulative_wave,
    }
