from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView, ListView
)
from django.core.paginator import Paginator
from .models import Post, Comment, Category
from django.contrib.auth.forms import UserCreationForm
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone

User = get_user_model()

class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).select_related('author', 'location', 'category').annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all().order_by('created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        # Для неавторизованных — редирект на /posts/<post_id>/
        if not request.user.is_authenticated:
            post_id = kwargs.get('pk')
            return redirect(f'/posts/{post_id}/')  # Явный редирект на нужный URL
        
        # Для авторизованных, но не авторов — 403 Forbidden
        self.object = self.get_object()
        if self.object.author != request.user:
            return HttpResponseForbidden("Нельзя редактировать чужой пост")
        
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'  # Используем шаблон деталей поста
    pk_url_kwarg = 'pk'
    context_object_name = 'post'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_delete_confirmation'] = True  # Флаг для показа подтверждения
        return context

    def get_success_url(self):
        return reverse('blog:index')

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['pk']})

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post__id=self.kwargs['pk']
        )

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=comment.post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['pk']})

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'  # Используем шаблон деталей поста
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=comment.post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object.post
        context['post'] = post
        context['show_comment_delete_confirmation'] = True  # Флаг для подтверждения
        context['comment_to_delete'] = self.object  # Комментарий для удаления
        return context

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.post.pk})

class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_posts = self.object.posts.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        
        paginator = Paginator(user_posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        return context

class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


def category_posts(request, category_slug):
    """Показывает только опубликованные посты в опубликованной категории."""
    # Проверяем, что категория существует и опубликована
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True  # ← Важно: только опубликованные категории
    )

    # Фильтруем только опубликованные посты с корректной датой
    post_list = Post.objects.filter(
        category=category,
        is_published=True,  # ← Только опубликованные посты
        pub_date__lte=timezone.now()  # ← Посты с датой <= текущей
    ).order_by('-pub_date')

    # Пагинация
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'blog/create.html'  # Используем существующий шаблон
    

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактирование профиля'
        return context
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})

