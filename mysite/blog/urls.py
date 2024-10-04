from django.urls import path
from .views import (
    home,
    register,
    login_view,
    logout_view,
    create_post,
    posts,
    edit_post,
    delete_post,
    post_detail,
    add_comment,
    AboutUsView,
    search_posts,
    feedback_view,
    recipe_list,
    create_recipe,
    receipts_view,  # Corrigido para incluir a view correta
)

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
    path('post/<int:post_id>/add_comment/', add_comment, name='add_comment'),
    path('about-us/', AboutUsView.as_view(), name='about-us'),
    path('search/', search_posts, name='search_posts'),
    path('feedback/', feedback_view, name='feedback'),
    path('receipts/<str:category>/', recipe_list, name='recipe-list'),
    path('receipts/create/', create_recipe, name='recipe_form'),  # Melhorar para uma única URL para criar receitas
    path('receipts/', receipts_view, name='receipts'),
]
