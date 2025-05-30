import json
from django import template

register = template.Library()

@register.filter
def get_from_json(json_string, key):
    """
    Парсит JSON-строку и возвращает значение по указанному ключу.
    """
    try:
        data = json.loads(json_string)
        return data.get(key, '')
    except (json.JSONDecodeError, TypeError):
        return ''


@register.filter
def get_dict_item(dictionary, key):
    return dictionary.get(key)