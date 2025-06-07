from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'text': forms.Textarea(attrs={'rows': 5}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
