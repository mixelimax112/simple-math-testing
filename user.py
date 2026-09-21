class User:
    """Класс для представления пользователя"""

    total_users = 0  # Счётчик общего количества пользователей

    def __init__(self, username, password):
        """
        Инициализация пользователя

        Args:
            username: логин пользователя
            password: пароль пользователя

        Raises:
            ValueError: если данные некорректны
        """
        # Валидация имени пользователя
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")

        # Валидация пароля
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string")

        if len(password) < 5:
            raise ValueError(f"Invalid password: '{password}'")

        self.username = username
        self.password = password

        # Увеличиваем счётчик пользователей
        User.total_users += 1

    @classmethod
    def get_total(cls):
        """Возвращает общее количество созданных пользователей"""
        return cls.total_users

    def __str__(self):
        """Строковое представление пользователя"""
        return f"User: {self.username}"


# Пример использования - Задание 1: Счётчик
if __name__ == "__main__":
    print("Python")
    print(f"Total users: {User.get_total()}")

    # Задание 2: Проверка данных
    print("\nPython")
    user1 = User('alice', 'secret')
    user2 = User('bob', 'qwe')

    print("\nPython")
    print(user1)
    print("...")

    try:
        user3 = User('charlie', 'qwe')
    except ValueError as e:
        print(f"ValueError: {e}")
