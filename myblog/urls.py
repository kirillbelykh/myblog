from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from blog import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]
