from rest_framework.viewsets import ModelViewSet
from .models import Employee
from .serializers import EmployeeSerializer

from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Employee, EmployeeFace

from django.core.files.base import ContentFile
from .utils.face_detection import detect_and_crop_face

from .utils.face_embedding import generate_embedding

import io

import numpy as np

from .utils.face_embedding import generate_embedding, l2_normalize, cosine_similarity
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from datetime import timedelta
from attendance.models import Attendance, Device

from .utils.face_embedding import generate_embedding, l2_normalize


class EmployeeViewSet(ModelViewSet):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.filter(company=self.request.user.company)



def enroll_face_view(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'employees/enroll_face.html', {'employee': employee})

from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def upload_face_view(request, employee_id):
    print("=== upload_face_view ===")
    print("METHOD:", request.method)
    print("CONTENT_TYPE:", request.content_type)
    print("FILES:", request.FILES)
    print("FILES KEYS:", list(request.FILES.keys()))
    print("POST:", request.POST)
    logger.info("📸 Inicio upload_face_view")

    if request.method != "POST":
        logger.warning("❌ Método no permitido")
        return JsonResponse({"error": "Método no permitido"}, status=405)

    if not request.FILES.get("image"):
        logger.warning("❌ No se recibió imagen")
        return JsonResponse({"error": "No se recibió imagen"}, status=400)

    try:
        # 1️⃣ Employee
        employee = get_object_or_404(Employee, id=employee_id)
        logger.info(f"👤 Employee OK id={employee.id}")

        # 2️⃣ Imagen
        image_file = request.FILES["image"]
        logger.info(f"🖼 Imagen recibida: {image_file.name}")

        image_bytes = image_file.read()

        # 3️⃣ Embedding
        logger.info("🧠 Generando embedding…")
        emb = generate_embedding(image_bytes, from_bytes=True)

        if emb is None:
            logger.warning("❌ No se detectó rostro válido")
            return JsonResponse(
                {"error": "No se detectó un rostro válido"},
                status=400
            )

        emb_norm = l2_normalize(emb)
        if emb_norm is None:
            logger.warning("❌ Embedding inválido")
            return JsonResponse(
                {"error": "Embedding inválido"},
                status=400
            )

        logger.info("✅ Embedding generado correctamente")

        # ⚠️ Rebobinar archivo
        image_file.seek(0)

        # 4️⃣ Guardado DB (sin imagen primero)
        logger.info("💾 Creando EmployeeFace (DB)…")
        face = EmployeeFace.objects.create(
            employee=employee,
            embedding=emb_norm.tolist()
        )

        # 5️⃣ Guardado imagen (S3)
        logger.info(
            f"☁️ Guardando imagen en storage: {default_storage.__class__}"
        )
        face.image = image_file
        face.save()


        logger.info(f"✅ EmployeeFace creado ID={face.id}")

        return JsonResponse(
            {"status": "ok", "face_id": face.id}
        )

    except Exception as e:
        logger.exception("🔥 Error en upload_face_view")
        return JsonResponse(
            {
                "error": "Error interno",
                "detail": str(e),
            },
            status=500,
        )
# Distancia máxima permitida para reconocer (ajustable)
#RECOGNITION_THRESHOLD = 1.1  


RECOGNITION_THRESHOLD = 0.68  # ya vimos que tus distancias rondan 9–16


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.utils.timezone import localdate
import uuid

