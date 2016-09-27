from django import template

from template_utils import filters

register = template.Library()
for name,filter_func in list(filters.items()):
    register.filter(name, filter_func)