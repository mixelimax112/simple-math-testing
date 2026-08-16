class Counter:
    """Класс для представления простого счётчика"""

    def __init__(self):
        """Инициализация счётчика с нуля"""
        self.value = 0

    def increment(self):
        """Увеличивает значение счётчика на единицу"""
        self.value += 1
        print(f"Значение увеличено, текущее: {self.value}")

    def decrement(self):
        """Уменьшает значение счётчика на единицу"""
        self.value -= 1
        print(f"Значение уменьшено, текущее: {self.value}")

    def get_value(self):
        """Возвращает текущее значение счётчика"""
        return self.value


# Пример использования
if __name__ == "__main__":
    print("Python")
    counter = Counter()
    counter.increment()  # Значение увеличено, текущее: 1
    counter.increment()  # Значение увеличено, текущее: 2
    counter.increment()  # Значение увеличено, текущее: 3
    counter.decrement()  # Значение уменьшено, текущее: 2
    print(f"Текущее значение: {counter.get_value()}")
