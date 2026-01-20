# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import Company

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='supervisor'
    )

    def __str__(self):
        return self.username
