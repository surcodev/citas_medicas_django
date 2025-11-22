from django.urls import path
from . import views

app_name = 'centro_costos'

urlpatterns = [
    path('home/', views.centro_costos_home, name='home'),

    path('lista_actividades/', views.lista_actividades, name='lista_actividades'),
    path('editar_actividad/', views.editar_actividad, name='editar_actividad'),
    path('eliminar_actividad/<int:doc_id>/', views.eliminar_actividad, name='eliminar_actividad'),
    
    path('lista_gastos/', views.lista_gasto_ta_2020, name='lista_gastos'),
    path('editar_gasto/', views.editar_gasto_ta_2020, name='editar_gasto'),
    path('eliminar_gasto/<int:doc_id>/', views.eliminar_gasto_ta_2020, name='eliminar_gasto'),

    path('lista_gastoN1/', views.lista_gasto_ta_2024, name='lista_gastoN1'),
    path('editar_gastoN1/', views.editar_gasto_ta_2024, name='editar_gastoN1'),
    path('eliminar_gastoN1/<int:doc_id>/', views.eliminar_gasto_ta_2024, name='eliminar_gastoN1'),

    path('lista_canta_callao/', views.lista_canta_callao, name='lista_canta_callao'),
    path('editar_canta_callao/', views.editar_canta_callao, name='editar_canta_callao'),
    path('eliminar_canta_callao/<int:doc_id>/', views.eliminar_canta_callao, name='eliminar_canta_callao'),

    path('agregar_nuevo_gasto/', views.agregar_nuevo_gasto, name='agregar_nuevo_gasto'),

    path('lista_gastoN2/', views.lista_gastoN2, name='lista_gastoN2'),
    path('editar_gastoN2/', views.editar_gastoN2, name='editar_gastoN2'),
    path('eliminar_gastoN2/<int:doc_id>/', views.eliminar_gastoN2, name='eliminar_gastoN2'),

    path('lista_gastoN3/', views.lista_gastoN3, name='lista_gastoN3'),
    path('editar_gastoN3/', views.editar_gastoN3, name='editar_gastoN3'),
    path('eliminar_gastoN3/<int:doc_id>/', views.eliminar_gastoN3, name='eliminar_gastoN3'),

    path('lista_gastoN4/', views.lista_gastoN4, name='lista_gastoN4'),
    path('editar_gastoN4/', views.editar_gastoN4, name='editar_gastoN4'),
    path('eliminar_gastoN4/<int:doc_id>/', views.eliminar_gastoN4, name='eliminar_gastoN4'),

    path('lista_gastoN5/', views.lista_gastoN5, name='lista_gastoN5'),
    path('editar_gastoN5/', views.editar_gastoN5, name='editar_gastoN5'),
    path('eliminar_gastoN5/<int:doc_id>/', views.eliminar_gastoN5, name='eliminar_gastoN5'),

    path('lista_gastoN6/', views.lista_gastoN6, name='lista_gastoN6'),
    path('editar_gastoN6/', views.editar_gastoN6, name='editar_gastoN6'),
    path('eliminar_gastoN6/<int:doc_id>/', views.eliminar_gastoN6, name='eliminar_gastoN6'),

    path('lista_gastoN7/', views.lista_gastoN7, name='lista_gastoN7'),
    path('editar_gastoN7/', views.editar_gastoN7, name='editar_gastoN7'),
    path('eliminar_gastoN7/<int:doc_id>/', views.eliminar_gastoN7, name='eliminar_gastoN7'),

    path('lista_gastoN8/', views.lista_gastoN8, name='lista_gastoN8'),
    path('editar_gastoN8/', views.editar_gastoN8, name='editar_gastoN8'),
    path('eliminar_gastoN8/<int:doc_id>/', views.eliminar_gastoN8, name='eliminar_gastoN8'),

    path('lista_gastoN9/', views.lista_gastoN9, name='lista_gastoN9'),
    path('editar_gastoN9/', views.editar_gastoN9, name='editar_gastoN9'),
    path('eliminar_gastoN9/<int:doc_id>/', views.eliminar_gastoN9, name='eliminar_gastoN9'),

    path('lista_gastoN10/', views.lista_gastoN10, name='lista_gastoN10'),
    path('editar_gastoN10/', views.editar_gastoN10, name='editar_gastoN10'),
    path('eliminar_gastoN10/<int:doc_id>/', views.eliminar_gastoN10, name='eliminar_gastoN10'),

    path('home_ta/', views.home_ta, name='home_ta'),
    path('home_cc/', views.home_cc, name='home_cc'),
]
