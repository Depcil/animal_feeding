import sqlite3

from django.shortcuts import render

from db.database import get_connection

PAGE_SIZE = 5

STATUS_FILTERS = {
    "all": (0, 1),
    "active": (0, 0),
    "cancelled": (1, 1),
}

FEEDINGS_SQL = """
    SELECT
        feedings.id,
        feedings.feeding_date,
        animals.name AS animal_name,
        users.name AS user_name,
        feedings.food,
        feedings.amount,
        feedings.is_cancelled
    FROM feedings
    JOIN animals
        ON feedings.animal_id = animals.id
    JOIN users
        ON feedings.user_id = users.id
    WHERE feedings.is_cancelled BETWEEN ? AND ?
    ORDER BY feedings.feeding_date DESC, feedings.id DESC
    LIMIT ? OFFSET ?;
"""

FEEDINGS_COUNT_SQL = """
    SELECT
        COUNT(*) AS feedings_count
    FROM feedings
    WHERE is_cancelled BETWEEN ? AND ?;
"""

FEEDING_SQL = """
    SELECT
        feedings.id,
        feedings.feeding_date,
        feedings.food,
        feedings.amount,
        feedings.is_cancelled,
        feedings.comment,
        animals.id AS animal_id,
        animals.name AS animal_name,
        animals.daily_norm,
        users.name AS user_name,
        users.email AS user_email
    FROM feedings
    JOIN animals
        ON feedings.animal_id = animals.id
    JOIN users
        ON feedings.user_id = users.id
    WHERE feedings.id = ?;
"""

SUMMARY_SQL = """
    SELECT
        COUNT(*) AS total_count,
        COALESCE(SUM(CASE WHEN is_cancelled = 0 THEN 1 ELSE 0 END), 0)
            AS active_count,
        COALESCE(SUM(is_cancelled), 0) AS cancelled_count,
        COALESCE(SUM(CASE WHEN is_cancelled = 0 THEN amount END), 0)
            AS total_amount
    FROM feedings;
"""

NORMS_SQL = """
    SELECT
        COUNT(*) AS animals_count,
        MIN(daily_norm) AS min_norm,
        MAX(daily_norm) AS max_norm,
        ROUND(AVG(daily_norm), 1) AS avg_norm
    FROM animals;
"""

BY_ANIMAL_SQL = """
    SELECT
        animals.name AS animal_name,
        COUNT(feedings.id) AS feedings_count,
        COALESCE(SUM(feedings.amount), 0) AS total_amount
    FROM animals
    LEFT JOIN feedings
        ON animals.id = feedings.animal_id
       AND feedings.is_cancelled = 0
    GROUP BY animals.id, animals.name
    ORDER BY feedings_count DESC, animals.name;
"""

BY_USER_SQL = """
    SELECT
        users.name AS user_name,
        COUNT(feedings.id) AS feedings_count,
        COALESCE(SUM(feedings.amount), 0) AS total_amount
    FROM users
    LEFT JOIN feedings
        ON users.id = feedings.user_id
       AND feedings.is_cancelled = 0
    GROUP BY users.id, users.name
    ORDER BY feedings_count DESC, users.name;
"""

BY_SPECIES_SQL = """
    SELECT
        species,
        COUNT(*) AS animals_count
    FROM animals
    GROUP BY species
    ORDER BY animals_count DESC, species;
"""

FREQUENT_SQL = """
    SELECT
        animals.name AS animal_name,
        COUNT(feedings.id) AS feedings_count
    FROM animals
    JOIN feedings
        ON animals.id = feedings.animal_id
    WHERE feedings.is_cancelled = 0
    GROUP BY animals.id, animals.name
    HAVING COUNT(feedings.id) >= ?
    ORDER BY feedings_count DESC, animals.name;
"""

BY_DATE_SQL = """
    SELECT
        feeding_date,
        COUNT(*) AS feedings_count,
        SUM(amount) AS total_amount
    FROM feedings
    WHERE is_cancelled = 0
    GROUP BY feeding_date
    ORDER BY feeding_date;
"""


def _fetch_all(sql, params=()):
    """Выполнить SELECT и вернуть строки sqlite3.Row (доступ по именам)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _fetch_one(sql, params=()):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()


def _positive_int(value, default):
    return int(value) if value and value.isdigit() and int(value) > 0 \
        else default


def feedings(request):
    status = request.GET.get("status", "all")
    if status not in STATUS_FILTERS:
        status = "all"
    low, high = STATUS_FILTERS[status]

    total = _fetch_one(FEEDINGS_COUNT_SQL, [low, high])["feedings_count"]
    pages = max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    page = min(_positive_int(request.GET.get("page"), 1), pages)
    offset = (page - 1) * PAGE_SIZE

    context = {
        "feedings": _fetch_all(
            FEEDINGS_SQL,
            [low, high, PAGE_SIZE, offset],
        ),
        "total": total,
        "status": status,
        "page": page,
        "pages": pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < pages else None,
    }

    return render(
        request,
        "feedings/feeding_list.html",
        context,
    )


def feeding_detail(request, feeding_id):
    feeding = _fetch_one(FEEDING_SQL, [feeding_id])

    context = {
        "feeding": feeding,
    }

    return render(
        request,
        "feedings/feeding_detail.html",
        context,
        status=404 if feeding is None else 200,
    )


def statistics(request):
    min_count = _positive_int(request.GET.get("min_count"), 2)

    context = {
        "summary": _fetch_one(SUMMARY_SQL),
        "norms": _fetch_one(NORMS_SQL),
        "by_animal": _fetch_all(BY_ANIMAL_SQL),
        "by_user": _fetch_all(BY_USER_SQL),
        "by_species": _fetch_all(BY_SPECIES_SQL),
        "by_date": _fetch_all(BY_DATE_SQL),
        "frequent": _fetch_all(FREQUENT_SQL, [min_count]),
        "min_count": min_count,
    }

    return render(
        request,
        "feedings/statistics.html",
        context,
    )
