from django.core.cache import cache
from datetime import datetime, timedelta
from django.conf import settings
import requests


def get_iam_token():
    """ Получает IAM-токен из кэша или делает запрос для нового токена. """
    iam_token = cache.get('yandex_iam_token')
    expires_at = cache.get('yandex_iam_token_expires_at')

    # print(iam_token, expires_at)
    if iam_token and datetime.utcnow() < expires_at:
        return iam_token

    oauth_token = settings.YANDEX_OAUTH_TOKEN
    response = requests.post(
        'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        json={"yandexPassportOauthToken": oauth_token}
    )
    print("response", response.json())

    response.raise_for_status()
    data = response.json()
    iam_token = data.get('iamToken')
    expires_at = datetime.utcnow() + timedelta(hours=1)
    cache.set('yandex_iam_token', iam_token, timeout=3600)
    cache.set('yandex_iam_token_expires_at', expires_at, timeout=3600)
    return iam_token


def query_yandex_gpt(iam_token, folder_id, user_text) -> dict:
    """ Отправляет запрос к Yandex GPT API и возвращает ответ. """
    URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    data = {
        "modelUri": f"gpt://{folder_id}/llama",
        "completionOptions": {"temperature": 0.3, "maxTokens": 3000},
        "messages": [
            {"role": "system", "text": """Я планирую путешествие и хочу получить расписание тайм-менеджмента на основе моих предпочтений. 
### Требования:
1. Тайм-менеджмент должен быть абстрактным, без привязки к конкретным местам. Используйте теги активности, такие как:
   Теги для Еды: Пекарня, Кондитерская, Кафе, Пиццерия, Грузинская кухня, Армянская кухня, Узбекская кухня, Итальянская кухня, Вкусно поесть
   Теги: Бары, Наука, Выставки, Архитектура, Музыка, Необычное место, Искусство, Экстрим, Достопримечательности, Искусство, Музеи, Гулять, Инстаграмные места, Экскурсии, Вкусно поест, Выставки
2. В КАЖДОМ ДНЕ ОБЯЗАТЕЛЬНО ДОЛЖНО БЫТЬ 5-6 АКТИВНОСТЕЙ
3. Структура данных в виде JSON (пример):
Представьте результат в форме объекта JSON, где каждый день представлен как ключ (например, '1 день', '2 день'), а значения — это массивы тайм-слотов. Каждый тайм-слот должен содержать:
- time: временной интервал в формате \"ЧЧ:ММ-ЧЧ:ММ\".
- activity: название активности.
- tags: категории активности.
Если ты подбираешь несколько тегов, в списке tags на первом месте должен быть самый важный тег, затем второстепенный.
Активности должны быть максимально нейтральными, никаких специфичных активностей, только те что следуют из тегов.
Но благодаря предпочтениями они могут менее нейтральными
{
    "1 день":[ 
       {
        "time": "08:00-09:00",
        "activity": "Завтрак", 
        "tags": ["Кафе"]},
       {, 
       ...
       ],
    "2 день":[ ...
Нужны только данные без вводных фраз и объяснений. Не используйте разметку Markdown!
"""},
            {"role": "user", "text": f"{user_text}"},
        ]
    }
    response = requests.post(
        URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {iam_token}"
        },
        json=data,
    ).json()

    return response
