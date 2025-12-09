from django.contrib import admin
from .models import User

# Registra el modelo User en el admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'role')
    ordering = ('date_joined',)

    # Elimina 'date_joined' y 'last_login' de los fieldsets, ya que son no editables
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superadmin', 'role')
        }),
        ('Important Dates', {
            'fields': ()  # No incluimos 'date_joined' ni 'last_login' aquí
        }),
    )

    # Añadimos los campos 'date_joined' y 'last_login' a readonly_fields
    readonly_fields = ('date_joined', 'last_login')
