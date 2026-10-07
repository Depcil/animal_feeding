from models import Animal, User
from models.feedings import create_feeding
from storage import (
    load_animals,
    load_feedings,
    load_users,
    save_animals,
    save_feedings,
    save_users,
)


def test_roundtrip_with_links(tmp_path):
    animals = [Animal(1, "Барсик", "кот", 200)]
    users = [User(1, "Анна", "anna@example.com")]
    feedings = []
    create_feeding(feedings, animals[0], users[0], "2026-10-07", "корм", 90)
    feedings[0].cancel()
    a, u, f = (tmp_path / n for n in ("a.json", "u.json", "f.json"))
    save_animals(str(a), animals)
    save_users(str(u), users)
    save_feedings(str(f), feedings)
    loaded_a = load_animals(str(a))
    loaded_u = load_users(str(u))
    loaded_f = load_feedings(str(f), loaded_a, loaded_u)
    assert loaded_f[0].animal is loaded_a[0]
    assert loaded_f[0].user is loaded_u[0]
    assert loaded_f[0].is_cancelled


def test_missing_and_broken_file(tmp_path):
    assert load_animals(str(tmp_path / "none.json")) == []
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert load_users(str(broken)) == []
