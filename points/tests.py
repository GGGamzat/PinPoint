from django.test import TestCase
from django.contrib.gis.geos import Point as GeoPoint
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Point, Message

User = get_user_model()


class CoreFunctionalityTests(APITestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        # Создаем токен для аутентификации
        from .authentication import create_token
        token = create_token(self.user)

        # Настраиваем клиент с токеном
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Создаем несколько тестовых точек
        self.moscow_point = Point.objects.create(
            user=self.user,
            name='Московский Кремль',
            location=GeoPoint(37.6176, 55.7558, srid=4326)
        )

        self.spb_point = Point.objects.create(
            user=self.user,
            name='Эрмитаж',
            location=GeoPoint(30.3141, 59.9386, srid=4326)
        )

        self.paris_point = Point.objects.create(
            user=self.user,
            name='Эйфелева башня',
            location=GeoPoint(2.2945, 48.8584, srid=4326)
        )

    def test_create_point_on_map(self):
        print("\n--- ТЕСТ №1: Создание точки на карте 📍 ---")

        url = '/api/points/'
        data = {
            'name': 'Красная площадь',
            'description': 'Главная площадь Москвы',
            'latitude': 55.7539,
            'longitude': 37.6208
        }

        response = self.client.post(url, data, format='json')

        # Проверяем успешное создание
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем возвращаемые данные
        self.assertIn('id', response.data)
        self.assertEqual(response.data['name'], 'Красная площадь')
        self.assertEqual(response.data['description'], 'Главная площадь Москвы')
        self.assertEqual(response.data['latitude'], 55.7539)
        self.assertEqual(response.data['longitude'], 37.6208)

        # Проверяем что точка создана в базе
        point_id = response.data['id']
        point_in_db = Point.objects.get(id=point_id)
        self.assertEqual(point_in_db.name, 'Красная площадь')
        self.assertEqual(point_in_db.user, self.user)

        print(f"✔ Точка создана: ID={point_id}, координаты: ({55.7539}, {37.6208})")
        return True


    def test_create_message_to_point(self):
        print("\n--- ТЕСТ №2: Создание сообщения к точке 📄 ---")

        url = '/api/messages/'
        data = {
            'point_id': self.moscow_point.id,
            'text': 'Историческое место России, обязательно к посещению!'
        }

        response = self.client.post(url, data, format='json')

        # Проверяем успешное создание
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем возвращаемые данные
        self.assertIn('id', response.data)
        self.assertEqual(response.data['text'], 'Историческое место России, обязательно к посещению!')
        self.assertEqual(response.data['point']['id'], self.moscow_point.id)
        self.assertEqual(response.data['point']['name'], 'Московский Кремль')

        # Проверяем что сообщение создано в базе
        message_id = response.data['id']
        message_in_db = Message.objects.get(id=message_id)
        self.assertEqual(message_in_db.text, 'Историческое место России, обязательно к посещению!')
        self.assertEqual(message_in_db.point, self.moscow_point)
        self.assertEqual(message_in_db.user, self.user)

        print(f"✔ Сообщение создано: ID={message_id}, точка: {self.moscow_point.name}")
        return True


    def test_search_points_in_radius(self):
        print("\n--- ТЕСТ №3: Поиск точек в радиусе 🔍 ---")

        # Поиск в радиусе 5 км от Кремля (должен найти только московскую точку)
        url = '/api/points/search/'
        params = {
            'latitude': 55.7558,  # Координаты Москвы
            'longitude': 37.6176,
            'radius': 5
        }

        response = self.client.get(url, params)

        # Проверяем успешный запрос
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        self.assertIn('count', response.data)
        self.assertIn('points', response.data)

        # Должна найтись только 1 точка (Московский Кремль)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['points']), 1)
        self.assertEqual(response.data['points'][0]['name'], 'Московский Кремль')

        print(f"✔ Найдено {response.data['count']} точек в радиусе {params['radius']} км от ({params['latitude']}, {params['longitude']})")

        # Дополнительный тест: поиск в большом радиусе
        params_large = {
            'latitude': 55.7558,  # Москва
            'longitude': 37.6176,
            'radius': 1000  # 1000 км (покрывает Москву, Санкт-Петербург)
        }

        response_large = self.client.get(url, params_large)
        self.assertEqual(response_large.status_code, status.HTTP_200_OK)
        # Должно найти 2 точки
        self.assertEqual(response_large.data['count'], 2)

        print(f"✔ При радиусе 1000 км найдено {response_large.data['count']} точек")
        return True


    def test_get_messages_in_area(self):
        print("\n--- ТЕСТ №4: Поиск сообщений в радиусе 🔍 ---")

        # Сначала создаем несколько сообщений к разным точкам
        message1 = Message.objects.create(
            point=self.moscow_point,
            user=self.user,
            text='Красивый Кремль в Москве'
        )

        message2 = Message.objects.create(
            point=self.spb_point,
            user=self.user,
            text='Великолепный Эрмитаж в Петербурге'
        )

        message3 = Message.objects.create(
            point=self.paris_point,
            user=self.user,
            text='Величественная Эйфелева башня в Париже'
        )

        # Поиск сообщений в радиусе 10 км от Москвы
        url = '/api/messages/search/'
        params = {
            'latitude': 55.7558,  # Москва
            'longitude': 37.6176,
            'radius': 10
        }

        response = self.client.get(url, params)

        # Проверяем успешный запрос
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа
        self.assertIn('count', response.data)
        self.assertIn('messages', response.data)

        # Должно найтись только 1 сообщение (к московской точке)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['messages']), 1)
        self.assertEqual(response.data['messages'][0]['text'], 'Красивый Кремль в Москве')
        self.assertEqual(response.data['messages'][0]['point']['name'], 'Московский Кремль')

        print(f"✔ Найдено {response.data['count']} сообщений в радиусе {params['radius']} км от Москвы")

        # Дополнительный тест: поиск в радиусе 1000 км (должен найти 2 сообщения)
        params_large = {
            'latitude': 55.7558,  # Москва
            'longitude': 37.6176,
            'radius': 1000  # 1000 км
        }

        response_large = self.client.get(url, params_large)
        self.assertEqual(response_large.status_code, status.HTTP_200_OK)
        # Должно найти 2 сообщения
        self.assertEqual(response_large.data['count'], 2)

        print(f"✔ При радиусе 3000 км найдено {response_large.data['count']} сообщений")
        return True

    def test_authorization_required(self):
        print("\n--- ТЕСТ №5: Проверка авторизации 🔐 ---")

        # Создаем новый клиент без авторизации
        unauthorized_client = APIClient()

        endpoints = [
            ('/api/points/', 'POST'),
            ('/api/points/', 'GET'),
            ('/api/points/search/?latitude=55&longitude=37&radius=10', 'GET'),
            ('/api/messages/', 'POST'),
            ('/api/messages/', 'GET'),
            ('/api/messages/search/?latitude=55&longitude=37&radius=10', 'GET'),
        ]

        for url, method in endpoints:
            if method == 'POST':
                response = unauthorized_client.post(url, {}, format='json')
            elif method == 'GET':
                response = unauthorized_client.get(url)

            # Должен вернуть 401 Unauthorized
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Эндпоинт {method} {url} должен требовать авторизацию"
            )

        print("✔ Все защищенные эндпоинты требуют авторизацию")
        return True


    def test_full_scenario(self):
        print("\n--- ТЕСТ №6: Полный сценарий использования ---")

        # 1. Создаем точку
        point_data = {
            'name': 'Стадион Лужники',
            'description': 'Крупнейший стадион России',
            'latitude': 55.7157,
            'longitude': 37.5538
        }

        point_response = self.client.post('/api/points/', point_data, format='json')
        self.assertEqual(point_response.status_code, status.HTTP_201_CREATED)
        point_id = point_response.data['id']
        print(f"✔ Создана точка: {point_response.data['name']}")

        # 2. Создаем сообщение к точке
        message_data = {
            'point_id': point_id,
            'text': 'Отличный стадион для футбольных матчей!'
        }

        message_response = self.client.post('/api/messages/', message_data, format='json')
        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        print(f"✔ Создано сообщение: {message_response.data['text'][:30]}...")

        # 3. Ищем точки в радиусе 2 км от стадиона
        search_params = {
            'latitude': 55.7157,
            'longitude': 37.5538,
            'radius': 2
        }

        search_response = self.client.get('/api/points/search/', search_params)
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(search_response.data['count'], 1)
        print(f"✔ Найдено {search_response.data['count']} точек в радиусе 2 км")

        # 4. Ищем сообщения в радиусе 2 км
        messages_search_response = self.client.get('/api/messages/search/', search_params)
        self.assertEqual(messages_search_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(messages_search_response.data['count'], 1)
        print(f"✔ Найдено {messages_search_response.data['count']} сообщений в радиусе 2 км")

        print("✔ Полный сценарий выполнен успешно!")
        return True