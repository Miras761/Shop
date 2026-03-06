from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, UserDetailView, UpdateAvatarView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/avatar/', UpdateAvatarView.as_view(), name='update-avatar'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
