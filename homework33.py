import time
from functools import wraps


def measure_time(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        times = []
        result = None
        for _ in range(5):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            times.append(end - start)

        avg_time = sum(times) / len(times)
        print(f"Среднее время выполнения для 5 вызовов: {avg_time:.2f} секунд")
        print(f"Результат: {result}")
        return result

    return wrapper


def measure_time_with_repeats(repeats):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            times = []
            result = None
            for _ in range(repeats):
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                times.append(end - start)

            avg_time = sum(times) / len(times)
            print(f"Среднее время выполнения для {repeats} вызовов: {avg_time:.2f} секунд")
            print(f"Результат: {result}")
            return result

        return wrapper
    return decorator



@measure_time
def compute():
    total = 0
    for i in range(10_000_000):
        total += i
    return total



@measure_time_with_repeats(10)
def calculate():
    total = 0
    for i in range(10_000_000):
        total += i
    return total


if __name__ == "__main__":
    print("=" * 50)
    print("Пример 1: Декоратор measure_time (5 вызовов)")
    print("=" * 50)
    compute()

    print("\n" + "=" * 50)
    print("Пример 2: Декоратор с параметром repeats=10")
    print("=" * 50)
    calculate()
