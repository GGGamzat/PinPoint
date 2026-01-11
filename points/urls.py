from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, LogoutView, PointViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'points', PointViewSet, basename='point')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/', include(router.urls)),
]