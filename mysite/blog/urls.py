from django.urls import path
from .views import home, register, login_view, logout_view, create_post, posts, edit_post, delete_post, post_detail, favourite_posts, add_comment, rate_post

urlpatterns = [
    path('', home, name='home'), 
    path('register/', register, name='register'),
    path('login/', login_view, name='login'), 
    path('logout/', logout_view, name='logout'), 
    path('posts/', posts, name='posts'),
    path('new-post/', create_post, name='new-post'),
    path('post/edit/<int:post_id>/', edit_post, name='edit_post'),
    path('post/delete/<int:post_id>/', delete_post, name='delete_post'),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path('favourite-posts/', favourite_posts, name='favourite-posts'),
    path('post/<int:post_id>/add_comment/', add_comment, name='add_comment'),
    path('post/<int:post_id>/rate/', rate_post, name='rate_post'),
]
