from flask import Flask, request, jsonify
from flask_cors import CORS
import ssl
import os

app = Flask(name)
CORS(app)

# Хранилище для пользователей (это просто пример, используйте базу данных в реальных приложениях)
users = {}

@app.route('/')
def home():
    return "Hello, Secure World!"

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users:
        return jsonify({'status': 'error', 'message': 'User already exists'}), 400

    users[username] = password
    return jsonify({'status': 'success', 'message': 'User registered successfully'}), 201

if name == 'main':
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
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # Обновленный протокол
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    # Запускаем Flask-приложение с SSL
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
