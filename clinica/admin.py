from django.contrib import admin
from .models import Paciente, Cita, RespuestaCita

# ============================
# INLINE: Respuesta de la cita
# ============================
class RespuestaCitaInline(admin.StackedInline):
    model = RespuestaCita
    extra = 0


# ============================
# ADMIN: Cita
# ============================
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'fecha', 'hora', 'motivo')
    list_filter = ('fecha',)
    search_fields = ('paciente__nombre', 'motivo')
    inlines = [RespuestaCitaInline]


# ============================
# INLINE: Citas dentro de paciente
# ============================
class CitaInline(admin.TabularInline):
    model = Cita
    extra = 0
    show_change_link = True


# ============================
# ADMIN: Paciente
# ============================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'dni', 'telefono', 'email')
    search_fields = ('nombre', 'dni', 'telefono', 'email')
    list_filter = ('tipo_de_sangre',)
    inlines = [CitaInline]


# ============================
# ADMIN: RespuestaCita (opcional)
# ============================

@admin.register(RespuestaCita)
class RespuestaCitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cita', 'diagnostico')
    search_fields = ('cita__paciente__nombre', 'diagnostico', 'tratamiento')
