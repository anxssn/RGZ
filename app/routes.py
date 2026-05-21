from app import app
from flask import render_template, request, redirect, url_for
import os

users = []  # Список пользователей
user_videos = {}  # Словарь: email пользователя -> список его видео
UPLOAD_FOLDER = 'app/static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
last_uploaded_video = None

@app.route('/')
def index():
    print(f"Переход на главную страницу: {request.url}")
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    print(f"Переход на страницу регистрации: {request.url}")
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        users.append({'username': username, 'email': email, 'password': password})
        user_videos[email] = []
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/video', methods=['GET', 'POST'])
def video():
    global last_uploaded_video
    video_url = None
    if last_uploaded_video:
        video_url = url_for('static', filename=f'uploads/{last_uploaded_video}')
    if request.method == 'POST':
        video_file = request.files['video_file']
        if video_file:
            filename = video_file.filename
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video_file.save(video_path)
            last_uploaded_video = filename
            video_url = url_for('static', filename=f'uploads/{filename}')
            if users:
                current_user_email = users[-1]['email']
                if current_user_email not in user_videos:
                    user_videos[current_user_email] = []
                user_videos[current_user_email].append(filename)
    return render_template('video.html', video_url=video_url)

@app.route('/account')
def account():
    print(f"Переход на страницу аккаунта: {request.url}")
    if not users:
        return redirect(url_for('register'))
    current_user = users[-1]
    username = current_user['username']
    email = current_user['email']
    videos = user_videos.get(email, [])
    video_urls = [url_for('static', filename=f'uploads/{video}') for video in videos]
    return render_template('account.html', username=username, email=email, video_urls=video_urls)

# Проверка зарегистрированных маршрутов
with app.app_context():
    print("Зарегистрированные маршруты:")
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, URL: {rule}")