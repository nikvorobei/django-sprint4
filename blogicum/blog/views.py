from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .constants import POSTS_PER_PAGE
from .models import Category, Post


def get_published_posts():
    return Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related('category', 'location', 'author')


def index(request):
    post_list = get_published_posts()[:POSTS_PER_PAGE]
    return render(request, 'blog/index.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(get_published_posts(), pk=post_id)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    """Посты категории (только если категория опубликована)."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_published_posts().filter(category=category)

    return render(request, 'blog/category.html', {
        'category': category,
        'post_list': post_list
    })
