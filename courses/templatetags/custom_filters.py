from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a value in a dictionary by key
    Usage: {{ dict|lookup:key }}
    """
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    elif dictionary and hasattr(dictionary, '__getitem__'):
        try:
            return dictionary[key]
        except (KeyError, TypeError):
            return None
    return None

@register.filter
def get_item(dictionary, key):
    """
    Alternative filter for dictionary lookup
    """
    return dictionary.get(key) if dictionary else None