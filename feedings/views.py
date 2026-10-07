from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.feedings import find_feeding_by_id
from storage import load_animals, load_feedings, load_users


def _load():
    animals_list = load_animals("data/animals.json")
    users_list = load_users("data/users.json")
    return load_feedings("data/feedings.json", animals_list, users_list)


def feedings(request):
    items = ""
    for feeding in _load():
        status = "отменено" if feeding.is_cancelled else "активно"
        badge = "bg-secondary" if feeding.is_cancelled else "bg-success"
        title = escape(f"{feeding.animal.name} – {feeding.feeding_date}")
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/feedings/{feeding.id}/">{title}</a>
            <span class="badge {badge}">{status}</span>
        </li>
        """
    content = f"""
    <h1>Кормления</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("PetFeed – кормления", content))


def feeding_detail(request, feeding_id):
    feeding = find_feeding_by_id(_load(), feeding_id)
    if feeding is None:
        content = """
        <h1 class="text-danger">Кормление не найдено</h1>
        <a href="/feedings/" class="btn btn-outline-secondary">
            ← к списку кормлений
        </a>
        """
        return HttpResponse(
            page("Кормление не найдено", content),
            status=404,
        )
    status = "отменено" if feeding.is_cancelled else "активно"
    badge = "bg-secondary" if feeding.is_cancelled else "bg-success"
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Кормление №{feeding.id}</h5>
            <p class="card-text">
                Животное: {escape(feeding.animal.name)}
            </p>
            <p class="card-text">Дата: {feeding.feeding_date}</p>
            <p class="card-text">
                Корм: {escape(feeding.food)}, {feeding.amount} г
            </p>
            <p class="card-text">
                Сотрудник: {escape(feeding.user.name)}
            </p>
            <p class="card-text">
                Статус: <span class="badge {badge}">{status}</span>
            </p>
            <a href="/feedings/" class="btn btn-outline-secondary">
                ← к списку кормлений
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Кормление №{feeding.id}", content))
