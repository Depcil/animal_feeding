# PetFeed – сервис учета кормления животных
Система учета кормления животных на Python с веб-интерфейсом на Django.

## 1. Назначение проекта
PetFeed – учебное приложение для учета животных и их кормления в приюте,
питомнике или зоопарке. Оно показывает суточную норму корма каждого
животного, историю кормлений и остаток нормы на сегодня. Консольная версия
(ПР1–ПР3) дополнена веб-интерфейсом на Django (ПР5–ПР6).

Правило предметной области: сумма активных кормлений животного за дату не
может превышать его суточную норму; отмененное кормление норму не занимает.

## 2. Используемые технологии
- Python 3;
- Django 5.2, Django Template Language (DTL);
- HTML5, CSS3, JavaScript;
- Bootstrap 5.3 (CDN);
- JSON для хранения данных;
- Git, pytest, flake8.

## 3. Предметная область
- Животное (Animal) – id, кличка, вид, суточная норма корма (г);
- Сотрудник (User) – id, имя, email;
- Кормление (Feeding) – id, животное, сотрудник, дата, корм, порция (г),
  признак отмены.

Для сущностей реализованы собственные Python-классы (пакет `models/`).
Данные хранятся в JSON; Django ORM и база данных пока не используются.

## 4. Структура проекта
```text
animal_feeding/
├── animals/
│   ├── templates/animals/
│   │   ├── includes/animal_card.html
│   │   ├── animal_detail.html
│   │   └── animal_list.html
│   ├── urls.py
│   └── views.py
├── feedings/
│   ├── templates/feedings/
│   │   ├── includes/feeding_status.html
│   │   ├── feeding_detail.html
│   │   └── feeding_list.html
│   ├── urls.py
│   └── views.py
├── homepage/
│   ├── static/homepage/
│   │   ├── css/style.css
│   │   ├── img/logo.png
│   │   └── js/main.js
│   ├── templates/homepage/index.html
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── includes/navigation.html
│   ├── 404.html
│   └── base.html
├── models/        animals.py, users.py, feedings.py
├── data/          animals.json, users.json, feedings.json
├── tests/         тесты классов, хранилища и веб-страниц
├── petfeed/       settings.py, urls.py
├── main.py  storage.py  utils.py  manage.py
└── README.md
```

## 5. Веб-интерфейс
Страницы: главная; список животных; карточка животного (остаток нормы на
сегодня); список кормлений; страница кормления.
HTML в Python-коде не формируется: функция `page()` удалена. View-функции
готовят данные и передают их в шаблоны через контекст `render()`.
Если объект не найден, страница отображает сообщение и отдает код 404.

## 6. Django Template Language
- базовый шаблон `templates/base.html` (блоки `title` и `content`);
- наследование: `{% extends "base.html" %}`;
- включаемые шаблоны: `animals/includes/animal_card.html`,
  `feedings/includes/feeding_status.html`,
  `includes/navigation.html`;
- контекст: например `{"animals": animals_list}`;
- циклы `{% for %}` с `{% empty %}`, условия `{% if %}`;
- шаблон 404: `templates/404.html` (`handler404`).

## 7. Фильтры шаблонов
- `{{ animals|length }}` – количество животных и записей;
- `{{ animal.name|default:"Без клички" }}` – значение по умолчанию.
Фильтры только форматируют вывод и не содержат бизнес-логики. Дата
кормления хранится строкой и выводится без преобразования.

## 8. URL-маршрутизация
Именованные маршруты с пространствами имен:
`homepage:index`, `animals:list`, `animals:detail`, `feedings:list`,
`feedings:detail`. Ссылки строятся через `{% url %}`.

## 9. Статические файлы
`homepage/static/homepage/`: `css/style.css`, `js/main.js`
(текущий год в подвале), `img/logo.png`. Подключаются через
`{% load static %}` и `{% static %}`.

## 10. Хранение данных
JSON-файлы `data/animals.json`, `data/users.json`, `data/feedings.json`.
Загрузку выполняет `storage.py`: в `feedings.json` лежат `animal_id` и
`user_id`, при загрузке восстанавливаются ссылки на объекты.

## 11. Тестирование
`pytest -v` – тесты классов, правила суточной нормы, хранилища и
веб-страниц (шаблоны, include, фильтры, 404, статика).

## 12. Проверка качества кода
`flake8 . --extend-exclude=venv`

## 13. Запуск проекта
Веб-версия: `python manage.py runserver`, адрес http://127.0.0.1:8000/
Консольная версия (сохранена): `python main.py`

## 14. Git
`git commit -m "PR6: add Django templates and static files"`

## 15. Текущее состояние проекта
Реализованы: классы Animal, User, Feeding; консольный интерфейс; JSON;
Django-проект; шаблоны, наследование, include, блоки; циклы и условия;
фильтры; именованные URL; статика, собственные CSS и JavaScript; тесты.
Формы, Django ORM и база данных пока не реализованы.

## 16. Дальнейшее развитие
Переход от JSON к базе данных и Django ORM, формы создания кормлений,
пользователи и авторизация, API, Docker, CI/CD.
