from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Хранилище для пользователей (это просто пример, используйте базу данных в реальных приложениях)
users = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users:
        return jsonify({'status': 'error', 'message': 'User already exists'}), 400

    users[username] = password
    return jsonify({'status': 'success', 'message': 'User registered successfully'}), 201

# Другие маршруты вашего приложения...

if __name__ == '__main__':
    # Запуск сервера на localhost или другом IP-адресе, указанный пользователем
    app.run(debug=True)