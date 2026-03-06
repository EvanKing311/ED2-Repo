# Create this file: MatlabApp/templatetags/experiment_filters.py

from django import template

register = template.Library()

@register.filter(name='replace_underscores')
def replace_underscores(value):
    """
    Replace underscores with spaces in parameter names
    Example: 'pendulum_mass' -> 'Pendulum Mass'
    """
    return str(value).replace('_', ' ')


@register.filter(name='format_param_name')
def format_param_name(value):
    """
    Format parameter names nicely
    Example: 'cart_friction' -> 'Cart Friction'
    """
    # Replace underscores with spaces
    formatted = str(value).replace('_', ' ')
    
    # Capitalize each word
    formatted = formatted.title()
    
    # Special cases
    replacements = {
        'Pi': 'π',
        'Kg': 'kg',
        'M/S²': 'm/s²',
    }
    
    for old, new in replacements.items():
        formatted = formatted.replace(old, new)
    
    return formatted