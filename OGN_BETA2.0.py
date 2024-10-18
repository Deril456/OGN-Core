from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import jwt
import datetime
import ssl
import os

# Инициализация приложения Flask
app = Flask(__name__)
CORS(app)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Ограничение числа запросов
limiter = Limiter(get_remote_address, app=app)

# Секретный ключ для JWT
SECRET_KEY = "supersecretkey"

# Модель пользователя для базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Создание таблицы в базе данных (при первом запуске)
with app.app_context():
    db.create_all()

# Функция хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Домашняя страница
@app.route('/')
def home():
    return "Hello, Secure World!"

# Регистрация пользователя
@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")  # Ограничение 5 запросов в минуту
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Проверка существующего пользователя
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'status': 'error', 'message': 'User already exists'}), 400

    # Хеширование пароля с использованием hashlib
    hashed_password = hash_password(password)

    # Сохранение пользователя в базе данных
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'User registered successfully'}), 201

# Вход пользователя
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Ограничение 5 запросов в минуту
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Поиск пользователя в базе данных
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User does not exist'}), 400

    # Проверка пароля (сравниваем хеши)
    hashed_password = hash_password(password)
    if hashed_password != user.password:
        return jsonify({'status': 'error', 'message': 'Incorrect password'}), 400

    # Генерация JWT токена
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({'status': 'success', 'token': token}), 200

# Защищённый маршрут
@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Token is missing!'}), 401

    try:
        # Декодирование токена
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({'status': 'success', 'message': 'Access granted', 'user': data['username']}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'error', 'message': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401

if __name__ == '__main__':
    # Определение абсолютных путей к сертификатам
    cert_path = os.path.join(os.path.expanduser('~'), 'cert.pem')  # Путь к cert.pem
    key_path = os.path.join(os.path.expanduser('~'), 'key.pem')    # Путь к key.pem

    # Проверка существования файлов сертификатов
    if not os.path.isfile(cert_path):
        print(f"Файл сертификата не найден: {cert_path}")
        exit(1)

    if not os.path.isfile(key_path):
        print(f"Файл ключа не найден: {key_path}")
        exit(1)

    # Создаем SSL контекст
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    # Запускаем Flask-приложение с SSL
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
