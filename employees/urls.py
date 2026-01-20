from django.urls import path
from .views import *

urlpatterns = [
    path('<int:employee_id>/enroll-face/', enroll_face_view, name='enroll_face'),
    path('<int:employee_id>/upload-face/', upload_face_view, name='upload_face'),    
    #path('kiosk/', kiosk_view, name='kiosk'),
    path("activate-kiosk/", kiosk_activate_device, name="kiosk_activate_device"),
    path("kiosk/", kiosk_activate_page, name="kiosk_page"),

     # 3) Página de cámara real
    path("kiosk-camera/", kiosk_camera_page, name="kiosk_camera_page"),
    # 4) Endpoint de reconocimiento    
    #path("activate-kiosk/", activate_kiosk, name="activate_kiosk"),
    path("recognize-face/", recognize_face_view, name="recognize_face"),
    path("confirm-attendance/", confirm_attendance_view, name="confirm_attendance"),


]

from django.urls import path
from .views import employee_list_view, employee_create_view,device_list_view, device_create_view


urlpatterns += [
    path("dashboard/employees/", employee_list_view, name="employee_list"),
    path("dashboard/employees/new/", employee_create_view, name="employee_create"),
    path("dashboard/devices/", device_list_view, name="device_list"),
    path("dashboard/devices/new/", device_create_view, name="device_create"),
]

