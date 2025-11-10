from datetime import datetime, timedelta

def calculate_stats(model):
    """
    Returns a dict of dashboard statistics:
    - total notes
    - notes created this month
    - average words per note
    - longest note (in words)
    - shortest note (in words)
    - notes created today
    """

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

    # Notes today
    today = now.date()
    notes_today = sum(
        1
        for n in all_notes
        if datetime.fromisoformat(n["created"]).date() == today
    )

    # Word count statistics
    word_counts = [len(n["content"].split()) for n in all_notes if n["content"]]
    avg_words = round(sum(word_counts) / len(word_counts), 1) if word_counts else 0
    longest_note = max(word_counts) if word_counts else 0
    shortest_note = min(word_counts) if word_counts else 0

    return {
        "total": total_notes,
        "monthly": notes_this_month,
        "avg_words": avg_words,
        "longest_note": longest_note,
        "shortest_note": shortest_note,
        "today": notes_today,
    }
