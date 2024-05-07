from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse_lazy

from blog.models import Category, Post


User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10
    template_name = 'blog/index.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    # def get_slug_field(self):
    #     return 'user__username'

    # def get_object(self):
    #     profile = get_object_or_404(User, username=self.kwargs['slug'])
    #     return 
    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     profile = get_object_or_404(User, username=self.kwargs['username'])
    #     context['profile'] = profile
    #     return context


# def index(request):
#     template = 'blog/index.html'
#     post_list = Post.published.select_related('category')[0:5]
#     context = {
#         'post_list': post_list
#     }
#     return render(request, template, context)


# def post_detail(request, pk):
#     template = 'blog/detail.html'
#     post = get_object_or_404(
#         Post.published.all(),
#         pk=pk
#     )
#     context = {
#         'post': post
#     }
#     return render(request, template, context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True,
            slug=category_slug
        )
    )
    post_list = category.posts(manager='published').all()
    template = 'blog/category.html'
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template, context)
