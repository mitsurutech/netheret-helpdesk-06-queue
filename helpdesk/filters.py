"""Template filters: small functions templates use to show values nicely.

In a template, {{ ticket.created_at|datetime }} calls show_datetime.
"""


def show_datetime(value):
    """12 Nov 2026, 14:05"""
    if value is None:
        return ""
    return value.strftime("%d %b %Y, %H:%M")


def show_date(value):
    """Wed 12 Nov"""
    if value is None:
        return ""
    return value.strftime("%a %d %b")


def register(app):
    app.add_template_filter(show_datetime, "datetime")
    app.add_template_filter(show_date, "date")
