from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog import views
from blog.views import PostCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', views.RegistrationView.as_view(), name='registration'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(), name='delete_comment'),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls')),
]

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)