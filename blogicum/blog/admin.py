from django.contrib import admin

from blog.models import Category, Location, Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'pub_date',
        'category'
    )

    list_editable = (
        'is_published',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published'
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published'
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'created_at',
        'author'
    )
