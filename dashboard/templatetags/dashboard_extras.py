from django import template

register = template.Library()


@register.filter
def widget_type(field):
    """Forma maydonining widget klass nomini kichik harflarda qaytaradi.

    Shablonda maydon turini aniqlash uchun: checkboxinput, textarea, clearablefileinput ...
    """
    try:
        return field.field.widget.__class__.__name__.lower()
    except AttributeError:
        return ''


@register.filter
def is_checkbox(field):
    return widget_type(field) == 'checkboxinput'


@register.filter
def is_wide(field):
    """Textarea va fayl maydonlari to'liq kenglikda ko'rsatiladi."""
    return widget_type(field) in ('textarea', 'clearablefileinput', 'fileinput')
