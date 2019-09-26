from django import template
from django.db.models import Q

from ..models import *

register = template.Library()

@register.simple_tag
def get_recent_posts(num = 5):
    return Post.objects.all().order_by('-created_time')[:num]

@register.simple_tag
def archives():
    return Post.objects.dates('created_time', 'month', order= 'DESC')

@register.simple_tag
def get_categories():
    return  Category.objects.all()

@register.simple_tag
def get_the_most_category():
    return Category.objects.filter(Q(name__icontains='django') | Q (name__icontains= 'Python')| Q(name__icontains= 'Linux'))