from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse

from blog.forms import PostForm, CommentForm
from blog.models import Category, Post, Comment


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
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/detail.html'
    success_url = reverse_lazy('blog:index')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/detail.html'
    success_url = reverse_lazy('blog:index')


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    # success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post:detail', kwargs={'pk': self.post.pk})


"""POST DONE"""


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'

    # def get_context_data(self, **kwargs):
    #     # users = User.objects.all()
    #     context = super().get_context_data(**kwargs)
    #     page_user = get_object_or_404(User, username=self.kwargs['username'])
    #     context['profile'] = page_user
    #     return context

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
    #     return context

    # def get_object(self):
    #     profile = get_object_or_404(User, username=self.kwargs['username'])
    #     context['profile'] = (self.object.User.all('author'))
    #     return context 
    

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