@csrf_exempt
def recognize_face_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # ---------------------------
        # 1. Verificar kiosko activado
        # ---------------------------
        device_id = request.session.get("device_id")
        if not device_id:
            return JsonResponse({"error": "Dispositivo no configurado"}, status=403)

        try:
            device = Device.objects.get(id=device_id, is_active=True)
        except Device.DoesNotExist:
            return JsonResponse({"error": "Dispositivo inválido"}, status=403)

        # ---------------------------
        # 2. Generar embedding consulta (NO CAMBIAR)
        # ---------------------------
        uploaded_image = request.FILES['image']
        image_bytes = uploaded_image.read()

        emb = generate_embedding(image_bytes, from_bytes=True)
        if emb is None:
            return JsonResponse(
                {'error': 'No se detectó rostro con calidad suficiente'},
                status=400
            )

        q = l2_normalize(emb)
        if q is None:
            return JsonResponse({'error': 'Embedding inválido'}, status=400)

        # ---------------------------
        # 3. Comparar contra base (NO CAMBIAR)
        # ---------------------------
        best_face = None
        best_sim = -1.0

        # ⛔ Por ahora déjalo así para no romper reconocimiento.
        # Luego (cuando confirmemos tu modelo multiempresa) lo filtramos por company.
        faces_qs = EmployeeFace.objects.filter(
            employee__company=device.company,
            embedding__isnull=False
        )

        for face in faces_qs:
            db = l2_normalize(face.embedding)
            if db is None:
                continue

            sim = cosine_similarity(q, db)

            print("Similitud contra", face.employee, ":", sim)

            if sim > best_sim:
                best_sim = sim
                best_face = face

        # ---------------------------
        # 4. Si reconocido → CREAR PENDIENTE (NO registrar Attendance aquí)
        # ---------------------------
        if best_face and best_sim >= RECOGNITION_THRESHOLD:
            emp = best_face.employee

            # Determinar si es entrada o salida (igual que antes)

            today = localdate()

            today_attendance = Attendance.objects.filter(
                employee=emp,
                timestamp__date=today
            ).order_by('timestamp')

            if not today_attendance.exists():
                # Primera marca del día
                suggested_type = 'in'
            elif today_attendance.count() == 1:
                # Segunda marca del día
                suggested_type = 'out'
            else:
                # Ya marcó entrada y salida
                return JsonResponse({
                    "recognized": True,
                    "employee_id": emp.id,
                    "employee_name": str(emp),
                    "message": "Asistencia del día ya completada",
                    "blocked": True
                })


            pending_id = uuid.uuid4().hex

            request.session["pending_attendance"] = {
                "pending_id": pending_id,
                "employee_id": emp.id,
                "suggested_type": suggested_type,
                "device_id": device.id,
                "created_at": timezone.now().isoformat(),
                "similarity": float(best_sim),
            }

            return JsonResponse({
                'recognized': True,
                'employee_id': emp.id,
                'employee_name': str(emp),
                'suggested_type': suggested_type,
                'pending_id': pending_id,
                'similarity': best_sim
            })

        # ---------------------------
        # 5. No reconocido
        # ---------------------------
        return JsonResponse({
            'recognized': False,
            'message': 'Rostro no registrado',
            'best_similarity': best_sim
        })

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


import json
from datetime import datetime
from django.utils.timezone import localtime

@csrf_exempt
def confirm_attendance_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    # ---------------------------
    # 1. Verificar kiosko activado
    # ---------------------------
    device_id = request.session.get("device_id")
    if not device_id:
        return JsonResponse({"error": "Dispositivo no configurado"}, status=403)

    try:
        device = Device.objects.get(id=device_id, is_active=True)
    except Device.DoesNotExist:
        return JsonResponse({"error": "Dispositivo inválido"}, status=403)

    # ---------------------------
    # 2. Leer JSON
    # ---------------------------
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    pending_id = payload.get("pending_id")
    if not pending_id:
        return JsonResponse({"error": "pending_id requerido"}, status=400)

    # ---------------------------
    # 3. Obtener pendiente de sesión
    # ---------------------------
    pending = request.session.get("pending_attendance")
    if not pending:
        return JsonResponse({"error": "No hay asistencia pendiente"}, status=400)

    if pending.get("pending_id") != pending_id:
        return JsonResponse({"error": "pending_id no coincide"}, status=400)

    if pending.get("device_id") != device.id:
        return JsonResponse({"error": "Pendiente no corresponde a este dispositivo"}, status=403)

    # ---------------------------
    # 4. Registrar asistencia
    # ---------------------------
    employee_id = pending.get("employee_id")
    attendance_type = pending.get("suggested_type")    

    # ... dentro de confirm_attendance_view, antes de crear Attendance ...

    now = timezone.now()
    now_local = localtime(now)

    policy = getattr(device.company, "attendance_policy", None)

    status = "unknown"
    scheduled_time = None
    delay_minutes = None

    if policy:
        if attendance_type == "in":
            scheduled_time = policy.entry_time
            # calcular atraso
            scheduled_dt = datetime.combine(now_local.date(), scheduled_time)
            scheduled_dt = timezone.make_aware(scheduled_dt, now_local.tzinfo)

            diff = (now_local - scheduled_dt).total_seconds() / 60  # minutos
            if diff > policy.grace_minutes:
                status = "late"
                delay_minutes = int(diff)
            else:
                status = "on_time"

        elif attendance_type == "out":
            scheduled_time = policy.exit_time
            status = "on_time"  # (nivel 3: early_leave / overtime)

    att = Attendance.objects.create(
        company=device.company,
        employee_id=employee_id,
        device=device,
        attendance_type=attendance_type,
        timestamp=now,
        is_synced=True,
        status=status,
        scheduled_time=scheduled_time,
        delay_minutes=delay_minutes,
    )

    # ---------------------------
    # 5. Limpiar pendiente
    # ---------------------------
    request.session.pop("pending_attendance", None)

    return JsonResponse({
    "success": True,
    "attendance_id": att.id,
    "attendance_type": att.attendance_type,
    "status": att.status,
    "delay_minutes": att.delay_minutes,
    "timestamp": att.timestamp.isoformat()
})




