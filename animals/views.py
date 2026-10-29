import sqlite3
from datetime import date

from django.shortcuts import render

from db.database import get_connection

ANIMALS_SQL = """
    SELECT
        id,
        name,
        species,
        daily_norm
    FROM animals
    WHERE (? = ''
           OR name LIKE '%' || ? || '%'
           OR species LIKE '%' || ? || '%')
      AND daily_norm >= ?
    ORDER BY name;
"""

ANIMAL_SQL = """
    SELECT
        id,
        name,
        species,
        daily_norm
    FROM animals
    WHERE id = ?;
"""

ANIMAL_DAY_FEEDINGS_SQL = """
    SELECT
        feedings.id,
        feedings.food,
        feedings.amount,
        feedings.is_cancelled,
        users.name AS user_name
    FROM feedings
    JOIN users
        ON feedings.user_id = users.id
    WHERE feedings.animal_id = ?
      AND feedings.feeding_date = ?
    ORDER BY feedings.id;
"""

ANIMAL_FED_SQL = """
    SELECT
        COALESCE(SUM(amount), 0) AS fed
    FROM feedings
    WHERE animal_id = ?
      AND feeding_date = ?
      AND is_cancelled = 0;
"""

AVAILABLE_SQL = """
    SELECT
        animals.id,
        animals.name,
        animals.species,
        animals.daily_norm,
        COALESCE(SUM(feedings.amount), 0) AS fed,
        animals.daily_norm - COALESCE(SUM(feedings.amount), 0) AS remaining
    FROM animals
    LEFT JOIN feedings
        ON feedings.animal_id = animals.id
       AND feedings.feeding_date = ?
       AND feedings.is_cancelled = 0
    GROUP BY animals.id, animals.name, animals.species, animals.daily_norm
    HAVING remaining > 0
    ORDER BY animals.name;
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


def _parse_date(value):
    """Строка YYYY-MM-DD -> та же строка или None, если формат неверный."""
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError):
        return None


def animals(request):
    query = request.GET.get("q", "").strip()
    min_norm_raw = request.GET.get("min_norm", "").strip()
    min_norm = int(min_norm_raw) if min_norm_raw.isdigit() else 0
    # Все значения уходят в запрос параметрами ?, текст SQL не меняется.
    animals_list = _fetch_all(
        ANIMALS_SQL,
        [query, query, query, min_norm],
    )

    context = {
        "animals": animals_list,
        "query": query,
        "min_norm": min_norm_raw,
    }

    return render(
        request,
        "animals/animal_list.html",
        context,
    )


def animal_detail(request, animal_id):
    animal = _fetch_one(ANIMAL_SQL, [animal_id])
    feeding_date = (
        _parse_date(request.GET.get("date")) or date.today().isoformat()
    )

    context = {
        "animal": animal,
        "feeding_date": feeding_date,
    }

    if animal is not None:
        fed = _fetch_one(ANIMAL_FED_SQL, [animal_id, feeding_date])["fed"]
        context["fed"] = fed
        context["remaining"] = max(animal["daily_norm"] - fed, 0)
        context["day_feedings"] = _fetch_all(
            ANIMAL_DAY_FEEDINGS_SQL,
            [animal_id, feeding_date],
        )

    return render(
        request,
        "animals/animal_detail.html",
        context,
        status=404 if animal is None else 200,
    )


def available_animals(request):
    raw_date = request.GET.get("date", "")
    feeding_date = _parse_date(raw_date)
    animals_list = []
    if feeding_date:
        animals_list = _fetch_all(AVAILABLE_SQL, [feeding_date])

    context = {
        "animals": animals_list,
        "feeding_date": feeding_date,
        "date_error": bool(raw_date) and feeding_date is None,
        "today": date.today().isoformat(),
    }

    return render(
        request,
        "animals/available.html",
        context,
    )
