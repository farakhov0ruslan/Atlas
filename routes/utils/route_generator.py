import json
from random import Random

from routes.utils import yandex
from django.conf import settings
from routes.models import Place


def generate_route(user_preferences: str) -> dict:
    """
     Генерирует маршрут с помощью Yandex GPT API на основе предпочтений пользователя.

     Выходные данные
     {
      "1 день": [
        {"time": "08:00-09:00", "activity": "Завтрак", "place": Place(...)},
        ...
      ],
      "2 день": [
        ...
      ]
    }
    """
    iam_token = yandex.get_iam_token()
    folder_id = settings.FOLDER_ID
    print(user_preferences)
    user_text = f""" Учтите мои предпочтения: {user_preferences}"""
    response = yandex.query_yandex_gpt(iam_token, folder_id, user_text)
    responce_route_str = response.get('result', {})['alternatives'][0]['message']['text']

    print(responce_route_str)
    route_dict = json.loads(responce_route_str)

    using_place = set()
    for day, activities in route_dict.items():
        for activity in activities:
            tags = activity.get("tags", [])

            # Если у активности есть тэги, пытаемся подобрать place
            if tags:
                main_tag = tags[0]

                # Найдём место, соответствующее этому тегу.
                # Предполагается, что модель Place имеет связанный ManyToMany 'tags' с полем 'name'.
                matched_places = Place.objects.filter(category__name=main_tag)
                if matched_places.exists():
                    i = 0
                    place = matched_places[0]
                    while (True):
                        if i > 15 or place.id not in using_place:
                            break
                        rand_ind = Random().randint(0, len(matched_places) - 1)
                        place = matched_places[rand_ind]
                        i += 1
                    # Заменяем 'tags' на 'place'
                    activity.pop("tags", None)
                    activity["place_id"] = place.id
                    using_place.add(place.id)
                else:
                    # Если не нашли место по тегу, можно либо оставить как есть, либо поставить заглушку
                    activity.pop("tags", None)
                    activity["place_id"] = None
            else:
                # Нет тегов - значит нет данных о месте
                # можно оставить без changes или например activity["place"] = None
                activity["place_id"] = None
                activity.pop("tags", None)

        # В итоге route_dict теперь имеет поле "place" вместо "tags".

    counter = 1
    for day, activities in route_dict.items():
        for activity in activities:
            activity["id"] = counter
            counter += 1
    return route_dict
