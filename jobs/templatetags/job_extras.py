"""
Custom template filters for jobs app
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    Usage: {{ mydict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def multiply(value, arg):
    """
    Multiply value by arg.
    Usage: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage_color(value):
    """
    Return a color based on percentage value.
    Usage: {{ value|percentage_color }}
    """
    try:
        val = int(value)
        if val >= 70:
            return '#10b981'  # Green
        elif val >= 50:
            return '#f59e0b'  # Orange
        else:
            return '#ef4444'  # Red
    except (ValueError, TypeError):
        return '#64748b'  # Gray
