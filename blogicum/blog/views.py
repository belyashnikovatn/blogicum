from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.forms import CommentForm, PostForm, ProfileForm
from blog.models import Category, Comment, Post

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

    def get_queryset(self):
        category = get_object_or_404(Category.objects.filter(
            is_published=True,
            slug=self.kwargs['category_slug'])
        )
        page_obj = category.posts(manager='published').all().select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by(
            '-pub_date')
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category.objects.filter(
            is_published=True,
            slug=self.kwargs['category_slug'])
        )
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
            kwargs={'username': self.request.user.username}
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['form'] = PostForm(instance=instance)
        # context['post'] = instance
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
        post_object = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post_object.author == self.request.user:
            return post_object
        else:
            return get_object_or_404(Post.published, pk=self.kwargs['pk'])

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
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']})


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.get_related_posts()
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
                'username': get_object_or_404(User, id=self.request.user.id)
            }
        )
