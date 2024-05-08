from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
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
    # queryset = Post.objects.prefetch_related('comments').select_related('author')
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


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


# class CommentCreateView(LoginRequiredMixin, CreateView):
#     object = None
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/comment.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.object = get_object_or_404(Post, pk=kwargs['pk'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.post = self.kwargs.get(pk)
#         return super().form_valid(form)

#     def get_success_url(self):
#         # pk = self.kwargs['pk']
#         return reverse('blog:post_detail', kwargs={'pk': self.object.pk})



@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', pk)
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None,
        instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=pk)
    template = 'blog/create.html'
    context = {'form': form,
               'comment': comment}
    return render(request, template, context)


@login_required
def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, comment_id)
    comment.delete()
    return render(request, 'blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.object = self.object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post:detail', kwargs={'pk': self.object.pk})


"""POST DONE"""


class ProfileDetailView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'blog/profile.html'
    success_url = reverse_lazy('blog:index')

    # def get_context_data(self, **kwargs):
    #     # users = User.objects.all()
    #     context = super().get_context_data(**kwargs)
    #     page_user = get_object_or_404(User, username=self.kwargs['username'])
    #     context['profile'] = page_user
    #     return context

    # def get_object(self):
    #     return get_object_or_404(User, username=self.kwargs['username'])
    def get_object(self):
        return self.request.user
    
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
