import os
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def run_bot():
    print(f"Токен получен: {TOKEN[:5]}...")  # выведет первые 5 символов
    print("Бот запущен (упрощённая версия)")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()