from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blogicum.settings import PAGE_COUNT

from blog.forms import CommentForm, PostForm, ProfileForm
from blog.models import Category, Comment, Post

User = get_user_model()


class OnlyUserMixin(UserPassesTestMixin):
    """Current user checking (to update profile e.g.)"""

    def test_func(self):
        """Check a user is the current user"""
        object = self.get_object()
        return object == self.request.user


class OnlyAuthorMixin(UserPassesTestMixin):
    """Authorship checking"""

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs.get('pk'))

    def test_func(self):
        """Check the author of object is the current user"""
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

    def get_queryset(self):
        self.category = get_object_or_404(Category.objects.filter(
            is_published=True,
            slug=self.kwargs.get('category_slug'))
        )
        page_obj = self.category.posts(manager='published').select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by(
            '-pub_date')
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
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
            kwargs={'pk': self.kwargs.get('pk')}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        context['form'] = PostForm(instance=instance)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    paginate_by = PAGE_COUNT
    template_name = 'blog/detail.html'

    def get_object(self):
        post_object = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        if post_object.author == self.request.user:
            return post_object
        return get_object_or_404(Post.published, pk=self.kwargs.get('pk'))

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
        self.post_obj = get_object_or_404(Post, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.post_obj.pk
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs.get('comment_id'))

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('pk')})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs.get('comment_id'))

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('pk')})


class ProfileDetailView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = PAGE_COUNT

    def get_queryset(self):
        self.profile = get_object_or_404(User,
                                         username=self.kwargs.get('username'))
        if self.request.user == self.profile:
            return self.profile.posts.select_related(
                'category', 'location').annotate(
                    comment_count=Count('comments')).order_by('-pub_date')
        return self.profile.posts(manager='published').select_related(
            'category', 'location').annotate(
                comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.profile
        return context


class ProfileUpdateView(OnlyUserMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.object
            }
        )
