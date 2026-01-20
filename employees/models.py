from django.db import models
from core.models import Company

class Employee(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    identification = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'identification')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

from .models import Employee

class EmployeeFace(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='faces'
    )
    image = models.ImageField(upload_to='employee_faces/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Face of {self.employee}"

class EmployeeFace(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='faces'
    )
    image = models.ImageField(upload_to='employee_faces/')
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Face of {self.employee}"
