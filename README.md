# Analyze Reviews API

## Описание
Этот сервис предоставляет API для анализа отзывов клиентов. Он использует OpenAI GPT-4o для классификации отзывов по категориям и автоматически определяет проблемные продукты в жалобах.

## Установка и запуск
### Требования:
- Python 3.8+
- Установленные зависимости

### 1. Установка зависимостей
Создайте виртуальное окружение (рекомендуется):
```sh
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

Установите необходимые пакеты:
```sh
pip install fastapi uvicorn httpx
```

### 2. Запуск сервера
Запустите API-сервер с помощью Uvicorn:
```sh
uvicorn main:app --reload
```

Сервер запустится на `http://127.0.0.1:8000`.

## Тестирование API
### 1. Тестирование через браузер
Перейдите в браузере по адресу:
```sh
http://127.0.0.1:8000/docs
```
Здесь доступен Swagger UI, где можно отправлять тестовые запросы.

### 2. Тестирование через cURL
Отправьте POST-запрос с отзывом:
```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/analyze' \
  -H 'Content-Type: application/json' \
  -d '[{
        "date_create": "2024-03-15",
        "text_comment": "Бургер был холодным и невкусным.",
        "guests_id": 123,
        "source_type": 1,
        "shop_name": "Test Shop",
        "source_description": "Отзыв с сайта",
        "vote": 1,
        "products": "[\"пицца\", \"бургер\"]"
    }]'
```

### 3. Тестирование через Python
```python
import requests

url = "http://127.0.0.1:8000/analyze"
data = [{
    "date_create": "2024-03-15",
    "text_comment": "Бургер был холодным и невкусным.",
    "guests_id": 123,
    "source_type": 1,
    "shop_name": "Test Shop",
    "source_description": "Отзыв с сайта",
    "vote": 1,
    "products": "[\"пицца\", \"бургер\"]"
}]
response = requests.post(url, json=data)
print(response.json())
```

## Ожидаемый ответ API
```json
{
  "status": "success",
  "processed_reviews": [
    {
      "date_create": "2024-03-15",
      "text_comment": "Бургер был холодным и невкусным.",
      "guests_id": 123,
      "source_type": 1,
      "shop_name": "Test Shop",
      "source_description": "Отзыв с сайта",
      "vote": 1,
      "products": "[\"пицца\", \"бургер\"]",
      "problem_products": "[\"бургер\"]",
      "category_comment": "Жалоба на блюдо"
    }
  ]
}
```

## Файлы
- `main.py` — основной код API
- `reviews.csv` — CSV-файл с сохраненными отзывами

## Лицензия
MIT License.