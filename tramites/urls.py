from django.urls import path
from . import views

app_name = 'tramites'

urlpatterns = [
    path('lista_tramite/', views.lista_tramite, name='lista_tramite'),
    path('editar_tramite/', views.editar_tramite, name='editar_tramite'),
    path('eliminar_tramite/<int:doc_id>/', views.eliminar_tramite, name='eliminar_tramite'),

    path('seguimiento_tramite/<int:caso_id>/', views.ver_seguimiento_tramite, name='ver_seguimiento_tramite'),
    path('editar_seguimiento_tramite/', views.editar_seguimiento_tramite, name='editar_seguimiento_tramite'),
    path('eliminar_seguimiento_tramite/eliminar/<int:seguimiento_tramite_id>/', views.eliminar_seguimiento_tramite, name='eliminar_seguimiento_tramite'),

    path('editar_gasto_tramite/', views.editar_gasto_tramite, name='editar_gasto_tramite'),
    path('eliminar_gasto_tramite/', views.eliminar_gasto_tramite, name='eliminar_gasto_tramite'),

    path('exportar_gastos_tramite_excel/<int:caso_id>/', views.exportar_gastos_tramite_excel, name='exportar_gastos_tramite_excel'),

    # CONCLUIDOS
    path('lista_t_concluidos/', views.lista_tramite_concluidos, name='lista_tramite_concluidos'),
    path('ver_seguimiento_t_concluido/<int:caso_id>/', views.ver_seguimiento_t_concluido, name='ver_seguimiento_t_concluido'),
    path('editar_t_concluido/', views.editar_t_concluido, name='editar_t_concluido'),
]