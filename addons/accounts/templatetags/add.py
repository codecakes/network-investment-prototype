from django import template

register = template.Library()

@register.simple_tag
def sumit(a, *x): 
    return a+sum(x)