from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)  # Поле для изображения
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:20]  # Возвращаем первые 20 символов содержимого

class Comment(models.Model):
	post = models.ForeignKey(Post, related_name='comments',
		on_delete=models.CASCADE)
	author = models.CharField(max_length=100)
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Comment by {self.author} on {self.post}'
		
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')  # Один пользователь может поставить лайк только один раз

