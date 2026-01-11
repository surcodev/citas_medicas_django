from django.db import models
from tinymce.models import HTMLField
from datetime import date

class Paciente(models.Model):
    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    nombre = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    dni = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)

    # ANAMNESIS
    alergias_conocidas = models.CharField(max_length=255, blank=True, null=True)
    emfermedades_previas = models.CharField(max_length=255, blank=True, null=True)
    antecentes_quirurgicos = models.CharField(max_length=255, blank=True, null=True)
    antecedentes_familiares = models.CharField(max_length=255, blank=True, null=True)
    medicamentos_actuales = models.CharField(max_length=255, blank=True, null=True)
    habitos = models.CharField(max_length=255, blank=True, null=True)
    relato_clinico = models.TextField(blank=True, null=True)

    # EXAMEN FISICO
    edad = models.CharField(max_length=255, blank=True, null=True)
    peso = models.CharField(max_length=50, blank=True, null=True)
    altura = models.CharField(max_length=50, blank=True, null=True)
    presion_arterial = models.CharField(max_length=50, blank=True, null=True)
    frecuencia_cardiaca = models.CharField(max_length=50, blank=True, null=True)
    frecuencia_respiratoria = models.CharField(max_length=50, blank=True, null=True)
    temperatura = models.CharField(max_length=50, blank=True, null=True)
    tipo_de_sangre = models.CharField(
        max_length=10,
        choices=TIPO_SANGRE_CHOICES,
        blank=True,
        null=True
    )
    descripcion_examen_fisico = models.TextField(blank=True, null=True)

    # CONTACTO DE EMERGENCIA
    nombre_contacto_emergencia1 = models.CharField(max_length=100, blank=True, null=True)
    telefono_contacto_emergencia1 = models.CharField(max_length=15, blank=True, null=True)
    relacion_contacto_emergencia1 = models.CharField(max_length=50, blank=True, null=True)
    nombre_contacto_emergencia2 = models.CharField(max_length=100, blank=True, null=True)
    telefono_contacto_emergencia2 = models.CharField(max_length=15, blank=True, null=True)
    relacion_contacto_emergencia2 = models.CharField(max_length=50, blank=True, null=True)
    nombre_contacto_emergencia3 = models.CharField(max_length=100, blank=True, null=True)
    telefono_contacto_emergencia3 = models.CharField(max_length=15, blank=True, null=True)
    relacion_contacto_emergencia3 = models.CharField(max_length=50, blank=True, null=True)

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre or "Paciente sin nombre"
    
    @property
    def edad_paciente(self):
        if not self.fecha_nacimiento:
            return None

        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )


class ArchivoPaciente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="archivos")
    archivo = models.FileField(upload_to="pacientes/archivos/")
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Archivo de {self.paciente.nombre}"


class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    estado = models.BooleanField(default=False, blank=True, null=True)  # False = programada, True = completada

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita de {self.paciente.nombre} el {self.fecha} a las {self.hora}"


class RespuestaCita(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='respuesta')
    diagnostico = HTMLField(null=True, blank=True)
    tratamiento = models.TextField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    receta = models.TextField(blank=True, null=True)

    # ANAMNESIS
    alergias_conocidas = models.CharField(max_length=255, blank=True, null=True)
    emfermedades_previas = models.CharField(max_length=255, blank=True, null=True)
    antecentes_quirurgicos = models.CharField(max_length=255, blank=True, null=True)
    antecedentes_familiares = models.CharField(max_length=255, blank=True, null=True)
    medicamentos_actuales = models.CharField(max_length=255, blank=True, null=True)
    habitos = models.CharField(max_length=255, blank=True, null=True)
    relato_clinico = models.TextField(blank=True, null=True)

    # EXAMEN FISICO
    peso = models.CharField(max_length=50, blank=True, null=True)
    altura = models.CharField(max_length=50, blank=True, null=True)
    presion_arterial = models.CharField(max_length=50, blank=True, null=True)
    frecuencia_cardiaca = models.CharField(max_length=50, blank=True, null=True)
    frecuencia_respiratoria = models.CharField(max_length=50, blank=True, null=True)
    descripcion_examen_fisico = models.TextField(blank=True, null=True)

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Respuesta a la cita {self.cita.id}"

class ImagenRespuestaCita(models.Model):
    respuesta = models.ForeignKey(
        RespuestaCita,
        on_delete=models.CASCADE,
        related_name="imagenes"
    )
    imagen = models.ImageField(upload_to="respuesta_cita/imagenes/")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagen de respuesta {self.respuesta.id}"