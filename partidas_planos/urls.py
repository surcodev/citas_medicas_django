from django.urls import path
from . import views

urlpatterns = [
    path('documentacion/', views.documentacion, name='documentacion'),
    
    # Rutas para Partida
    path('lista_partidas/', views.lista_partidas, name='lista_partidas'),
    path('editar_partida/', views.editar_partida, name='editar_partida'),
    path('eliminar_partida/<int:doc_id>/', views.eliminar_partida, name='eliminar_partida'),

    # Rutas para Plano
    path('lista_planos/', views.lista_planos, name='lista_planos'),
    path('editar_plano/', views.editar_plano, name='editar_plano'),
    path('eliminar_plano/<int:doc_id>/', views.eliminar_plano, name='eliminar_plano'),

    # Sistemas
    path('sistemas/', views.sistemas, name='sistemas'),

]
