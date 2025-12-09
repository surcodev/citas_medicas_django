from django.test import TestCase
from django.contrib.auth import get_user_model
from productividad.models import DailyActivity


User = get_user_model()


class ActivityModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', email='u1@example.com', password='pass')


    def test_create_activity(self):
        a = DailyActivity.objects.create(user=self.user, date='2025-01-01', title='Tarea X')
        self.assertEqual(a.title, 'Tarea X')




# === README (setup quick steps) ===
"""
1) Añadir 'productivity' en INSTALLED_APPS.
2) Asegúrate AUTH_USER_MODEL apunta a tu modelo User personalizado.
3) Ejecuta migrations: python manage.py makemigrations && python manage.py migrate
4) Instala dependencias (opcional): pip install django
5) Copia templates y static a las rutas correspondientes.
6) Ejecuta collectstatic si en producción.
7) Para protección extra: instalar and configure fail2ban y limitar SSH (no relacionado con la app).


Me avisas y adapto cualquier cosa: permisos, campos, o reportes.
"""