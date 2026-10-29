# PetFeed – сервис учета кормления животных
Система учета кормления животных на Python с веб-интерфейсом на Django.

## 1. Назначение проекта
PetFeed – учебное приложение для учета животных и их кормления в приюте,
питомнике или зоопарке. Оно показывает суточную норму корма каждого
животного, историю кормлений и остаток нормы на сегодня. Консольная версия
(ПР1–ПР3) дополнена веб-интерфейсом на Django (ПР5–ПР6), а в ПР7 данные
перенесены в базу SQLite и обрабатываются SQL-запросами.

Правило предметной области: сумма активных кормлений животного за дату не
может превышать его суточную норму; отмененное кормление норму не занимает.

## 2. Используемые технологии
- Python 3;
- Django 5.2, Django Template Language (DTL);
- HTML5, CSS3, JavaScript;
- Bootstrap 5.3 (CDN);
- SQLite и модуль `sqlite3` стандартной библиотеки (ПР7);
- JSON – исходные данные и хранилище консольной версии;
- Git, pytest, flake8.

## 3. Предметная область
- Животное (Animal) – id, кличка, вид, суточная норма корма (г);
- Сотрудник (User) – id, имя, email;
- Кормление (Feeding) – id, животное, сотрудник, дата, корм, порция (г),
  признак отмены.

