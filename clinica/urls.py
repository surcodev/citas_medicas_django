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

    path('atender_cita/<int:cita_id>/', views.atender_cita, name='atender_cita'),

    path("eliminar_imagen_respuesta/<int:img_id>/", views.eliminar_imagen_respuesta, name="eliminar_imagen_respuesta"),

    path('', views.home, name='home'),

    path("cita/<int:cita_id>/pdf/", views.generar_pdf_cita, name="generar_pdf_cita"),

    path('paciente/<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    path('historial_paciente/<int:paciente_id>/', views.historial_paciente, name='historial_paciente')

]
