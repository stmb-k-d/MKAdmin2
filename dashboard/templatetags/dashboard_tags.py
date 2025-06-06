from django import template
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Фильтр для получения значения по ключу из словаря в шаблоне.
    Использование: {{ dict|get_item:key }}
    """
    if isinstance(dictionary, str):
        dictionary = json.loads(dictionary)
    return dictionary.get(key, '') 