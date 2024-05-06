from django.shortcuts import get_object_or_404, render

from blog.models import Category, Post


def index(request):
    template = 'blog/index.html'
    post_list = Post.published.select_related('category')[0:5]
    context = {
        'post_list': post_list
    }
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.published.all(),
        pk=pk
    )
    context = {
        'post': post
    }
    return render(request, template, context)


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
