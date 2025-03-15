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


async def analyze_text_with_openai(text: str) -> List[str]:
    if not text.strip():
        return ["Без категории"]

    logging.info(f"Отправка запроса в OpenAI для анализа текста: {text}")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system",
             "content": "Ты эксперт по анализу отзывов. Тебе нужно выбрать одну или несколько категорий отзыва из списка, строго следуя значению текста."},
            {"role": "user",
             "content": f"Проанализируй текст отзыва и выбери одну или несколько наиболее подходящих категорий из списка: {', '.join(CATEGORY_OPTIONS)}. Если отзыв подходит под несколько категорий, укажи их все, разделяя запятой. Если ни одна из категорий не подходит, напиши 'Другое'. Ответ должен содержать только категории без дополнительных комментариев. \n\nТекст отзыва: {text}"}
        ],
        "max_tokens": 100
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            category_text = data.get("choices", [{}])[0].get("message", {}).get("content", "Другое").strip()
            categories = [c.strip() for c in category_text.split(",") if c.strip() in CATEGORY_OPTIONS]
            logging.info(f"OpenAI определил категории: {categories}")
            return categories if categories else ["Другое"]
        logging.error("Ошибка при запросе OpenAI: %s", response.text)
        return ["Другое"]


def extract_problem_product(text_comment: str, products: str) -> str:
    """Определяет, какие продукты упоминаются в негативном отзыве."""
    if not text_comment.strip():
        return "[]"

    product_list = [p.strip('" ') for p in products.strip("[]").split(", ") if p]
    text_words = set(text_comment.lower().split())

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
            if not review_data.get("text_comment", "").strip():
                logging.warning("Пропущен пустой отзыв")
                continue

            review = Review(**review_data)
            review.category_comment = ", ".join(await analyze_text_with_openai(review.text_comment))

            if any(cat in review.category_comment for cat in ["Жалоба на блюдо", "Жалоба на просрочку в зале"]):
                review.problem_products = extract_problem_product(review.text_comment, review.products)

            writer.writerow([
                review.date_create, review.text_comment, review.guests_id, review.source_type, review.shop_name,
                review.source_description, review.vote, review.products, review.problem_products,
                review.category_comment
            ])
            processed_reviews.append(review.dict())

    return {"status": "success", "processed_reviews": processed_reviews}
