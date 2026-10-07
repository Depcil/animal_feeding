"""Класс User (сотрудник) и функции работы с пользователями."""
from typing import List, Optional


class User:
    """Пользователь системы – сотрудник, который кормит животных."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        """Создать объект пользователя."""
        self.id = user_id
        self.name = name
        self.email = email

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из набора данных JSON."""
        return cls(data["id"], data["name"], data["email"])

    def __str__(self) -> str:
        """Строковое представление пользователя."""
        return f"{self.name} <{self.email}>"


def add_user(users: List[User], name: str, email: str) -> None:
    """Создать объект User и добавить его в коллекцию."""
    user_id = max((u.id for u in users), default=0) + 1
    users.append(User(user_id, name, email))


def find_user(users: List[User], query: str) -> List[User]:
    """Найти пользователей по имени или адресу электронной почты."""
    query = query.lower()
    return [
        u for u in users
        if query in u.name.lower() or query in u.email.lower()
    ]


def find_user_by_id(users: List[User], user_id: int) -> Optional[User]:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def show_users(users: List[User]) -> None:
    """Вывести информацию об объектах User."""
    if not users:
        print("Пользователи не найдены.")
    for user in users:
        print(f"{user.id}. {user}")
