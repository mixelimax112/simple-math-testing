from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Создаем движок для подключения к SQLite базе данных
engine = create_engine('sqlite:///shop.db', echo=False)

Base = declarative_base()


# Определяем модель категории Category
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))

    # Связь с продуктами
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', description='{self.description}')>"


# Определяем модель продукта Product
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, nullable=False, default=True)

    # Связь с категорией
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, in_stock={self.in_stock})>"


# Создаем таблицы в базе данных
Base.metadata.create_all(engine)

# Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()


def task1_populate_database():
    """
    Задача 1: Наполнение данными
    Добавьте в базу данных следующие категории и продукты
    """
    print("\n" + "="*80)
    print("ЗАДАЧА 1: НАПОЛНЕНИЕ ДАННЫМИ")
    print("="*80)

    # Добавление категорий
    category1 = Category(name="Электроника", description="Гаджеты и устройства")
    category2 = Category(name="Книги", description="Печатные книги и электронные книги")
    category3 = Category(name="Одежда", description="Одежда для мужчин и женщин")

    session.add_all([category1, category2, category3])
    session.commit()

    print("✓ Добавлены категории: Электроника, Книги, Одежда")

    # Добавление продуктов
    products = [
        Product(name="Смартфон", price=299.99, in_stock=True, category=category1),
        Product(name="Ноутбук", price=499.99, in_stock=True, category=category1),
        Product(name="Научно-фантастический роман", price=15.99, in_stock=True, category=category2),
        Product(name="Джинсы", price=40.50, in_stock=True, category=category3),
        Product(name="Футболка", price=20.00, in_stock=True, category=category3),
    ]

    session.add_all(products)
    session.commit()

    print("✓ Добавлены продукты:")
    for p in products:
        print(f"  - {p.name} (Цена: {p.price}, Категория: {p.category.name})")


def task2_read_data():
    """
    Задача 2: Чтение данных
    Извлеките все записи из таблицы categories. Для каждой категории извлеките и выведите все связанные с ней продукты.
    """
    print("\n" + "="*80)
    print("ЗАДАЧА 2: ЧТЕНИЕ ДАННЫХ")
    print("="*80)

    categories = session.query(Category).all()

    for category in categories:
        print(f"\n📁 Категория: {category.name}")
        print(f"   Описание: {category.description}")
        print(f"   Продукты:")

        if category.products:
            for product in category.products:
                print(f"     • {product.name} - Цена: {product.price} руб.")
        else:
            print(f"     (нет продуктов)")


def task3_update_data():
    """
    Задача 3: Обновление данных
    Найдите в таблице products первый продукт с названием "Смартфон". Замените цену этого продукта на 349.99.
    """
    print("\n" + "="*80)
    print("ЗАДАЧА 3: ОБНОВЛЕНИЕ ДАННЫХ")
    print("="*80)

    # Находим продукт "Смартфон"
    smartphone = session.query(Product).filter_by(name="Смартфон").first()

    if smartphone:
        old_price = smartphone.price
        smartphone.price = 349.99
        session.commit()

        print(f"✓ Цена продукта '{smartphone.name}' обновлена:")
        print(f"  Старая цена: {old_price} руб.")
        print(f"  Новая цена: {smartphone.price} руб.")
    else:
        print("✗ Продукт 'Смартфон' не найден")


def task4_aggregation():
    """
    Задача 4: Агрегация и группировка
    Используя агрегирующие функции и группировку, подсчитайте общее количество продуктов в каждой категории.
    """
    print("\n" + "="*80)
    print("ЗАДАЧА 4: АГРЕГАЦИЯ И ГРУППИРОВКА")
    print("="*80)

    # Группировка и подсчёт количества продуктов в каждой категории
    results = session.query(
        Category.name,
        func.count(Product.id).label('product_count')
    ).join(Product).group_by(Category.name).all()

    print("\nКоличество продуктов в каждой категории:")
    for category_name, count in results:
        print(f"  📊 {category_name}: {count} продукт(ов)")


def task5_filtering():
    """
    Задача 5: Группировка с фильтрацией
    Отфильтруйте и выведите только те категории, в которых более одного продукта.
    """
    print("\n" + "="*80)
    print("ЗАДАЧА 5: ГРУППИРОВКА С ФИЛЬТРАЦИЕЙ")
    print("="*80)

    # Фильтруем категории с более чем одним продуктом
    results = session.query(
        Category.name,
        func.count(Product.id).label('product_count')
    ).join(Product).group_by(Category.name).having(func.count(Product.id) > 1).all()

    print("\nКатегории с более чем одним продуктом:")
    if results:
        for category_name, count in results:
            print(f"  ✓ {category_name}: {count} продукт(ов)")
    else:
        print("  (нет категорий с более чем одним продуктом)")


if __name__ == "__main__":
    print("="*80)
    print("ДОМАШНЕЕ ЗАДАНИЕ: РАБОТА С SQLALCHEMY")
    print("="*80)

    # Очистка базы данных для повторного запуска
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Выполнение всех задач
    task1_populate_database()
    task2_read_data()
    task3_update_data()
    task4_aggregation()
    task5_filtering()

    # Закрываем сессию
    session.close()

    print("\n" + "="*80)
    print("ВСЕ ЗАДАЧИ ВЫПОЛНЕНЫ!")
    print("="*80)
