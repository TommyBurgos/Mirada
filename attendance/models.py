from django.db import models
from core.models import Company
from employees.models import Employee

class Device(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name='devices')
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    ATTENDANCE_TYPE = (
        ('in', 'Entrada'),
        ('out', 'Salida'),
    )
    STATUS_CHOICES = (
        ('on_time', 'A tiempo'),
        ('late', 'Atraso'),
        ('early_leave', 'Salida temprana'),
        ('overtime', 'Hora extra'),
        ('unknown', 'Sin regla'),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    attendance_type = models.CharField(
        max_length=3,
        choices=ATTENDANCE_TYPE
    )

    # ✅ NUEVO: campos para nivel 2
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    scheduled_time = models.TimeField(null=True, blank=True)
    delay_minutes = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField()
    is_synced = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.attendance_type}"

class CompanyAttendancePolicy(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="attendance_policy")

    # Hora estándar de entrada / salida (por ahora global para la empresa)
    entry_time = models.TimeField(default="08:00")
    exit_time = models.TimeField(default="17:00")

    # tolerancia (minutos) antes de marcar atraso
    grace_minutes = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Policy - {self.company.name}"
