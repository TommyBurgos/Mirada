from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=150)
    ruc = models.CharField(max_length=13, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
