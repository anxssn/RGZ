from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from app.database import init_db, add_user, get_user_by_username, add_video, get_user_videos, add_chat_message, \
    get_chat_messages, get_all_videos, get_recent_videos, delete_video

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'your-secret-key'

# Абсолютный путь к папке uploads
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Убедитесь, что папка существует
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Инициализация базы данных
init_db()


@app.route('/')
def index():
    try:
        template_path = os.path.join(app.template_folder, 'index.html')
        print(f"Попытка загрузить шаблон из: {template_path}")
        if not os.path.exists(template_path):
            print(f"Файл не найден по пути: {template_path}")
            return "Ошибка: файл index.html не найден в app/templates/", 500
        recent_videos = get_recent_videos(limit=3)
        return render_template('index.html', videos=recent_videos)
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return f"Произошла ошибка: {str(e)}", 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        if add_user(username, email, hashed_password):
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Пользователь с таким именем или email уже существует.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            flash('Вход успешен!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    flash('Вы вышли из аккаунта.', 'success')
    return redirect(url_for('index'))


@app.route('/video', methods=['GET', 'POST'])
def video():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в аккаунт.', 'error')
        return redirect(url_for('login'))

    video_url = None
    if request.method == 'POST':
        if 'video_file' in request.files:
            video_file = request.files['video_file']
            if video_file:
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
                video_file.save(video_path)
                add_video(session['user_id'], f'static/uploads/{video_file.filename}')
                video_url = url_for('static', filename=f'uploads/{video_file.filename}')
        elif 'message' in request.form:
            message = request.form['message']
            if message:
                add_chat_message(session['user_id'], message)

    videos = get_all_videos()
    messages = get_chat_messages()
    return render_template('video.html', video_url=video_url, videos=videos, messages=messages)


@app.route('/account')
def account():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в аккаунт.', 'error')
        return redirect(url_for('login'))

    videos = get_user_videos(session['user_id'])
    video_urls = [video['video_path'] for video in videos]
    return render_template('account.html', username=session['username'], email=session['email'], video_urls=video_urls)


@app.route('/delete_video/<path:video_path>', methods=['POST'])
def delete_video_route(video_path):
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в аккаунт.', 'error')
        return redirect(url_for('login'))

    delete_video(video_path, session['user_id'])
    flash('Видео успешно удалено.', 'success')
    return redirect(url_for('account'))


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return {'error': 'Не авторизован'}, 401

    if request.method == 'POST':
        message = request.form['message']
        add_chat_message(session['user_id'], message)

    messages = get_chat_messages()
    return {'messages': [{'username': msg['username'], 'message': msg['message']} for msg in messages]}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Используем порт Render
    app.run(host='0.0.0.0', port=port, debug=False)