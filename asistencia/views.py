from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Asistencia

@login_required
def home(request):
    user = request.user

    # Si es administrador → ve todo
    if user.role == user.ADMINISTRADOR or user.is_superuser:
        asistencias = Asistencia.objects.all().order_by('-fecha')

        # 🔹 Obtener lista única de trabajadores
        trabajadores = (
            Asistencia.objects
            .select_related('trabajador')
            .values('trabajador__id', 'trabajador__first_name', 'trabajador__last_name')
            .distinct()
            .order_by('trabajador__first_name')
        )

    else:
        # Si no es administrador → solo sus asistencias
        asistencias = Asistencia.objects.filter(trabajador=user).order_by('-fecha')
        trabajadores = []  # No necesita el filtro

    return render(
        request,
        'asistencia/home.html',
        {'asistencias': asistencias, 'trabajadores': trabajadores}
    )
