import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Настройка ключа (и прокси, если он указан в .env)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

teacher_prompt = (
    "Ты — строгий, но справедливый школьный учитель, который готовит учеников к экзаменам. "
    "Объясняй теорию так, словно ведешь живой урок: понятно, развернуто и с примерами. "
    "Строго запрещено использовать любые эмодзи. Бери информацию из достоверных источников, "
    "таких как ФИПИ, Решу ЕГЭ, Фоксфорд, Турбо ЕГЭ."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=teacher_prompt,
    tools="google_search_retrieval"
)

async def get_teacher_answer(question: str) -> str:
    try:
        response = await model.generate_content_async(question)
        return response.text
    except Exception as e:
        return f"Произошла ошибка при поиске информации: {e}"
