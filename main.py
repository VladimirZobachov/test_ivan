import csv
import json
import logging
import os
from fastapi import FastAPI, HTTPException, Request
import httpx
from typing import List
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

app = FastAPI()

OPENAI_API_KEY = "openai_api_key"
CATEGORY_OPTIONS = [
    "Жалоба на блюдо",
    "Жалоба на просрочку на доставке",
    "Жалоба на просрочку в зале",
    "Положительный отзыв",
    "Жалоба на долгую доставку",
    "Жалоба на то, что не дозвониться по телефону",
    "Жалоба на опоздание доставки",
    "Жалоба на доставку",
    "Жалоба на кофе на доставку",
    "Жалоба на пустые полки",
    "Жалоба на недовоз",
    "Жалоба на грубость продавцов",
    "Жалоба на кофе в зале",
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


def ensure_csv_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                ["date_create", "text_comment", "guests_id", "source_type", "shop_name", "source_description", "vote",
                 "products", "problem_products", "category_comment"])


async def analyze_text_with_openai(text: str) -> str:
    logging.info(f"Отправка запроса в OpenAI для анализа текста: {text}")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Ты должен выбрать категорию отзыва из списка."},
            {"role": "user",
             "content": f"Ты классификатор отзывов. Твоя задача — выбрать одну категорию отзыва из списка: {', '.join(CATEGORY_OPTIONS)}. Текст: {text}"}
        ],
        "max_tokens": 50
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            category = data.get("choices", [{}])[0].get("message", {}).get("content", "Другое").strip()
            logging.info(f"OpenAI определил категорию: {category}")
            return category
        logging.error("Ошибка при запросе OpenAI: %s", response.text)
        return "Другое"


def extract_problem_product(text_comment: str, products: str) -> str:
    """Определяет, какие продукты упоминаются в негативном отзыве."""
    product_list = [p.strip('" ') for p in products.strip("[]").split(", ")]
    text_words = set(text_comment.lower().split())  # Разделяем текст на слова

    matched_products = [
        p for p in product_list if any(word in text_words for word in p.lower().split())
    ]

    return json.dumps(matched_products, ensure_ascii=False) if matched_products else "[]"


@app.post("/analyze")
async def analyze_reviews(request: Request):
    reviews = await request.json()
    if not isinstance(reviews, list):
        raise HTTPException(status_code=400, detail="Некорректный формат данных")

    ensure_csv_exists()
    processed_reviews = []
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for review_data in reviews:
            review = Review(**review_data)
            review.category_comment = await analyze_text_with_openai(review.text_comment)
            if review.category_comment in ["Жалоба на блюдо", "Жалоба на просрочку в зале"]:
                review.problem_products = extract_problem_product(review.text_comment, review.products)
            writer.writerow([
                review.date_create, review.text_comment, review.guests_id, review.source_type, review.shop_name,
                review.source_description, review.vote, review.products, review.problem_products,
                review.category_comment
            ])
            processed_reviews.append(review.dict())

    return {"status": "success", "processed_reviews": processed_reviews}
