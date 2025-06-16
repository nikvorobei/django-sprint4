from django.shortcuts import redirect


class AuthorPermissionMixin:
    """Миксин для проверки авторства."""

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.get_object().pk)
        return super().dispatch(request, *args, **kwargs)
