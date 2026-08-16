class Rectangle:


    def __init__(self, width, height):
        """
        Инициализация прямоугольника

        Args:
            width: ширина прямоугольника
            height: высота прямоугольника
        """
        self.width = width
        self.height = height

    def get_area(self):
        return self.width * self.height

    def __str__(self):
        return f"Rectangle(width={self.width}, height={self.height})"


if __name__ == "__main__":
    rect = Rectangle(width=20, height=35)
    print("Python")
    print(f"Площадь: {rect.get_area()}")
    print(f"Новая площадь: {rect.get_area()}")
