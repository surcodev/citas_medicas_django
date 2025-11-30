from django.urls import path
from . import views

app_name = 'clinica'

urlpatterns = [
    path('lista_pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('eliminar_paciente/<int:doc_id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('pacientes/editar/', views.editar_paciente, name='editar_paciente'),
    path("obtener_paciente/<int:id>/", views.obtener_paciente, name="obtener_paciente"),

    path('lista_citas/', views.lista_citas, name='lista_citas'),
    path('citas/editar/', views.editar_cita, name='editar_cita'),
    path('eliminar_cita/<int:doc_id>/', views.eliminar_cita, name='eliminar_cita'),


]
