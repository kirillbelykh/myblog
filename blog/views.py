from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm, UserProfileForm, CustomUserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.http import JsonResponse
from .models import Like
from django.views.decorators.http import require_POST

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

@login_required
def profile_setup(request):
    user_profile = request.user.userprofile  # Получаем профиль пользователя
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Перенаправляем на страницу профиля после сохранения
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'registration/profile_setup.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Убедитесь, что устанавливается автор
            post.save()
            return redirect('post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_create.html', {'form': form, 'post': post, 'page_title': 'Редактирование поста'})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Устанавливаем автора поста
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_create.html', {'form': form, 'page_title': 'Создание поста'})
    
def post_delete(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if post.author != request.user:
		return redirect('post_list')

	if request.method == 'POST':
		post.delete()
		return redirect('post_list')

	return render(request, 'blog/post_delete_confirm.html', {'post': post})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически логиним пользователя
            return redirect('profile_setup')  # Перенаправляем на страницу заполнения профиля
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    posts = Post.objects.filter(author=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'blog/profile.html', {
        'posts': posts,
        'form': form,
        'user_profile': user_profile,
    })

def post_list(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(content__icontains=query)
    else:
        posts = Post.objects.all().order_by('-created_at')

    # Получаем количество лайков и комментариев для каждого поста
    for post in posts:
        post.likes_count = post.like_set.count()  # Количество лайков
        post.comments_count = post.comments.count()  # Количество комментариев

    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()  # Получаем все комментарии к посту

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user  # Сохраняем текущего пользователя как автора комментария
            comment.save()
            return redirect('post_detail', pk=post.pk)  # Перенаправляем на страницу поста

    else:
        form = CommentForm()  # Если это не POST, создаем пустую форму

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

@require_POST
def like_post(request, post_id):
    if request.user.is_authenticated:
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()  # Удалить лайк, если он уже существует

        return JsonResponse({'success': True, 'likes_count': post.like_set.count()})

    return JsonResponse({'success': False}, status=400)