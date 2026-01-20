from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from employees.views import EmployeeViewSet
from attendance.views import DeviceViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'devices', DeviceViewSet, basename='devices')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('attendance.urls')),
    path('employees/', include('employees.urls')),
    path('accounts/', include('accounts.urls')),

]

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
