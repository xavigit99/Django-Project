from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PostForm, FeedbackForm
from .models import Post, Comment, FavouritePost, Rating
from django.views.generic import TemplateView

def home(request):
    return render(request, 'blog/home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "O nome de usuário já está em uso.")
            return redirect('register')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        return redirect('home')
    
    return render(request, 'blog/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Credenciais inválidas.")
            return redirect('login')
    
    return render(request, 'blog/login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post criado com sucesso!")
            return redirect('posts')
    else:
        form = PostForm()
    
    return render(request, 'blog/new_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar este post.")
        return redirect('posts')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post editado com sucesso!")
            return redirect('posts')
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form})

@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para excluir este post.")
        return redirect('posts')
    
    if request.method == 'POST':
        post.delete()
        messages.success(request)
        return redirect('posts')

    return render(request, 'blog/delete_post.html', {'post': post})

def posts(request):
    all_posts = Post.objects.all()
    return render(request, 'blog/posts.html', {'posts': all_posts})

@login_required(login_url='login')
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    
    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_content = request.POST['comment']
            Comment.objects.create(post=post, author=request.user, content=comment_content)
            messages.success(request, "Comentário adicionado com sucesso!")
            return redirect('post_detail', post_id=post.id)
        
        elif 'rating' in request.POST:
            rating = request.POST['rating']
            if rating == 'positive':
                messages.success(request, "Post adicionado aos Favoritos!")
                return redirect('favourite-posts')

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
    })

@login_required(login_url='login')
def favourite_posts(request):
    favourite_posts = FavouritePost.objects.filter(user=request.user).select_related('post')
    return render(request, 'blog/favourite_posts.html', {'favorite_posts': favourite_posts})

@login_required(login_url='login')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content') 
        if content: 
            Comment.objects.create(post=post, author=request.user, content=content)
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment content cannot be empty.')
    return redirect('posts')

@login_required(login_url='login')
def rate_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        value = int(request.POST['value']) 
        Rating.objects.update_or_create(
            post=post,
            user=request.user,
            defaults={'value': value}
        )
        messages.success(request, "Avaliação adicionada com sucesso!")
        return redirect('post_detail', post_id=post.id)

class AboutUsView(TemplateView):
    template_name = 'blog/about_us.html'

@login_required(login_url='login')
def search_posts(request):
    query = request.GET.get('query')
    posts = Post.objects.filter(title__icontains=query) 
    return render(request, 'blog/posts.html', {'posts': posts, 'query': query})

@login_required(login_url='login')
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'feedback.html', {'form': FeedbackForm(), 'success': True})
    else:
        form = FeedbackForm()
    return render(request, 'blog/feedback.html', {'form': form})