import json
import logging
import os
import asyncio
from fastapi import FastAPI, HTTPException, Request
import httpx
import aiofiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Читаем API-ключ из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("API-ключ OpenAI не найден! Укажите его в .env файле.")

CATEGORY_OPTIONS = [
    "Жалоба на блюдо", "Жалоба на просрочку на доставке", "Жалоба на просрочку в зале",
    "Положительный отзыв", "Жалоба на долгую доставку", "Жалоба на то, что не дозвониться по телефону",
    "Жалоба на опоздание доставки", "Жалоба на доставку", "Жалоба на кофе на доставку",
    "Жалоба на пустые полки", "Жалоба на недовоз", "Жалоба на грубость продавцов",
    "Жалоба на кофе в зале"
]

CSV_FILE = "reviews.csv"


class Review(BaseModel):
    date_create: str
    text_comment: str
    guests_id: int
    source_type: int
    shop_name: str
    source_description: str
    vote: int
    products: str
    problem_products: str = ""
    category_comment: str = ""


async def ensure_csv_exists():
    """Асинхронно проверяет наличие CSV-файла и создаёт его при необходимости."""
    if not os.path.exists(CSV_FILE):
        async with aiofiles.open(CSV_FILE, mode='w', encoding='utf-8', newline='') as file:
            await file.write(
                "date_create;text_comment;guests_id;source_type;shop_name;source_description;vote;products;problem_products;category_comment\n"
            )


semaphore = asyncio.Semaphore(5)

import json
import logging
import os
import asyncio
from fastapi import FastAPI, HTTPException, Request
import httpx
import aiofiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Читаем API-ключ из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("API-ключ OpenAI не найден! Укажите его в .env файле.")

CATEGORY_OPTIONS = [
    "Жалоба на блюдо", "Жалоба на просрочку на доставке", "Жалоба на просрочку в зале",
    "Положительный отзыв", "Жалоба на долгую доставку", "Жалоба на то, что не дозвониться по телефону",
    "Жалоба на опоздание доставки", "Жалоба на доставку", "Жалоба на кофе на доставку",
    "Жалоба на пустые полки", "Жалоба на недовоз", "Жалоба на грубость продавцов",
    "Жалоба на кофе в зале"
]

CSV_FILE = "reviews.csv"


class Review(BaseModel):
    date_create: str
    text_comment: str
    guests_id: int
    source_type: int
    shop_name: str
    source_description: str
    vote: int
    products: str
    problem_products: str = ""
    category_comment: str = ""


async def ensure_csv_exists():
    """Асинхронно проверяет наличие CSV-файла и создаёт его при необходимости."""
    if not os.path.exists(CSV_FILE):
        async with aiofiles.open(CSV_FILE, mode='w', encoding='utf-8', newline='') as file:
            await file.write(
                "date_create;text_comment;guests_id;source_type;shop_name;source_description;vote;products;problem_products;category_comment\n"
            )


semaphore = asyncio.Semaphore(5)

import json
import logging
import os
import asyncio
from fastapi import FastAPI, HTTPException, Request
import httpx
import aiofiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Читаем API-ключ из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("API-ключ OpenAI не найден! Укажите его в .env файле.")

CATEGORY_OPTIONS = [
    "Жалоба на блюдо", "Жалоба на просрочку на доставке", "Жалоба на просрочку в зале",
    "Положительный отзыв", "Жалоба на долгую доставку", "Жалоба на то, что не дозвониться по телефону",
    "Жалоба на опоздание доставки", "Жалоба на доставку", "Жалоба на кофе на доставку",
    "Жалоба на пустые полки", "Жалоба на недовоз", "Жалоба на грубость продавцов",
    "Жалоба на кофе в зале"
]

CSV_FILE = "reviews.csv"


class Review(BaseModel):
    date_create: str
    text_comment: str
    guests_id: int
    source_type: int
    shop_name: str
    source_description: str
    vote: int
    products: str
    problem_products: str = ""
    category_comment: str = ""