Для сущностей реализованы собственные Python-классы (пакет `models/`).
Веб-версия читает данные из SQLite (`data/petfeed.sqlite`), консольная
версия по-прежнему работает с JSON. Django ORM пока не используется.

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
├── db/
│   ├── __init__.py
│   ├── database.py      подключение, PRAGMA foreign_keys = ON
│   └── import_json.py   перенос JSON -> SQLite
├── sql/
│   ├── schema.sql       CREATE TABLE
│   └── queries.sql      18 проверенных запросов
├── data/          animals.json, users.json, feedings.json, petfeed.sqlite
├── tests/         тесты классов, хранилища и веб-страниц
├── petfeed/       settings.py, urls.py
├── main.py  storage.py  utils.py  manage.py
└── README.md
```

## 5. Веб-интерфейс
Страницы: главная; список животных с поиском; карточка животного (остаток
нормы на выбранную дату); «Кого можно покормить» на дату; журнал
кормлений с фильтром и постраничным выводом; страница кормления;
статистика. Все данные страниц приходят из SQLite.
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
`homepage:index`, `animals:list`, `animals:detail`, `animals:available`,
`feedings:list`, `feedings:detail`, `feedings:statistics`.
Ссылки строятся через `{% url %}`. Меню: Главная | Животные | Кормления |
Статистика; «Кого можно покормить» – ссылка в разделе «Животные».

## 9. Статические файлы
`homepage/static/homepage/`: `css/style.css`, `js/main.js`
(текущий год в подвале), `img/logo.png`. Подключаются через
`{% load static %}` и `{% static %}`.

## 10. Хранение данных
JSON-файлы `data/animals.json`, `data/users.json`, `data/feedings.json`
остаются исходными данными и хранилищем консольной версии (`storage.py`).
Веб-версия работает с базой `data/petfeed.sqlite` (раздел 11).

## 11. База данных SQLite (ПР7)
### Таблицы
| Таблица | Поле | Тип | Ограничения |
|---|---|---|---|
| animals | id | INTEGER | PRIMARY KEY |
| | name | TEXT | NOT NULL |
| | species | TEXT | NOT NULL |
| | daily_norm | INTEGER | NOT NULL, CHECK > 0 |
| users | id | INTEGER | PRIMARY KEY |
| | name | TEXT | NOT NULL |
| | email | TEXT | NOT NULL, UNIQUE |
| feedings | id | INTEGER | PRIMARY KEY |
| | animal_id | INTEGER | NOT NULL, FOREIGN KEY → animals(id) |
| | user_id | INTEGER | NOT NULL, FOREIGN KEY → users(id) |
| | feeding_date | TEXT | NOT NULL, формат YYYY-MM-DD |
| | food | TEXT | NOT NULL |
| | amount | INTEGER | NOT NULL, CHECK > 0 |
| | is_cancelled | INTEGER | NOT NULL DEFAULT 0, 0/1 |
| | comment | TEXT | допускает NULL |

Связи: одно животное – много кормлений, один сотрудник – много кормлений.

### Создание и заполнение базы
```bash
python -c "import sqlite3; sqlite3.connect('data/petfeed.sqlite').close()"
python -c "import sqlite3; c=sqlite3.connect('data/petfeed.sqlite'); c.executescript(open('sql/schema.sql', encoding='utf-8').read()); c.close()"
python -m db.import_json
```
`db/import_json.py` сам выполняет схему (`CREATE TABLE IF NOT EXISTS`),
очищает таблицы и вставляет записи через `executemany()` с параметрами `?`
в порядке animals → users → feedings. При ошибке – `rollback()`, при
успехе – `commit()`. Скрипт можно запускать повторно.

### SQL-запросы (`sql/queries.sql`)
Проверка в CLI: `sqlite3 data/petfeed.sqlite ".read sql/queries.sql"`.
- списки: Q1 животные, Q2 сотрудники;
- WHERE: Q3 норма от N г, Q4 поиск LIKE, Q5 активные кормления,
  Q6 комментарий IS NOT NULL;
- JOIN: Q7 журнал кормлений, Q8 одно кормление, Q9 кормления животного
  за дату, Q10 последние кормления (LIMIT/OFFSET);
- агрегатные функции: Q11 COUNT/SUM сводка, Q12 MIN/MAX/AVG норм;
- GROUP BY: Q13 остаток нормы на дату (+ HAVING), Q14 по животным,
  Q15 по сотрудникам, Q16 по видам, Q17 кормили не менее N раз (HAVING),
  Q18 расход корма по датам.

### Данные в Django
Представления открывают соединение через `db.database.get_connection()`,
задают `conn.row_factory = sqlite3.Row` и передают строки в шаблоны через
context; в шаблонах поля читаются по именам (`{{ animal.name }}`).
Значения пользователя (поиск, норма, дата, статус, страница, порог)
передаются только параметрами `?`, текст SQL не собирается из строк.

| Страница | Запросы |
|---|---|
| `/` | COUNT животных и активных кормлений |
| `/animals/?q=&min_norm=` | Q1/Q3/Q4 в одном параметризованном запросе |
| `/animals/<id>/?date=` | животное, SUM за дату, Q9 |
| `/animals/available/?date=` | Q13 |
| `/feedings/?status=&page=` | Q7 + COUNT, LIMIT/OFFSET |
| `/feedings/<id>/` | Q8 |
| `/feedings/statistics/?min_count=` | Q11, Q12, Q14–Q18 |

Путь к базе можно переопределить переменной окружения `PETFEED_DB`
(тесты используют временную базу, собранную из JSON).
Ограничение SQLite: `LIKE` без учета регистра работает только для латиницы,
поиск по кириллице чувствителен к регистру.

## 12. Тестирование
`pytest -v` – 39 тестов: классы, правило суточной нормы, хранилище JSON,
веб-страницы, а также база: таблицы и внешние ключи, совпадение числа
записей с JSON, проверка FOREIGN KEY, выполнение всех запросов
`queries.sql`, поиск, защита от SQL-инъекции, страницы ПР7.

## 13. Проверка качества кода
`flake8 . --extend-exclude=venv`

## 14. Запуск проекта
Веб-версия: `python manage.py runserver` (база `data/petfeed.sqlite`
уже в репозитории; пересоздать – `python -m db.import_json`), адрес http://127.0.0.1:8000/
Консольная версия (сохранена): `python main.py`

## 15. Git
`git commit -m "PR7: add SQLite database and SQL queries"`

## 16. Текущий этап разработки
На ПР7 данные PetFeed перенесены из JSON в базу данных SQLite:
- создана база `data/petfeed.sqlite`;
- таблицы созданы с помощью `sql/schema.sql`;
- данные перенесены из JSON скриптом `db/import_json.py`;
- SQL-запросы сохранены в `sql/queries.sql`;
- Django-представления получают данные из SQLite;
- страницы животных, кормлений, «Кого можно покормить» и статистики
  работают с базой данных.

На следующих практических работах база будет подключена к Django через
Django ORM.

## 17. Текущее состояние проекта
Реализованы: классы Animal, User, Feeding; консольный интерфейс; JSON;
Django-проект; шаблоны, наследование, include, блоки; циклы и условия;
фильтры; именованные URL; статика, собственные CSS и JavaScript; база
SQLite, SQL-запросы и их вывод на страницах; тесты.
Формы создания записей и Django ORM пока не реализованы.

## 18. Дальнейшее развитие
Переход на Django ORM и модели, формы создания кормлений,
пользователи и авторизация, API, Docker, CI/CD.
