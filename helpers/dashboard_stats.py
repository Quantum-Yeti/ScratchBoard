# helpers/dashboard_stats.py

from datetime import datetime

def calculate_stats(model):
    """
    Returns a dict of dashboard statistics:
    - total notes
    - number of categories
    - notes created this month
    """

    categories = model.get_all_categories()
    all_notes = [
        note
        for category in categories
        for note in model.get_notes(category_name=category)
    ]

    total = len(all_notes)
    cats = len(categories)
    monthly_count = sum(
        1
        for n in all_notes
        if datetime.fromisoformat(n["created"]).month == datetime.now().month
    )

    return {
        "total": total,
        "cats": cats,
        "monthly": monthly_count,
    }
