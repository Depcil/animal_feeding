from datetime import date

from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.animals import find_animal_by_id
from models.feedings import get_fed_amount, get_remaining_norm
from storage import load_animals, load_feedings, load_users


def animals(request):
    items = ""
    for animal in load_animals("data/animals.json"):
        text = escape(
            f"{animal.name} ({animal.species}) – "
            f"суточная норма {animal.daily_norm} г"
        )
        items += (
            '<li class="list-group-item">'
            f'<a href="/animals/{animal.id}/">{text}</a></li>'
        )
    content = f"""
    <h1>Животные</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("PetFeed – животные", content))


def animal_detail(request, animal_id):
    animals_list = load_animals("data/animals.json")
    animal = find_animal_by_id(animals_list, animal_id)
    if animal is None:
        content = """
        <h1 class="text-danger">Животное не найдено</h1>
        <a href="/animals/" class="btn btn-outline-secondary">
            ← к списку животных
        </a>
        """
        return HttpResponse(
            page("Животное не найдено", content),
            status=404,
        )
    users_list = load_users("data/users.json")
    feedings_list = load_feedings(
        "data/feedings.json",
        animals_list,
        users_list,
    )
    today = date.today().isoformat()
    fed = get_fed_amount(feedings_list, animal, today)
    remaining = get_remaining_norm(feedings_list, animal, today)
    status = "можно кормить" if remaining > 0 else "норма выполнена"
    badge = "bg-success" if remaining > 0 else "bg-danger"
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(animal.name)}</h5>
            <p class="card-text">
                <strong>ID:</strong> {animal.id}
            </p>
            <p class="card-text">
                <strong>Вид:</strong> {escape(animal.species)}
            </p>
            <p class="card-text">
                <strong>Суточная норма:</strong> {animal.daily_norm} г
            </p>
            <p class="card-text">
                <strong>Сегодня получил:</strong> {fed} г,
                остаток нормы: {remaining} г
            </p>
            <p class="card-text">
                Кормление на текущую дату:
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="/animals/" class="btn btn-outline-secondary">
                ← к списку животных
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(animal.name, content), status=200)
