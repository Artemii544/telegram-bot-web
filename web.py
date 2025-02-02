from flask import Flask, render_template, request, redirect, url_for
import hmac
import hashlib
import json
import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле!")

BOT_USERNAME = "mass_looking_bot"  # Замените на username вашего бота

def check_telegram_auth(auth_data):
    """Проверка данных авторизации от Telegram"""
    try:
        if 'hash' not in auth_data:
            logger.error("Hash отсутствует в данных авторизации")
            return False
        
        # Получаем hash для проверки
        received_hash = auth_data['hash']
        auth_data_check = dict(auth_data)
        del auth_data_check['hash']
        
        # Сортируем параметры
        data_check_list = []
        for key, value in sorted(auth_data_check.items()):
            data_check_list.append(f"{key}={value}")
        data_check_string = "\n".join(data_check_list)
        
        # Создаем secret_key из токена бота
        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        
        # Вычисляем hash
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return computed_hash == received_hash
    except Exception as e:
        logger.error(f"Ошибка при проверке авторизации: {str(e)}")
        return False

@app.route('/')
def index():
    """Главная страница с виджетом авторизации"""
    try:
        return render_template(
            'index.html',
            bot_username=BOT_USERNAME
        )
    except Exception as e:
        logger.error(f"Ошибка при рендеринге главной страницы: {str(e)}")
        return "Произошла ошибка при загрузке страницы", 500

@app.route('/login/telegram')
def telegram_login():
    """Обработчик авторизации через Telegram"""
    try:
        auth_data = request.args.to_dict()
        logger.info(f"Получены данные авторизации: {json.dumps(auth_data, ensure_ascii=False)}")
        
        if check_telegram_auth(auth_data):
            # Сохраняем данные пользователя
            user_id = auth_data['id']
            first_name = auth_data.get('first_name', '')
            username = auth_data.get('username', '')
            photo_url = auth_data.get('photo_url', '')
            auth_date = auth_data['auth_date']
            
            logger.info(f"Успешная авторизация пользователя {username} (ID: {user_id})")
            return render_template(
                'success.html',
                username=username or first_name
            )
        else:
            logger.warning("Неудачная попытка авторизации")
            return "Ошибка авторизации. Пожалуйста, попробуйте снова.", 400
    except Exception as e:
        logger.error(f"Ошибка при обработке авторизации: {str(e)}")
        return "Произошла ошибка при авторизации", 500

if __name__ == '__main__':
    # Создаем папку для шаблонов если её нет
    os.makedirs('templates', exist_ok=True)
    logger.info("Сервер запущен на http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=True) 