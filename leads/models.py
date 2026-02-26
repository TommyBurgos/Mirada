from django.db import models


class Lead(models.Model):
    STATUS_CHOICES = (
        ("new", "Nuevo"),
        ("contacted", "Contactado"),
        ("qualified", "Calificado"),
        ("closed", "Cerrado"),
    )

    name = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    employees = models.PositiveIntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.name}"