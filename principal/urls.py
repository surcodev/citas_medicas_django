from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    path('lista_usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('editar_usuario/', views.editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('cambiar_password_usuario/', views.cambiar_password_usuario, name='cambiar_password_usuario'),

    path('', include('partidas_planos.urls')),
    path('productivity/', include('productividad.urls')),
    
    path('clinica/', include('clinica.urls')),
    path('ia/', views.int_art, name='int_art'),
    path('perfil_user/', views.perfil_user, name='perfil_user'),
    

    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),
    # path('tinymce/', include('tinymce.urls')),

] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)