async def ensure_csv_exists():
    """Асинхронно проверяет наличие CSV-файла и создаёт его при необходимости."""
    if not os.path.exists(CSV_FILE):
        async with aiofiles.open(CSV_FILE, mode='w', encoding='utf-8', newline='') as file:
            await file.write(
                "date_create;text_comment;guests_id;source_type;shop_name;source_description;vote;products;problem_products;category_comment\n"
            )


semaphore = asyncio.Semaphore(5)


async def analyze_text_with_openai(text: str, prompt_type: str, products: str = None):
    """Асинхронный запрос к OpenAI с обработкой таймаутов."""
    if not text.strip():
        return []

    logging.info(f"Отправка запроса в OpenAI для анализа текста: {text}")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    if prompt_type == "category":
        prompt = f"""
        Проанализируй отзыв клиента и выбери все подходящие категории из списка: {', '.join(CATEGORY_OPTIONS)}. 
        Если отзыв касается плохого качества продуктов, обязательно включи "Жалоба на блюдо". 
        Перечисли категории через запятую без дополнительных пояснений.
        Отзыв: {text}
        """
    elif prompt_type == "products":
        prompt = f"""
        Определи все упомянутые блюда из списка: {products}. 
        Укажи только найденные блюда через запятую без дополнительных пояснений.
        Если блюдо не указано, верни пустую строку.
        Отзыв: {text}
        """

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Ты специалист по анализу отзывов клиентов."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100
    }

    retries = 3
    timeout = 60.0

    async with semaphore:
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    category_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                    return [c.strip() for c in category_text.split(",") if c.strip()]

                elif response.status_code == 429:
                    logging.warning("Превышен лимит запросов, ожидание...")
                    await asyncio.sleep(2)

                else:
                    logging.error(f"Ошибка OpenAI: {response.text}")
                    return []

            except httpx.ReadTimeout:
                logging.warning(f"Таймаут! Попытка {attempt + 1} из {retries}...")
                await asyncio.sleep(5)

            except httpx.RequestError as e:
                logging.error(f"Ошибка сети: {e}")
                return []

    return []


async def process_review(review_data):
    """Обработка одного отзыва."""
    if not review_data.get("text_comment", "").strip():
        return None

    review = Review(**review_data)
    categories = await analyze_text_with_openai(review.text_comment, "category")
    review.category_comment = ", ".join(categories) if categories else "Без категории"

    if "Жалоба на блюдо" in categories or "Жалоба на просрочку в зале" in categories:
        problem_products = await analyze_text_with_openai(review.text_comment, "products", review.products)
        review.problem_products = json.dumps(problem_products, ensure_ascii=False) if problem_products else "[]"

    return review

async def write_reviews_to_csv(reviews):
    """Запись отзывов в CSV."""
    async with aiofiles.open(CSV_FILE, mode='a', encoding='utf-8', newline='') as file:
        for review in reviews:
            if review:
                row = [
                    review.date_create, json.dumps(review.text_comment, ensure_ascii=False), review.guests_id,
                    review.source_type, review.shop_name, json.dumps(review.source_description, ensure_ascii=False),
                    review.vote, json.dumps(review.products, ensure_ascii=False),
                    json.dumps(review.problem_products, ensure_ascii=False),
                    json.dumps(review.category_comment, ensure_ascii=False)
                ]
                await file.write(";".join(map(str, row)) + "\n")


@app.post("/analyze")
async def analyze_reviews(request: Request):
    reviews = await request.json()
    if not isinstance(reviews, list):
        raise HTTPException(status_code=400, detail="Некорректный формат данных")

    await ensure_csv_exists()
    processed_reviews = await asyncio.gather(*[process_review(review) for review in reviews])
    processed_reviews = [r for r in processed_reviews if r is not None]
    await write_reviews_to_csv(processed_reviews)

    return {"status": "success", "processed_reviews": [r.model_dump() for r in processed_reviews]}
