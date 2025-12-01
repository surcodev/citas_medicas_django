from django.urls import path
from . import views

app_name = 'control_expediente'

urlpatterns = [
    path('lista_expediente/', views.lista_expediente, name='lista_expediente'),
    
    path('editar_expediente/', views.editar_expediente, name='editar_expediente'),
    path('eliminar_expediente/<int:doc_id>/', views.eliminar_expediente, name='eliminar_expediente'),

    path('seguimiento_expediente/<int:caso_id>/', views.ver_seguimiento, name='ver_seguimiento'),
    path('editar_seguimiento_expediente/', views.editar_seguimiento, name='editar_seguimiento'),
    path('seguimiento_expediente/eliminar/<int:seguimiento_id>/', views.eliminar_seguimiento, name='eliminar_seguimiento'),

    path('editar_ce_gasto/', views.editar_gasto, name='editar_gasto'),
    path('eliminar_ce_gasto/', views.eliminar_gasto, name='eliminar_gasto'),


    path('lista_registros_actividad/', views.lista_registros_actividad, name='lista_registros_actividad'),

    # EXPORTAR GASTOS A EXCEL
    path('exportar_gastos_excel/<int:caso_id>/', views.exportar_gastos_excel, name='exportar_gastos_excel'),
    path('exportar_gastos_fiscal_excel/<int:caso_id>/', views.exportar_gastos_fiscal_excel, name='exportar_gastos_fiscal_excel'),




    # CARPETA FISCAL
    path('lista_carpeta_fiscal/', views.lista_carpeta_fiscal, name='lista_carpeta_fiscal'),
    path('editar_carpeta_fiscal/', views.editar_carpeta_fiscal, name='editar_carpeta_fiscal'),
    path('eliminar_carpeta_fiscal/<int:doc_id>/', views.eliminar_carpeta_fiscal, name='eliminar_carpeta_fiscal'),

    path('ver_seguimiento_carpeta_fiscal/<int:caso_id>/', views.ver_seguimiento_carpeta_fiscal, name='ver_seguimiento_carpeta_fiscal'),
    path('editar_seguimiento_carpeta_fiscal/', views.editar_seguimiento_carpeta_fiscal, name='editar_seguimiento_carpeta_fiscal'),
    path('seguimiento_carpeta_fiscal/eliminar/<int:seguimiento_id>/', views.eliminar_seguimiento_carpeta_fiscal, name='eliminar_seguimiento_carpeta_fiscal'),

    path('editar_ce_gasto_carpeta_fiscal/', views.editar_ce_gasto_carpeta_fiscal, name='editar_ce_gasto_carpeta_fiscal'),
    path('eliminar_gasto_carpeta_fiscal/', views.eliminar_gasto_carpeta_fiscal, name='eliminar_gasto_carpeta_fiscal'),


    # CONCLUIDOS
    path('concluido/', views.lista_concluidos, name='lista_concluidos'),
    path('seguimiento_concluido/<int:caso_id>/', views.ver_seguimiento_concluido, name='ver_seguimiento_concluido'),
    path('editar_exp_gen_concluido/', views.editar_expediente_general_concluido, name='editar_expediente_general_concluido'),
    path('eliminar_exp_concluido/<int:doc_id>/', views.eliminar_exp_concluido, name='eliminar_exp_concluido'),

    path('lista_concluidos_fiscal/', views.lista_concluidos_fiscal, name='lista_concluidos_fiscal'),
    path('seguimiento_fiscal_concluido/<int:caso_id>/', views.ver_seguimiento_fiscal_concluido, name='ver_seguimiento_fiscal_concluido'),
    path('editar_exp_fiscal_concluido/', views.editar_expediente_fiscal_concluido, name='editar_expediente_fiscal_concluido'),
    path('eliminar_concluidos_fiscal/<int:doc_id>/', views.eliminar_concluidos_fiscal, name='eliminar_concluidos_fiscal'),
]