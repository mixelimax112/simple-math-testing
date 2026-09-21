from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
import json


class Address(BaseModel):
    """Модель адреса пользователя"""
    city: str = Field(..., min_length=2, description="Город, минимум 2 символа")
    street: str = Field(..., min_length=3, description="Улица, минимум 3 символа")
    house_number: int = Field(..., gt=0, description="Номер дома, должен быть положительным")


class User(BaseModel):
    """Модель пользователя"""
    name: str = Field(..., min_length=2, description="Имя, только буквы, минимум 2 символа")
    age: int = Field(..., ge=0, le=120, description="Возраст от 0 до 120")
    email: EmailStr = Field(..., description="Email в правильном формате")
    is_employed: bool = Field(..., description="Статус занятости")
    address: Address = Field(..., description="Вложенная модель адреса")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Проверка, что имя содержит только буквы"""
        if not v.replace(' ', '').isalpha():
            raise ValueError('Имя должно содержать только буквы')
        return v

    @field_validator('age')
    @classmethod
    def validate_employment_age(cls, v: int, info) -> int:
        """Проверка возраста работающего пользователя"""
        # Проверяем is_employed через info.data
        if info.data.get('is_employed') and not (18 <= v <= 65):
            raise ValueError('Если пользователь работает (is_employed = true), возраст должен быть от 18 до 65 лет')
        return v


def validate_user_registration(json_string: str) -> dict:
    """
    Функция валидации JSON строки пользователя

    Args:
        json_string: JSON строка с данными пользователя

    Returns:
        dict: Словарь с результатом валидации
    """
    try:
        # Десериализуем JSON
        data = json.loads(json_string)

        # Валидируем данные через Pydantic
        user = User(**data)

        # Сериализуем объект обратно в JSON
        validated_json = user.model_dump_json(indent=2)

        return {
            'success': True,
            'message': 'Регистрация успешна!',
            'data': json.loads(validated_json)
        }

    except json.JSONDecodeError as e:
        return {
            'success': False,
            'message': f'Ошибка парсинга JSON: {str(e)}',
            'data': None
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Ошибка валидации: {str(e)}',
            'data': None
        }


def add_custom_validator(validator_func):
    """Декоратор для добавления кастомных валидаторов"""
    def wrapper(json_string: str) -> dict:
        result = validate_user_registration(json_string)
        if result['success']:
            try:
                validator_func(result['data'])
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Кастомная валидация не пройдена: {str(e)}',
                    'data': None
                }
        return result
    return wrapper


# Пример JSON данных для регистрации пользователя (правильный)
json_input_valid = """{
    "name": "John Doe",
    "age": 70,
    "email": "john.doe@example.com",
    "is_employed": true,
    "address": {
        "city": "New York",
        "street": "5th Avenue",
        "house_number": 123
    }
}"""

# Пример JSON с ошибкой (is_employed = true, но возраст 70)
json_input_invalid_age = """{
    "name": "John Doe",
    "age": 70,
    "email": "john.doe@example.com",
    "is_employed": true,
    "address": {
        "city": "New York",
        "street": "5th Avenue",
        "house_number": 123
    }
}"""

# Пример JSON с ошибкой (возраст не соответствует статусу)
json_input_invalid_employment = """{
    "name": "Jane Smith",
    "age": 16,
    "email": "jane@example.com",
    "is_employed": true,
    "address": {
        "city": "LA",
        "street": "Main Street",
        "house_number": 456
    }
}"""

# Пример JSON с ошибкой формата email
json_input_invalid_email = """{
    "name": "Bob",
    "age": 25,
    "email": "not-an-email",
    "is_employed": false,
    "address": {
        "city": "Chicago",
        "street": "Oak Street",
        "house_number": 789
    }
}"""


if __name__ == "__main__":
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 80)

    # Тест 1: Успешная регистрация (is_employed = false)
    print("\n1. Тест успешной регистрации (is_employed = false, age = 70):")
    json_valid_unemployed = """{
        "name": "John Doe",
        "age": 70,
        "email": "john.doe@example.com",
        "is_employed": false,
        "address": {
            "city": "New York",
            "street": "5th Avenue",
            "house_number": 123
        }
    }"""
    result = validate_user_registration(json_valid_unemployed)
    print(f"Статус: {'✓ УСПЕХ' if result['success'] else '✗ ОШИБКА'}")
    print(f"Сообщение: {result['message']}")
    if result['data']:
        print(f"Данные: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")

    # Тест 2: Ошибка валидации возраста для работающего
    print("\n2. Тест валидации возраста (is_employed = true, age = 70):")
    result = validate_user_registration(json_input_invalid_age)
    print(f"Статус: {'✓ УСПЕХ' if result['success'] else '✗ ОШИБКА'}")
    print(f"Сообщение: {result['message']}")

    # Тест 3: Ошибка валидации возраста для работающего (младше 18)
    print("\n3. Тест валидации возраста (is_employed = true, age = 16):")
    result = validate_user_registration(json_input_invalid_employment)
    print(f"Статус: {'✓ УСПЕХ' if result['success'] else '✗ ОШИБКА'}")
    print(f"Сообщение: {result['message']}")

    # Тест 4: Ошибка формата email
    print("\n4. Тест валидации email:")
    result = validate_user_registration(json_input_invalid_email)
    print(f"Статус: {'✓ УСПЕХ' if result['success'] else '✗ ОШИБКА'}")
    print(f"Сообщение: {result['message']}")

    # Тест 5: Успешная регистрация работающего
    print("\n5. Тест успешной регистрации (is_employed = true, age = 30):")
    json_valid_employed = """{
        "name": "Alice Johnson",
        "age": 30,
        "email": "alice@example.com",
        "is_employed": true,
        "address": {
            "city": "Boston",
            "street": "Park Avenue",
            "house_number": 999
        }
    }"""
    result = validate_user_registration(json_valid_employed)
    print(f"Статус: {'✓ УСПЕХ' if result['success'] else '✗ ОШИБКА'}")
    print(f"Сообщение: {result['message']}")
    if result['data']:
        print(f"Данные: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")

    print("\n" + "=" * 80)