def kiosk_view(request):
    return render(request, 'kiosk.html')


@csrf_exempt
def activate_kiosk_view(request):
    """
    Recibe un código de dispositivo (identifier)
    y guarda el device_id en sesión.
    """

    if request.method == "POST":
        code = request.POST.get("code")

        if not code:
            return JsonResponse({"error": "Debe ingresar un código"}, status=400)

        device = Device.objects.filter(
            identifier=code,
            is_active=True
        ).first()

        if not device:
            return JsonResponse({"error": "Código inválido o dispositivo inactivo"}, status=404)

        # Guardamos dispositivo en sesión
        request.session["device_id"] = device.id
        request.session["company_id"] = device.company.id

        return JsonResponse({
            "status": "ok",
            "device_name": device.name,
            "company": device.company.name
        })

    return JsonResponse({"error": "Solicitud inválida"}, status=400)

def kiosk_activate_page(request):
    return render(request, "employees/kiosk_activate.html")

@csrf_exempt
def kiosk_activate_device(request):
    if request.method == "POST":
        code = request.POST.get("code")

        device = Device.objects.filter(
            identifier=code,
            is_active=True
        ).first()

        if not device:
            return JsonResponse({
                "success": False,
                "message": "Código inválido o dispositivo inactivo"
            })

        # Guardar dispositivo en sesión
        request.session["device_id"] = device.id

        # 🔥 AQUÍ VA EL REDIRECT
        return JsonResponse({
            "success": True,
            "redirect": "/employees/kiosk-camera/"
        })

    return JsonResponse({"error": "Solicitud inválida"}, status=400)


# Página donde está la cámara
def kiosk_camera_page(request):
    if not request.session.get("device_id"):
        return redirect("/employees/kiosk")  # o la url /employees/kiosk/
    
    return render(request, "kiosk.html")

def activate_kiosk(request):
    if request.method == "POST":
        code = request.POST.get("code")

        device = Device.objects.filter(
            identifier=code,
            is_active=True
        ).first()

        if not device:
            return JsonResponse({"error": "Código inválido"})

        # Guardar dispositivo en sesión
        request.session["device_id"] = device.id

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Solicitud inválida"}, status=400)


@login_required(login_url="/accounts/login/")
def employee_list_view(request):
    company = request.user.company

    employees = Employee.objects.filter(
        company=company
    ).order_by("last_name", "first_name")

    return render(request, "dashboard/employee_list.html", {
        "employees": employees
    })

from django.shortcuts import redirect

@login_required(login_url="/accounts/login/")
def employee_create_view(request):
    company = request.user.company

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        identification = request.POST.get("document_number")

        if first_name and last_name:
            Employee.objects.create(
                company=company,
                first_name=first_name,
                last_name=last_name,
                identification=identification,
                is_active=True
            )
            return redirect("/employees/dashboard/employees/")

    return render(request, "dashboard/employee_form.html")


@login_required(login_url="/accounts/login/")
def device_list_view(request):
    company = request.user.company

    devices = Device.objects.filter(company=company).order_by("name")

    return render(request, "dashboard/device_list.html", {
        "devices": devices
    })

@login_required(login_url="/accounts/login/")
def device_create_view(request):
    company = request.user.company

    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Device.objects.create(
                company=company,
                name=name,
                identifier=uuid.uuid4().hex[:8],
                is_active=True
            )
            return redirect("/employees/dashboard/devices/")

    return render(request, "dashboard/device_form.html")

