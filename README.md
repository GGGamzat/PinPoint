# PinPoint
***

***Содержание:***
+ [Введение](#введение)
+ [Требования к реализации](#-требования-к-реализации)
  + [Функциональные требования](#функциональные-требования)
  + [Технические требования](#функциональные-требования)
+ [Установка и запуск](#-запуск-проекта)
+ [API Эндпоинты](#-api-эндпоинты)

# Введение
***
**PinPoint** - Backend-приложение на Django(DRF) для работы с географическими точками на карте. Приложение предоставляет REST API для создания точек, обмена сообщениями и поиска контента в заданном радиусе от указанных координат.

# 📋 Требования к реализации
***
### Функциональные требования:
1. ✔ Создание точки на карте
2. ✔ Создание сообщения к заданной точке
3. ✔ Поиск точек в заданном радиусе
4. ✔ Получение сообщений от пользователей в заданной области
5. ✔ Использовать авторизацию для всех эндпоинтов

### Технические требования:
+ Python 3.10
+ Django 5
+ Django Rest Framework
+ PostgreSQL, PostGIS
+ GeoDjango
+ Django TestCase

# 🚀 Запуск проекта
***
+ Клонируйте репозиторий и перейдите в папку проекта
```
git clone https://github.com/GGGamzat/PinPoint.git
cd PinPoint
```

+ Соберите и запустите с помощью Docker
```
docker-compose up --build
```

+ Api будет доступно по адресу http://localhost:8000/api/

+ Запуск тестов
```
docker-compose exec web python manage.py test
```

# 📡 API Эндпоинты
***
## 🔐 Аутентификация
+ [POST /api/auth/register/ - регистрация](#1-регистрация-пользователя)
+ [POST /api/auth/login/ - вход в систему](#2-вход-в-систему)
+ [POST /api/auth/logout/ - выход из системы](#3-выход-из-системы)

## 📍 Точки
+ [POST /api/points/ - создание точки](#4-создание-точки)
+ [GET /api/points/search/ - поиск точек в радиусе](#5-поиск-точек-в-радиусе)

## 💬 Сообщения
+ [POST /api/messages/ - создание сообщения к точке](#6-создание-сообщения-к-точке)
+ [GET /api/messages/search/ - поиск сообщений в радиусе](#7-поиск-сообщений-в-радиусе)
***
> Далее даны запросы в виде curl (две версии: для Windows и для Linux/macOS)
> > Не забудьте подставить свой ТОКЕН в запрос, там где это требуется (все запросы требуют токены кроме Регистрации и Входа в систему)❗❗❗

### 1. Регистрация пользователя
#### Windows (PowerShell):
```
curl -X POST http://localhost:8000/api/auth/register/ `
  -H "Content-Type: application/json" `
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```
#### Linux/MacOS:
```
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

### 2. Вход в систему
#### Windows (PowerShell):
```
curl -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```
#### Linux/MacOS:
```
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

### 3. Выход из системы
#### Windows (PowerShell):
```
curl -X POST http://localhost:8000/api/auth/logout/ `
  -H "Authorization: Token YOUR_TOKEN_HERE"
```
#### Linux/MacOS:
```
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 4. Создание точки
#### Windows (PowerShell):
```
curl -X POST http://localhost:8000/api/points/ `
  -H "Authorization: Token YOUR_TOKEN_HERE" `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Эйфелева башня",
    "description": "Знаменитая башня в Париже",
    "latitude": 48.8584,
    "longitude": 2.2945
  }'
```
#### Linux/MacOS:
```
curl -X POST http://localhost:8000/api/points/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Эйфелева башня",
    "description": "Знаменитая башня в Париже",
    "latitude": 48.8584,
    "longitude": 2.2945
  }'
```

### 5. Поиск точек в радиусе
#### Windows (PowerShell):
```
curl -X GET "http://localhost:8000/api/points/search/?latitude=55.7558&longitude=37.6176&radius=10" `
  -H "Authorization: Token YOUR_TOKEN_HERE"
```
#### Linux/MacOS:
```
curl -X GET "http://localhost:8000/api/points/search/?latitude=55.7558&longitude=37.6176&radius=10" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 6. Создание сообщения к точке
#### Windows (PowerShell):
```
curl -X POST http://localhost:8000/api/messages/ `
  -H "Authorization: Token YOUR_TOKEN_HERE" `
  -H "Content-Type: application/json" `
  -d '{
    "point_id": 1,
    "text": "Очень красивое место!"
  }'
```
#### Linux/MacOS:
```
curl -X POST http://localhost:8000/api/messages/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "point_id": 1,
    "text": "Очень красивое место!"
  }'
```

### 7. Поиск сообщений в радиусе
#### Windows (PowerShell):
```
curl -X GET "http://localhost:8000/api/messages/search/?latitude=55.7558&longitude=37.6176&radius=5" `
  -H "Authorization: Token YOUR_TOKEN_HERE"
```
#### Linux/MacOS:
```
curl -X GET "http://localhost:8000/api/messages/search/?latitude=55.7558&longitude=37.6176&radius=5" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```