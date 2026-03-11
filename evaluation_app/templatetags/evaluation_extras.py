from django import template

register = template.Library()

@register.filter
def split_fields(value, arg):
    """
    Converts a comma-separated string of attribute names into a list.
    Used to iterate over the Ev_Q_ fields in the template.
    """
    return arg.split(',')

@register.filter
def get_attr(obj, attr_name):
    """
    Gets an attribute from an object by string name.
    """
    return getattr(obj, attr_name, None)

@register.filter
def div(value, arg):
    """
    Divides the value by the argument.
    """
    try:
        return value / arg
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def add(value, arg):
    """
    Adds the value and the argument.
    """
    try:
        return value + arg
    except (ValueError, TypeError):
        return None
