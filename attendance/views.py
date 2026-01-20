from rest_framework.viewsets import ModelViewSet
from .models import Device, Attendance, CompanyAttendancePolicy
from .serializers import DeviceSerializer, AttendanceSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.utils.timezone import localdate
from employees.models import Employee

import csv
from django.http import HttpResponse
from django.utils.dateparse import parse_date

from openpyxl import Workbook


class DeviceViewSet(ModelViewSet):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        return Device.objects.filter(company=self.request.user.company)


class AttendanceViewSet(ModelViewSet):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        return Attendance.objects.filter(company=self.request.user.company)


@login_required
def kiosk_view(request):
    return render(request, 'attendance/kiosk.html')

from django.db.models import Count
from django.utils.timezone import localdate, timedelta

@login_required(login_url="/accounts/login/")
def dashboard_view(request):
    company = request.user.company
    today = localdate()

    today_attendance = Attendance.objects.filter(
        company=company,
        timestamp__date=today
    )

    total_employees = Employee.objects.filter(company=company).count()
    entries_today = today_attendance.filter(attendance_type="in").count()
    exits_today = today_attendance.filter(attendance_type="out").count()
    late_today = today_attendance.filter(status="late").count()

    # Empleados presentes
    present_employee_ids = []
    for emp_id in today_attendance.values_list("employee_id", flat=True).distinct():
        last = today_attendance.filter(employee_id=emp_id).order_by("-timestamp").first()
        if last and last.attendance_type == "in":
            present_employee_ids.append(emp_id)

    # 🔹 DATOS PARA GRÁFICOS (últimos 7 días)
    days = []
    entries = []
    lates = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        qs = Attendance.objects.filter(
            company=company,
            timestamp__date=day,
            attendance_type="in"
        )

        days.append(day.strftime("%d/%m"))
        entries.append(qs.count())
        lates.append(qs.filter(status="late").count())
    
    punctuality_percent = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        total_entries = Attendance.objects.filter(
            company=company,
            timestamp__date=day,
            attendance_type="in"
        ).count()

        on_time_entries = Attendance.objects.filter(
            company=company,
            timestamp__date=day,
            attendance_type="in",
            status="on_time"
        ).count()

        if total_entries > 0:
            percent = round((on_time_entries / total_entries) * 100, 1)
        else:
            percent = 0

        punctuality_percent.append(percent)
    #TOP EMPLEADOS CON MÁS ATRASOS
    top_late_employees = (
        Attendance.objects.filter(
            company=company,
            status="late",
            timestamp__date__gte=today - timedelta(days=6)
        )
        .values("employee__first_name", "employee__last_name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    late_employee_labels = [
        f"{e['employee__first_name']} {e['employee__last_name']}"
        for e in top_late_employees
    ]

    late_employee_totals = [e["total"] for e in top_late_employees]

    today_entries = entries_today
    today_exits = exits_today

    context = {
        "total_employees": total_employees,
        "entries_today": entries_today,
        "exits_today": exits_today,
        "late_today": late_today,
        "present_now": len(present_employee_ids),
        "today": today,

        # gráficos
        "chart_days": days,
        "chart_entries": entries,
        "chart_lates": lates,
    }
    context.update({
        "chart_punctuality": punctuality_percent,
        "chart_late_employee_labels": late_employee_labels,
        "chart_late_employee_totals": late_employee_totals,
        "chart_today_entries": today_entries,
        "chart_today_exits": today_exits,
    })


    return render(request, "dashboard/index.html", context)


@login_required(login_url="/accounts/login/")
def attendance_list_view(request):
    company = request.user.company

    qs = Attendance.objects.filter(company=company)

    employee_id = request.GET.get("employee")
    status = request.GET.get("status")
    device_id = request.GET.get("device")

    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    if status:
        qs = qs.filter(status=status)

    if device_id:
        qs = qs.filter(device_id=device_id)

    attendances = qs.select_related(
        "employee", "device"
    ).order_by("-timestamp")[:200]

    context = {
        "attendances": attendances,
        "employees": Employee.objects.filter(company=company),
        "devices": Device.objects.filter(company=company),
        "filters": {
            "employee": employee_id,
            "status": status,
            "device": device_id,
        }
    }

    return render(request, "dashboard/attendance_list.html", context)


@login_required(login_url="/accounts/login/")
def attendance_policy_view(request):
    company = request.user.company

    policy, created = CompanyAttendancePolicy.objects.get_or_create(
        company=company
    )

    if request.method == "POST":
        policy.entry_time = request.POST.get("entry_time")
        policy.exit_time = request.POST.get("exit_time")
        policy.grace_minutes = request.POST.get("grace_minutes") or 0
        policy.save()
        return redirect("/dashboard/settings/attendance/")

    return render(request, "dashboard/attendance_policy.html", {
        "policy": policy
    })


@login_required(login_url="/accounts/login/")
def attendance_export_view(request):
    company = request.user.company

    start_date = parse_date(request.GET.get("start"))
    end_date = parse_date(request.GET.get("end"))
    export_format = request.GET.get("format", "csv")

    employee_id = request.GET.get("employee")
    status = request.GET.get("status")
    device_id = request.GET.get("device")

    if not start_date or not end_date:
        return HttpResponse("Fechas inválidas", status=400)

    qs = Attendance.objects.filter(
        company=company,
        timestamp__date__range=(start_date, end_date)
    )

    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    if status:
        qs = qs.filter(status=status)

    if device_id:
        qs = qs.filter(device_id=device_id)

    qs = qs.select_related("employee", "device").order_by("timestamp")

    # =====================
    # EXPORT CSV
    # =====================
    if export_format == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="asistencias_{start_date}_a_{end_date}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow([
            "Empleado", "Fecha", "Hora",
            "Tipo", "Estado", "Minutos atraso", "Dispositivo"
        ])

        for att in qs:
            writer.writerow([
                str(att.employee),
                att.timestamp.date(),
                att.timestamp.strftime("%H:%M"),
                att.attendance_type,
                att.status,
                att.delay_minutes or "",
                att.device.name if att.device else ""
            ])

        return response

    # =====================
    # EXPORT EXCEL
    # =====================
    wb = Workbook()
    ws = wb.active
    ws.title = "Asistencias"

    ws.append([
        "Empleado", "Fecha", "Hora",
        "Tipo", "Estado", "Minutos atraso", "Dispositivo"
    ])

    for att in qs:
        ws.append([
            str(att.employee),
            att.timestamp.date().isoformat(),
            att.timestamp.strftime("%H:%M"),
            att.attendance_type,
            att.status,
            att.delay_minutes or "",
            att.device.name if att.device else ""
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="asistencias_{start_date}_a_{end_date}.xlsx"'
    )

    wb.save(response)
    return response
