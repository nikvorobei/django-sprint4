from django.urls import path
from . import views
from .views import PostCreateView, PostDetailView, PostDeleteView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

app_name = 'blog'

urlpatterns = [
    # Главная страница (список постов)
    path('', views.PostListView.as_view(), name='index'),

    # Детали поста (используем PostDetailView вместо post_detail функции)
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),

    # Категории (если у вас есть CategoryView в views.py)
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),

    # Создание поста
    path('posts/create/', PostCreateView.as_view(), name='create_post'),

    # Редактирование поста
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(), name='post_edit'),

    # Удаление поста
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='delete_post'),

    # Комментарии
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', 
         views.CommentUpdateView.as_view(), 
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', 
         views.CommentDeleteView.as_view(), 
         name='delete_comment'),

    path('edit_profile/',
         views.ProfileUpdateView.as_view(template_name='blog/create.html'), name='edit_profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),

    # Регистрация
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('profile/change-password/',
         PasswordChangeView.as_view(
             template_name='blog/change_password.html',
             success_url=reverse_lazy('blog:index')
         ),
         name='change_password'),
]
