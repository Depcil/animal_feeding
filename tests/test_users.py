from models import User
from models.users import add_user, find_user, find_user_by_id


def test_user_creation_and_str():
    user = User(1, "Анна Смирнова", "anna@example.com")
    assert user.id == 1
    assert user.name == "Анна Смирнова"
    assert str(user) == "Анна Смирнова <anna@example.com>"


def test_from_data():
    user = User.from_data({"id": 2, "name": "Иван", "email": "i@e.com"})
    assert isinstance(user, User)
    assert user.email == "i@e.com"


def test_add_find_user():
    users = []
    add_user(users, "Анна", "anna@example.com")
    add_user(users, "Иван", "ivan@example.com")
    assert len(find_user(users, "ИВАН")) == 1
    assert find_user_by_id(users, 2).name == "Иван"
    assert find_user_by_id(users, 5) is None
