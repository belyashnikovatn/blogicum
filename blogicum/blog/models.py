from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Location(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места',
        help_text='Напишите название локации')
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
        help_text='Дата и время добавления, автоматически'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(max_length=256,
                             verbose_name='Заголовок',
                             help_text='Напишите заголовок категории')
    description = models.TextField(verbose_name='Описание',
                                   help_text='Напишите описание категории')
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены '
                   'символы латиницы, цифры, дефис и подчёркивание.')
    )
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено',
        help_text='Дата и время добавления, автоматически'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class PublishedManager(models.Manager):
    """Manager for published posts only."""

    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )


class Post(models.Model):
    title = models.CharField(max_length=256,
                             verbose_name='Заголовок',
                             help_text='Напишите заголовок публикации')
    text = models.TextField(verbose_name='Текст',
                            help_text='Напишите текст публикации')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем '
                   '— можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
        help_text='Выберите автора публикации'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posts',
        verbose_name='Местоположение',
        help_text='Выберите место публикации'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория',
        help_text='Выберите категорию публикации'
    )
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено',
        help_text='Дата и время добавления, автоматически'
    )
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='posts_images',
                              blank=True,
                              help_text='Выберите изображение')

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text=('Напишите комментарий, и люди узнают ваше мнение')

    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый пост',
        help_text='К этой публикации вы оставляете комментарий'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
        help_text='Дата и время добавления, автоматически'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор поста',
        help_text='Выберите автора комментария',
        related_name='comments')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
