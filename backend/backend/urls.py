from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from employees.views import EmployeeTokenObtainPairView
from attendance.views import MobileDashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', EmployeeTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('employees.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/leaves/', include('leaves.urls')),
    path("api/meetings/", include("meetings.urls")),
    path("api/assistant/", include("assistantbot.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/analytics/", include("analytics.urls")),
    path('api/dashboard/', MobileDashboardView.as_view(), name='mobile-dashboard'),

    # API documentation
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
