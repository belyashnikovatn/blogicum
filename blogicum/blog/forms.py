from django import forms
from django.contrib.auth import get_user_model

from blog.models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image',)
        widgets = {
            'pub_date': forms.DateInput(
                format='%Y-%m-%d %H:%M:%S',
                attrs={
                    # 'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),
            'text': forms.Textarea(attrs={'cols': '22', 'rows': '5'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)
