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

User = get_user_model()

class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'pk'

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
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})

class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')  # Редирект после удаления

    def get(self, request, *args, **kwargs):
        """Пропускаем GET-запрос и сразу удаляем (только через POST)."""
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Добавляем сообщение об успешном удалении."""
        messages.success(request, 'Пост успешно удалён!')
        return super().delete(request, *args, **kwargs)

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post__id=self.kwargs['post_id']
        )

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=comment.post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post__id=self.kwargs['post_id']
        )

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=comment.post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})

class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.all().order_by('-pub_date')
        return context

class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


def category_posts(request, category_slug):
    """Показывает все посты в конкретной категории."""
    category = get_object_or_404(Category, slug=category_slug)
    post_list = Post.objects.filter(category=category).order_by('-pub_date')
    
    # Добавляем пагинацию (по аналогии с PostListView)
    paginator = Paginator(post_list, 10)  # 10 постов на страницу
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

@login_required
def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
    author=profile,
).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('created_at')
    form = CommentForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', pk=pk)
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)