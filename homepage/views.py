import sqlite3

from django.shortcuts import render

from db.database import get_connection

COUNTS_SQL = """
    SELECT
        (SELECT COUNT(*) FROM animals) AS animals_count,
        (SELECT COUNT(*) FROM feedings WHERE is_cancelled = 0)
            AS active_feedings;
"""


def index(request):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        counts = conn.execute(COUNTS_SQL).fetchone()
    finally:
        conn.close()

    return render(
        request,
        "homepage/index.html",
        {"counts": counts},
    )


def page_not_found(request, exception):
    return render(
        request,
        "404.html",
        status=404,
    )
