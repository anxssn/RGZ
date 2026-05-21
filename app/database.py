import sqlite3
from datetime import datetime
import os

# Абсолютный путь к базе данных
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'videoplatform.db'))

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных (создание таблиц)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Таблица видео
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            video_path TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Таблица сообщений чата
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Добавление пользователя с обработкой ошибки
def add_user(username, email, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                       (username, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Получение пользователя по имени
def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Добавление видео
def add_video(user_id, video_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    upload_date = datetime.now().isoformat()
    cursor.execute('INSERT INTO videos (user_id, video_path, upload_date) VALUES (?, ?, ?)',
                   (user_id, video_path, upload_date))
    conn.commit()
    conn.close()

# Удаление видео по пути
def delete_video(video_path, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM videos WHERE video_path = ? AND user_id = ?', (video_path, user_id))
    conn.commit()
    conn.close()

# Получение видео пользователя
def get_user_videos(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos WHERE user_id = ?', (user_id,))
    videos = cursor.fetchall()
    conn.close()
    return videos

# Получение всех видео
def get_all_videos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT videos.*, users.username FROM videos JOIN users ON videos.user_id = users.id ORDER BY upload_date DESC')
    videos = cursor.fetchall()
    conn.close()
    return videos

# Получение последних трёх видео
def get_recent_videos(limit=3):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT videos.*, users.username FROM videos JOIN users ON videos.user_id = users.id ORDER BY upload_date DESC LIMIT ?', (limit,))
    videos = cursor.fetchall()
    conn.close()
    return videos

# Добавление сообщения в чат
def add_chat_message(user_id, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('INSERT INTO chat_messages (user_id, message, timestamp) VALUES (?, ?, ?)',
                   (user_id, message, timestamp))
    conn.commit()
    conn.close()

# Получение всех сообщений чата
def get_chat_messages():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT chat_messages.*, users.username FROM chat_messages JOIN users ON chat_messages.user_id = users.id ORDER BY timestamp')
    messages = cursor.fetchall()
    conn.close()
    return messages

# Функция для добавления тестовых данных
def add_test_data():
    # Добавляем тестового пользователя
    username = "testuser"
    email = "testuser@example.com"
    password = "testhash"
    user = get_user_by_username(username)
    if not user:
        add_user(username, email, password)
        user = get_user_by_username(username)

    # Добавляем три тестовых видео
    user_id = user['id']
    videos = [
        "static/uploads/video1.mp4",
        "static/uploads/video2.mp4",
        "static/uploads/video3.mp4"
    ]
    for video_path in videos:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM videos WHERE video_path = ?', (video_path,))
        if not cursor.fetchone():
            add_video(user_id, video_path)
        conn.close()

if __name__ == '__main__':
    init_db()
    add_test_data()