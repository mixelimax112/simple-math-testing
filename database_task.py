from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Задача 1: Создаем движок для подключения к SQLite базе данных в памяти
engine = create_engine('sqlite:///products.db', echo=True)

Base = declarative_base()


# Задача 3: Определяем модель продукта Product
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


# Задача 4: Определяем связанную модель категории Category
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))

    # Связь с продуктами
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', description='{self.description}')>"


# Создаем таблицы в базе данных
Base.metadata.create_all(engine)

# Задача 2: Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()


def populate_database():
    """Заполняем базу данных тестовыми данными"""

    # Создаем категории
    category1 = Category(name="Электроника", description="Электронные устройства и гаджеты")
    category2 = Category(name="Одежда", description="Мужская и женская одежда")
    category3 = Category(name="Продукты", description="Продукты питания")

    session.add_all([category1, category2, category3])
    session.commit()

    # Создаем продукты
    product1 = Product(name="Ноутбук", price=45000.50, in_stock=True, category_id=category1.id)
    product2 = Product(name="Смартфон", price=25000.00, in_stock=True, category_id=category1.id)
    product3 = Product(name="Футболка", price=500.00, in_stock=False, category_id=category2.id)
    product4 = Product(name="Джинсы", price=2500.00, in_stock=True, category_id=category2.id)
    product5 = Product(name="Молоко", price=80.50, in_stock=True, category_id=category3.id)

    session.add_all([product1, product2, product3, product4, product5])
    session.commit()

    print("База данных успешно заполнена!")


def display_products():
    """Выводим все продукты"""
    print("\n" + "="*80)
    print("ВСЕ ПРОДУКТЫ В БАЗЕ ДАННЫХ")
    print("="*80)

    products = session.query(Product).all()
    for product in products:
        print(f"ID: {product.id}, Название: {product.name}, Цена: {product.price} руб., "
              f"В наличии: {'Да' if product.in_stock else 'Нет'}, "
              f"Категория: {product.category.name if product.category else 'Без категории'}")


def display_categories():
    """Выводим все категории"""
    print("\n" + "="*80)
    print("ВСЕ КАТЕГОРИИ В БАЗЕ ДАННЫХ")
    print("="*80)

    categories = session.query(Category).all()
    for category in categories:
        print(f"ID: {category.id}, Название: {category.name}, Описание: {category.description}")
        print(f"  Продуктов в категории: {len(category.products)}")


def display_products_by_category(category_name):
    """Выводим продукты конкретной категории"""
    print(f"\n" + "="*80)
    print(f"ПРОДУКТЫ В КАТЕГОРИИ '{category_name}'")
    print("="*80)

    category = session.query(Category).filter_by(name=category_name).first()
    if category:
        for product in category.products:
            print(f"  - {product.name} ({product.price} руб.) - {'В наличии' if product.in_stock else 'Нет в наличии'}")
    else:
        print(f"Категория '{category_name}' не найдена")


if __name__ == "__main__":
    # Заполняем базу данных
    populate_database()

    # Выводим все продукты
    display_products()

    # Выводим все категории
    display_categories()

    # Задача 5: Демонстрируем связь между таблицами Product и Category
    display_products_by_category("Электроника")
    display_products_by_category("Одежда")
    display_products_by_category("Продукты")

    # Закрываем сессию
    session.close()
    print("\n" + "="*80)
    print("Сессия закрыта. Все задачи выполнены!")
    print("="*80)
