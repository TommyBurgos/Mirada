from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    # Campos que se muestran al editar usuario
    fieldsets = UserAdmin.fieldsets + (
        ("Información de Empresa", {
            "fields": ("company", "role"),
        }),
    )

    # Campos que se muestran al crear usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Información de Empresa", {
            "fields": ("company", "role"),
        }),
    )

    list_display = (
        "username",
        "email",
        "company",
        "role",
        "is_staff",
        "is_superuser",
    )