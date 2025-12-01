from django.db import models
from django.utils import timezone
from partidas_planos.models import User
from ckeditor.fields import RichTextField
from datetime import date
from tinymce.models import HTMLField

class CasoJudicial(models.Model):
    REPRESENTANTE_CHOICES = [
        ('Demandante', 'Demandante'),
        ('Demandado', 'Demandado'),
        ('Martillero', 'Martillero'),
    ]
    codigo = models.CharField(max_length=100, blank=True, null=True)
    fecha_compromiso = models.DateField(blank=True, null=True)
    expediente = models.CharField(max_length=100)
    sede = models.CharField(max_length=100, blank=True, null=True)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    materia = models.CharField(max_length=255, blank=True, null=True)
    juzgado = models.CharField(max_length=255, blank=True, null=True)
    demandante = models.CharField(max_length=255)
    demandado = models.CharField(max_length=255)
    representante = models.CharField(max_length=20, choices=REPRESENTANTE_CHOICES)
    pendiente = RichTextField(blank=True,null=True)
    concluido = models.BooleanField(default=True, help_text="True => Activo, False => Concluido")

    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 2},  # Solo usuarios con rol LEGAL
        related_name='casos_asignados',
        verbose_name='Responsable (Área Legal)'
    )

    def __str__(self):
        return f"{self.expediente}"


class Seguimiento(models.Model):
    ESTADO_CHOICES = [
        ('En proceso', 'En Proceso'),
        ('Finalizado', 'Finalizado'),
        ('Presentado', 'Presentado'),
        ('Notificado', 'Notificado'),
        ('Otros', 'Otros'),
    ]

    caso = models.ForeignKey(CasoJudicial, on_delete=models.CASCADE, related_name='seguimientos')
    resolucion = models.CharField(max_length=255, blank=True, null=True)
    fecha_seguimiento = models.DateField(blank=True, null=True)
    seguimiento = HTMLField(null=True, blank=True)
    fecha_pendiente = models.DateField(blank=True, null=True) # fecha notificacion
    pendiente = HTMLField(null=True, blank=True)
    responsable = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Finalizado')
    pdf = models.FileField(upload_to='seguimiento/', max_length=255, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now=True) # (auto_now_add=True)
    editor = models.CharField(max_length=255, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='seguimientos_creados')
    fecha_alerta = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Seguimiento - {self.caso.expediente} - {self.fecha_seguimiento}"



class Gasto(models.Model):
    # TIPO_GASTO = [
    #     ('Caja Chica', 'Caja Chica'),
    #     ('Externo', 'Externo'),
    # ]
    seguimiento = models.ForeignKey(Seguimiento, on_delete=models.CASCADE, related_name='gastos')
    fecha = models.DateField()
    detalle = models.CharField(max_length=255, blank=True, null=True)
    sustento = models.TextField(blank=True)
    pdf = models.FileField(upload_to='gastos_expediente/', max_length=255, blank=True, null=True)
    codigo_pago = models.CharField(max_length=255, blank=True, null=True)
    gastos_soles = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gastos_dolares = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)   # Fecha de creación
    fecha_modificacion = models.DateTimeField(auto_now=True)       # Fecha de modificación
    editor = models.CharField(max_length=255, blank=True, null=True)
    # tipo_gasto = models.CharField(max_length=20, choices=TIPO_GASTO, default='Externo')

    def __str__(self):
        return f"Gasto - {self.seguimiento.caso.expediente} - {self.fecha}"

################################################################################################################

# LOGS ACTIVIDAD
class RegistroActividad(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateTimeField()
    actividad = models.TextField()

    def __str__(self):
        return f"{self.nombre} - {self.actividad}"
    
################################################################################################################

class CarpetaFiscal(models.Model):
    REPRESENTANTE_CHOICES = [
        ('Demandante', 'Demandante'),
        ('Demandado', 'Demandado'),
        ('Martillero', 'Martillero'),
    ]
    item = models.CharField(max_length=100, blank=True, null=True)
    carpeta_fiscal = models.CharField(max_length=100, blank=True, null=True)
    pendiente = RichTextField(blank=True,null=True)
    delito = models.CharField(max_length=100, blank=True, null=True)
    fiscalia = models.CharField(max_length=100, blank=True, null=True)
    demandante = models.CharField(max_length=255)
    demandado = models.CharField(max_length=255)
    sede = models.CharField(max_length=100, blank=True, null=True)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    representante = models.CharField(max_length=20, choices=REPRESENTANTE_CHOICES)
    concluido = models.BooleanField(default=True, help_text="True => Activo, False => Concluido")

    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 2},  # Solo usuarios con rol LEGAL
        related_name='casos_asignados_carpeta_fiscal',
        verbose_name='Responsable (Área Legal)'
    )

    def __str__(self):
        return f"{self.carpeta_fiscal}"

    def alerta_color(self):
        """
        Devuelve el color según la fecha_alerta más cercana a hoy (futura o actual).
        Si todas las fechas ya pasaron o no existen, retorna 'secondary'.
        """
        hoy = date.today()

        # Buscar la fecha más próxima a hoy (sin haber pasado)
        proximo_seguimiento = (
            self.seguimientos_penal
            .filter(fecha_alerta__gte=hoy)
            .order_by('fecha_alerta')  # más próxima
            .first()
        )

        if not proximo_seguimiento:
            return "secondary"  # no hay alertas futuras o todas pasaron

        dias_restantes = (proximo_seguimiento.fecha_alerta - hoy).days

        if dias_restantes <= 5:
            return "danger"     # 3 días o menos → rojo
        elif dias_restantes <= 15:
            return "warning"    # entre 4 y 6 días → amarillo
        else:
            return "success"    # más de 6 días → verde


class SeguimientoFiscal(models.Model):
    ESTADO_CHOICES = [
        ('En proceso', 'En Proceso'),
        ('Finalizado', 'Finalizado'),
        ('Presentado', 'Presentado'),
        ('Notificado', 'Notificado'),
        ('Otros', 'Otros'),
    ]

    caso = models.ForeignKey(CarpetaFiscal, on_delete=models.CASCADE, related_name='seguimientos_penal')
    resolucion = models.CharField(max_length=255, blank=True, null=True)
    fecha_seguimiento = models.DateField(blank=True, null=True)
    seguimiento = RichTextField(blank=True,null=True)
    fecha_pendiente = models.DateField(blank=True, null=True) # fecha notificacion
    pendiente = RichTextField(blank=True,null=True)
    responsable = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_proceso')
    pdf = models.FileField(upload_to='seguimiento/', max_length=255, blank=True, null=True)
    inter = models.BooleanField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now=True) # (auto_now_add=True)
    editor = models.CharField(max_length=255, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='seguimientos_creados_fiscal')
    fecha_alerta = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Seguimiento - {self.caso.carpeta_fiscal} - {self.fecha_seguimiento}"


class GastoFiscal(models.Model):
    seguimiento = models.ForeignKey(SeguimientoFiscal, on_delete=models.CASCADE, related_name='gastos_fiscal')
    fecha = models.DateField()
    detalle = models.CharField(max_length=255, blank=True, null=True)
    sustento = models.TextField(blank=True)
    pdf = models.FileField(upload_to='gastos_expediente/', max_length=255, blank=True, null=True)
    codigo_pago = models.CharField(max_length=255, blank=True, null=True)
    gastos_soles = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gastos_dolares = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    editor = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Gasto - {self.seguimiento.caso.carpeta_fiscal} - {self.fecha} - S/ {self.gastos_soles}"