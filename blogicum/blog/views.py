from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils import timezone

from django.urls import reverse_lazy, reverse

from blog.forms import PostForm, CommentForm, ProfileForm
from blog.models import Category, Post, Comment

User = get_user_model()
PAGE_COUNT = 10


class OnlyUserMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object == self.request.user


class OnlyAuthorMixin(UserPassesTestMixin):

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['pk'])

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    paginate_by = PAGE_COUNT
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.published.select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by(
            '-pub_date')


class CategoryPostListView(ListView):
    paginate_by = PAGE_COUNT
    template_name = 'blog/category.html'
    allow_empty = False

    def get_queryset(self):
        return Post.published.filter(
            category__slug=self.kwargs['category_slug']
        ).select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by(
            '-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.filter(
                is_published=True,
                slug=self.kwargs['category_slug']))
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     context = self.get_context_data(object=self.object)
    #     return self.render_to_response(context)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # instance = get_object_or_404(Post, self.kwargs['pk'])
    #     # context['form'] = PostForm(instance=instance)
    #     return context

    # def form_valid(self, form):
    #     return super().form_valid(form)

    # def get_form(self, form_class=PostForm):
    #     """Return an instance of the form to be used in this view."""
    #     if form_class is None:
    #         form_class = self.get_form_class()
    #     return form_class(**self.get_form_kwargs())

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    paginate_by = PAGE_COUNT
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.post_obj.pk
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['pk']})




@login_required
def delete_comment(request, pk, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=pk)
    return render(request, 'blog/create.html', context)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.get_related_posts()
        context['user'] = get_object_or_404(User, id=self.request.user.id)
        context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        context['page_obj'] = posts
        return context

    def get_related_posts(self):
        if self.request.user.id == self.object.id:
            queryset = self.object.posts.all().select_related(
                'category', 'location').annotate(
                    comment_count=Count('comments')).order_by('-pub_date')
        else:
            queryset = self.object.posts(manager='published').select_related(
                'category', 'location').annotate(
                    comment_count=Count('comments')).order_by('-pub_date')
        paginator = Paginator(queryset, PAGE_COUNT)
        page = self.request.GET.get('page')
        posts = paginator.get_page(page)
        return posts


class ProfileUpdateView(LoginRequiredMixin, OnlyUserMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': get_object_or_404(User, id=self.request.user.id)
            }
        )
