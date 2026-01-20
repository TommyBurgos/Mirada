from django.urls import path
from .views import kiosk_view, dashboard_view, attendance_list_view, attendance_policy_view, attendance_export_view

urlpatterns = [
    path('kiosk/', kiosk_view, name='kiosk'),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/attendance/", attendance_list_view, name="attendance_list"),
    path("dashboard/settings/attendance/", attendance_policy_view, name="attendance_policy"),
]

urlpatterns += [
    path(
        "dashboard/attendance/export/",
        attendance_export_view,
        name="attendance_export"
    ),
]

