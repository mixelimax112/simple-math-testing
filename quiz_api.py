from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Модель Category
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Связь с вопросами
    questions = db.relationship('Question', back_populates='category', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'questions_count': len(self.questions)
        }

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


# Модель Question
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с категорией
    category = db.relationship('Category', back_populates='questions')

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Question(id={self.id}, text='{self.text[:30]}...')>"


# === API ENDPOINTS ===

# Главная страница
@app.route('/')
def index():
    return jsonify({
        'message': 'Quiz API',
        'endpoints': {
            'categories': {
                'GET /api/categories': 'Получить все категории',
                'POST /api/categories': 'Создать новую категорию',
                'GET /api/categories/<id>': 'Получить категорию по ID',
                'PUT /api/categories/<id>': 'Обновить категорию',
                'DELETE /api/categories/<id>': 'Удалить категорию'
            },
            'questions': {
                'GET /api/questions': 'Получить все вопросы',
                'POST /api/questions': 'Создать новый вопрос',
                'GET /api/questions/<id>': 'Получить вопрос по ID',
                'PUT /api/questions/<id>': 'Обновить вопрос',
                'DELETE /api/questions/<id>': 'Удалить вопрос',
                'GET /api/categories/<id>/questions': 'Получить вопросы категории'
            }
        }
    })


# === КАТЕГОРИИ ===

# Получить все категории
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'success': True,
        'count': len(categories),
        'categories': [cat.to_dict() for cat in categories]
    })


# Получить категорию по ID
@app.route('/api/categories/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'success': False, 'message': 'Категория не найдена'}), 404

    return jsonify({
        'success': True,
        'category': category.to_dict()
    })


# Создать новую категорию
@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Поле "name" обязательно'}), 400

    # Проверка на существование категории с таким именем
    existing = Category.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'success': False, 'message': 'Категория с таким именем уже существует'}), 400

    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Категория создана',
        'category': category.to_dict()
    }), 201


# Обновить категорию
@app.route('/api/categories/<int:id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'success': False, 'message': 'Категория не найдена'}), 404

    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Поле "name" обязательно'}), 400

    # Проверка на уникальность имени
    existing = Category.query.filter_by(name=data['name']).first()
    if existing and existing.id != id:
        return jsonify({'success': False, 'message': 'Категория с таким именем уже существует'}), 400

    category.name = data['name']
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Категория обновлена',
        'category': category.to_dict()
    })


# Удалить категорию
@app.route('/api/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'success': False, 'message': 'Категория не найдена'}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Категория "{category.name}" удалена'
    })


# === ВОПРОСЫ ===

# Получить все вопросы
@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify({
        'success': True,
        'count': len(questions),
        'questions': [q.to_dict() for q in questions]
    })


# Получить вопрос по ID
@app.route('/api/questions/<int:id>', methods=['GET'])
def get_question(id):
    question = Question.query.get(id)
    if not question:
        return jsonify({'success': False, 'message': 'Вопрос не найден'}), 404

    return jsonify({
        'success': True,
        'question': question.to_dict()
    })


# Получить вопросы категории
@app.route('/api/categories/<int:id>/questions', methods=['GET'])
def get_category_questions(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'success': False, 'message': 'Категория не найдена'}), 404

    return jsonify({
        'success': True,
        'category': category.name,
        'count': len(category.questions),
        'questions': [q.to_dict() for q in category.questions]
    })


# Создать новый вопрос
@app.route('/api/questions', methods=['POST'])
def create_question():
    data = request.get_json()

    if not data or 'text' not in data or 'category_id' not in data:
        return jsonify({'success': False, 'message': 'Поля "text" и "category_id" обязательны'}), 400

    # Проверка существования категории
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'success': False, 'message': 'Категория не найдена'}), 404

    question = Question(text=data['text'], category_id=data['category_id'])
    db.session.add(question)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Вопрос создан',
        'question': question.to_dict()
    }), 201


# Обновить вопрос
@app.route('/api/questions/<int:id>', methods=['PUT'])
def update_question(id):
    question = Question.query.get(id)
    if not question:
        return jsonify({'success': False, 'message': 'Вопрос не найден'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Нет данных для обновления'}), 400

    if 'text' in data:
        question.text = data['text']

    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'success': False, 'message': 'Категория не найдена'}), 404
        question.category_id = data['category_id']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Вопрос обновлен',
        'question': question.to_dict()
    })


# Удалить вопрос
@app.route('/api/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    question = Question.query.get(id)
    if not question:
        return jsonify({'success': False, 'message': 'Вопрос не найден'}), 404

    db.session.delete(question)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Вопрос удален'
    })


# Инициализация базы данных и тестовые данные
def init_db():
    with app.app_context():
        db.create_all()

        # Добавляем тестовые данные, если база пустая
        if Category.query.count() == 0:
            categories = [
                Category(name='История'),
                Category(name='Наука'),
                Category(name='Спорт'),
                Category(name='География')
            ]
            db.session.add_all(categories)
            db.session.commit()

            questions = [
                Question(text='В каком году началась Вторая мировая война?', category_id=1),
                Question(text='Кто открыл закон всемирного тяготения?', category_id=2),
                Question(text='Сколько игроков в футбольной команде?', category_id=3),
                Question(text='Столица Франции?', category_id=4),
            ]
            db.session.add_all(questions)
            db.session.commit()

            print('✓ База данных инициализирована с тестовыми данными')


if __name__ == '__main__':
    init_db()
    print('\n' + '='*80)
    print('QUIZ API ЗАПУЩЕН')
    print('='*80)
    print('Доступные эндпоинты:')
    print('  GET    http://127.0.0.1:5000/api/categories')
    print('  POST   http://127.0.0.1:5000/api/categories')
    print('  GET    http://127.0.0.1:5000/api/categories/<id>')
    print('  PUT    http://127.0.0.1:5000/api/categories/<id>')
    print('  DELETE http://127.0.0.1:5000/api/categories/<id>')
    print('  GET    http://127.0.0.1:5000/api/questions')
    print('  POST   http://127.0.0.1:5000/api/questions')
    print('  GET    http://127.0.0.1:5000/api/categories/<id>/questions')
    print('='*80 + '\n')
    app.run(debug=True)
