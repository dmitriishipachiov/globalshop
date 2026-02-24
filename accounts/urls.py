from django.urls import path
from .views import RegisterView, LoginView, LogoutView, AddressView, UserView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('address/', AddressView.as_view(), name='address'),
    path('profile/', UserView.as_view(), name='profile'),
]
