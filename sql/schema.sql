-- ==========================================
-- PetFeed: структура базы данных (ПР7)
-- ==========================================
-- Сущности предметной области:
--   animals  – животные с суточной нормой корма;
--   users    – сотрудники, которые кормят животных;
--   feedings – кормления (связывают животное и сотрудника).
-- Связи: одно животное – много кормлений, один сотрудник – много кормлений.

CREATE TABLE IF NOT EXISTS animals (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    daily_norm INTEGER NOT NULL CHECK (daily_norm > 0)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS feedings (
    id INTEGER PRIMARY KEY,
    animal_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    feeding_date TEXT NOT NULL,              -- дата в формате YYYY-MM-DD
    food TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),  -- порция, г
    is_cancelled INTEGER NOT NULL DEFAULT 0
        CHECK (is_cancelled IN (0, 1)),      -- 0 – активно, 1 – отменено
    comment TEXT,                            -- необязательное поле (NULL)
    FOREIGN KEY (animal_id) REFERENCES animals(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
