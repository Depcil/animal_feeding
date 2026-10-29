-- ==========================================
-- PetFeed: SQL-запросы проекта (ПР7)
-- ==========================================
-- Проверка: sqlite3 data/petfeed.sqlite, затем .read sql/queries.sql
-- Значения в условиях (даты, пороги, строки поиска) приведены для проверки
-- в SQLite CLI. В Django-представлениях вместо них стоят параметры ?.

.headers on
.mode column

-- ------------------------------------------
-- Выборка списков
-- ------------------------------------------

-- Q1. Список всех животных по кличке (страница «Животные»)
SELECT
    id,
    name,
    species,
    daily_norm
FROM animals
ORDER BY name;

-- Q2. Список сотрудников по имени
SELECT
    id,
    name,
    email
FROM users
ORDER BY name;

-- ------------------------------------------
-- Фильтрация WHERE
-- ------------------------------------------

-- Q3. Животные с суточной нормой не меньше заданной (поиск по норме)
SELECT
    id,
    name,
    species,
    daily_norm
FROM animals
WHERE daily_norm >= 200
ORDER BY daily_norm;

-- Q4. Поиск животного по кличке или виду (LIKE, без учета позиции)
SELECT
    id,
    name,
    species,
    daily_norm
FROM animals
WHERE name LIKE '%ко%'
   OR species LIKE '%ко%'
ORDER BY name;

-- Q5. Активные кормления (отмененные норму не занимают)
SELECT
    id,
    animal_id,
    user_id,
    feeding_date,
    amount
FROM feedings
WHERE is_cancelled = 0
ORDER BY feeding_date, id;

-- Q6. Кормления с комментарием (необязательное поле, IS NOT NULL)
SELECT
    id,
    feeding_date,
    comment
FROM feedings
WHERE comment IS NOT NULL
ORDER BY id;

-- ------------------------------------------
-- Соединение таблиц JOIN
-- ------------------------------------------

-- Q7. Журнал кормлений: кличка животного и имя сотрудника вместо id
--     (страница «Кормления»)
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
ORDER BY feedings.feeding_date DESC, feedings.id DESC;

-- Q8. Полная информация об одном кормлении (страница кормления)
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
WHERE feedings.id = 1;

-- Q9. Активные кормления животного за дату – несколько условий
--     (карточка животного)
SELECT
    feedings.id,
    feedings.food,
    feedings.amount,
    users.name AS user_name
FROM feedings
JOIN users
    ON feedings.user_id = users.id
WHERE feedings.animal_id = 1
  AND feedings.feeding_date = '2026-10-07'
  AND feedings.is_cancelled = 0
ORDER BY feedings.id;

-- Q10. Последние кормления постранично (ORDER BY + LIMIT/OFFSET)
SELECT
    feedings.id,
    feedings.feeding_date,
    animals.name AS animal_name,
    feedings.amount
FROM feedings
JOIN animals
    ON feedings.animal_id = animals.id
ORDER BY feedings.feeding_date DESC, feedings.id DESC
LIMIT 5 OFFSET 0;

-- ------------------------------------------
-- Агрегатные функции
-- ------------------------------------------

-- Q11. Сводка: всего кормлений, активных, отмененных и выдано корма, г
SELECT
    COUNT(*) AS total_count,
    SUM(CASE WHEN is_cancelled = 0 THEN 1 ELSE 0 END) AS active_count,
    SUM(is_cancelled) AS cancelled_count,
    COALESCE(SUM(CASE WHEN is_cancelled = 0 THEN amount END), 0)
        AS total_amount
FROM feedings;

-- Q12. Суточные нормы: минимум, максимум, среднее
SELECT
    COUNT(*) AS animals_count,
    MIN(daily_norm) AS min_norm,
    MAX(daily_norm) AS max_norm,
    ROUND(AVG(daily_norm), 1) AS avg_norm
FROM animals;

-- ------------------------------------------
-- Группировка GROUP BY и фильтрация групп HAVING
-- ------------------------------------------

-- Q13. Остаток нормы каждого животного на дату. HAVING оставляет тех,
--      кого еще можно кормить (страница «Кого можно покормить»)
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
   AND feedings.feeding_date = '2026-10-07'
   AND feedings.is_cancelled = 0
GROUP BY animals.id, animals.name, animals.species, animals.daily_norm
HAVING remaining > 0
ORDER BY animals.name;

-- Q14. Статистика по животным: число активных кормлений и корм, г
--      (LEFT JOIN – животные без кормлений тоже попадают в отчет)
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

-- Q15. Статистика по сотрудникам: сколько кормлений провел каждый
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

-- Q16. Количество животных по видам
SELECT
    species,
    COUNT(*) AS animals_count
FROM animals
GROUP BY species
ORDER BY animals_count DESC, species;

-- Q17. Животные, которых кормили не менее 2 раз (HAVING по COUNT)
SELECT
    animals.name AS animal_name,
    COUNT(feedings.id) AS feedings_count
FROM animals
JOIN feedings
    ON animals.id = feedings.animal_id
WHERE feedings.is_cancelled = 0
GROUP BY animals.id, animals.name
HAVING COUNT(feedings.id) >= 2
ORDER BY feedings_count DESC, animals.name;

-- Q18. Расход корма по датам (группировка по дню)
SELECT
    feeding_date,
    COUNT(*) AS feedings_count,
    SUM(amount) AS total_amount
FROM feedings
WHERE is_cancelled = 0
GROUP BY feeding_date
ORDER BY feeding_date;
