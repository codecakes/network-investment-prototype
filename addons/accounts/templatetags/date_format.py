from django import template

register = template.Library()

@register.simple_tag
def format_date(dt_time): 
    return dt_time.strpfmt("%Y-%m-%d:%H-%m")