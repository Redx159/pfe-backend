from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardStats.as_view(), name='analytics-dashboard'),
    path('report/', views.GenerateReport.as_view(), name='analytics-report'),
]
