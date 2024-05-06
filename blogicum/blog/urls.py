from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/create', views.PostCreateView.as_view(), name='create_post'),
    path('profile/<slug:username>/', views.ProfileDetailView.as_view(), name='profile'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
