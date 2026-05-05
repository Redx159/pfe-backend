from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet
from .views import (
    LoginView,
    RegisterView,
    ProfileView,
    RefreshTokenView,
    LogoutView,
    ApproveUserView,
    EmployeeListView,
)

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employees")
router.register("departments", DepartmentViewSet, basename="departments")

urlpatterns = [
    path("", include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('approve/<int:pk>/', ApproveUserView.as_view(), name='approve_user'),
    path('employees/', EmployeeListView.as_view(), name='employees'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
