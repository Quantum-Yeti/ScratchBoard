import math
from datetime import datetime

def calculate_stats(model):
    """
    Returns a dict of dashboard statistics calculated relative to a target date.
    - Now respects `override_date_for_stats` for charting over time.
    """

    # Use date override for charts; default to today
    date_override = getattr(model, "override_date_for_stats", None)
    target_date = date_override or datetime.now().date()

    categories = model.get_all_categories()
    all_notes = [
        note
        for category in categories
        for note in model.get_notes(category_name=category)
    ]

    # --- Cumulative total notes up to target date ---
    total_notes = sum(
        1 for n in all_notes
        if datetime.fromisoformat(n["created"]).date() <= target_date
    )

    # --- Notes this month relative to target_date ---
    notes_this_month = sum(
        1 for n in all_notes
        if datetime.fromisoformat(n["created"]).year == target_date.year
           and datetime.fromisoformat(n["created"]).month == target_date.month
    )

    # --- Notes today (or target_date) ---
    notes_today = sum(
        1 for n in all_notes
        if datetime.fromisoformat(n["created"]).date() == target_date
    )

    # --- Word count statistics for notes up to target date ---
    word_counts = [
        len(n["content"].split())
        for n in all_notes
        if n["content"] and datetime.fromisoformat(n["created"]).date() <= target_date
    ]
    avg_words = round(sum(word_counts) / len(word_counts), 1) if word_counts else 0
    longest_note = max(word_counts) if word_counts else 0
    shortest_note = min(word_counts) if word_counts else 0

    # --- Daily words added on target_date ---
    daily_words = sum(
        len(n["content"].split())
        for n in all_notes
        if datetime.fromisoformat(n["created"]).date() == target_date
    )

    # --- Daily edits ---
    daily_edits = sum(
        1
        for n in all_notes
        if "modified" in n and datetime.fromisoformat(n["modified"]).date() == target_date
    )

    # --- Rolling words/notes over the last 7 days ---
    rolling_days = 7
    rolling_notes = sum(
        1
        for n in all_notes
        if 0 <= (target_date - datetime.fromisoformat(n["created"]).date()).days < rolling_days
    ) / rolling_days  # average per day

    rolling_words = sum(
        len(n["content"].split())
        for n in all_notes
        if 0 <= (target_date - datetime.fromisoformat(n["created"]).date()).days < rolling_days
    ) / rolling_days  # average words/day

    # --- Ratio of today's notes / cumulative total ---
    total_ratio = notes_today / max(1, total_notes)

    # --- Notes per category ---
    notes_per_category = total_notes / max(1, len(categories))

    # --- Words per note ---
    words_per_note = sum(word_counts) / max(1, total_notes)

    # --- Words this week (last 7 days) ---
    words_this_week = sum(
        len(n["content"].split())
        for n in all_notes
        if 0 <= (target_date - datetime.fromisoformat(n["created"]).date()).days < 7
    )

    # --- Cumulative words wave for chart (sine normalized) ---
    cumulative_words = sum(
        len(n["content"].split())
        for n in all_notes
        if datetime.fromisoformat(n["created"]).date() <= target_date
    )
    cumulative_wave = math.sin(cumulative_words / 100.0)

    return {
        # Dashboard stats
        "total": total_notes,
        "monthly": notes_this_month,
        "avg_words": avg_words,
        "longest_note": longest_note,
        "shortest_note": shortest_note,
        "today": notes_today,

        # Multi-line chart stats
        "daily_notes": notes_today,
        "daily_words": daily_words,
        "daily_edits": daily_edits,
        "total_ratio": total_ratio,
        "rolling_notes": rolling_notes,
        "rolling_words": rolling_words,
        "notes_per_category": notes_per_category,
        "words_per_note": words_per_note,
        "words_this_week": words_this_week,
        "cumulative_wave": cumulative_wave,
    }
