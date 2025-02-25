from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query_string(context, key, value):
    """
    Создает строку запроса, сохраняя все текущие параметры GET и заменяя указанный ключ на новое значение.
    """
    request = context['request']
    query_dict = request.GET.copy()  # Создаем копию текущих параметров запроса
    query_dict[key] = value  # Устанавливаем новое значение для указанного ключа
    return query_dict.urlencode()  # Преобразуем в строку запроса (например, "search=test&status=1&page=2")