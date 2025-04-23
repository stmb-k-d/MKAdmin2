from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Фильтр для получения значения по ключу из словаря в шаблоне.
    Использование: {{ dict|get_item:key }}
    """
    return dictionary.get(key, None) 