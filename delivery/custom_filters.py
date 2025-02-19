# delivery/templatetags/custom_filters.py

from django import template
import json

register = template.Library()

@register.filter
def json_parse(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value  # Return the original value if parsing fails
