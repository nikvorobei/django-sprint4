from django.contrib.auth.views import PasswordChangeView
from django.urls import path, reverse_lazy

from . import views
from .views import PostCreateView, PostDetailView, PostDeleteView

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),

    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),

    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),

    path('posts/create/', PostCreateView.as_view(), name='create_post'),

    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(),
         name='delete_post'),

    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),

    path('edit_profile/',
         views.ProfileUpdateView.as_view(template_name='blog/create.html'),
         name='edit_profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),

    path('registration/', views.RegistrationView.as_view(),
         name='registration'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('profile/change-password/',
         PasswordChangeView.as_view(
             template_name='blog/change_password.html',
             success_url=reverse_lazy('blog:index')
         ),
         name='change_password'),
]
