from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/create', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('profile/<slug:username>/', views.ProfileDetailView.as_view(), name='profile'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
