from django import template

register = template.Library()


@register.simple_tag
def querystring_without_page(get_params):
    """'page' parametrisiz querystring qaytaradi (pagination havolalari uchun)."""
    params = get_params.copy()
    params.pop('page', None)
    return params.urlencode()


@register.filter
def money(value):
    """Summani o'qishga qulay qiladi: har uch xonadan keyin bo'sh joy (masalan 4500000 -> 4 500 000)."""
    try:
        value = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    return f'{value:,}'.replace(',', ' ')
