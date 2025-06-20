from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.constants import PAGINATE_BY
from blog.models import Post


def get_published_posts(queryset=None):
    if queryset is None:
        queryset = Post.objects
    now = timezone.now()
    return queryset.filter(
        is_published=True,
        pub_date__lte=now,
        category__is_published=True
    ).select_related(
        'author', 'location', 'category'
    ).annotate(
        comment_count=Count('comments')
    )


def get_paginator(queryset, request):
    paginator = Paginator(queryset, PAGINATE_BY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
