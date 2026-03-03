import json
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # разрешаем запросы с любого источника (для разработки)

DATABASE = 'database.db'

def init_db():
    """Создаёт таблицу, если её нет"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS shows (
            user_id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Хендлер для главной страницы (отдаёт index.html)
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

# Получить список сериалов пользователя
@app.route('/api/shows/<user_id>', methods=['GET'])
def get_shows(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT data FROM shows WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(json.loads(row[0]))
    else:
        return jsonify([])

# Сохранить список сериалов пользователя
@app.route('/api/shows/<user_id>', methods=['POST'])
def save_shows(user_id):
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO shows (user_id, data) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET data=excluded.data
    ''', (user_id, json.dumps(data)))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
