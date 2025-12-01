from django.urls import path
from . import views

app_name = 'hoja_requerimiento'

urlpatterns = [
    path('hoja_requerimiento_home/', views.hoja_requerimiento_home, name='hoja_requerimiento_home'),
    path('lista_q1_t1/', views.lista_q1_n1, name='lista_q1_t1'),
]
