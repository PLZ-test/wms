from django import template

register = template.Library()

@register.filter(name='get_attribute')
def get_attribute(obj, key):
    return getattr(obj, key, "")