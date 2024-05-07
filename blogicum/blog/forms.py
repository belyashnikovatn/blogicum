from django import forms

from blog.models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }
