from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from productividad.models import *
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.http import HttpResponse
import pdfkit


from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def historial_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Solo citas completadas
    citas = paciente.citas.filter(estado=True).order_by('-fecha', '-hora')

    citas_data = []
    for c in citas:
        # Manejar citas sin respuesta
        try:
            r = c.respuesta
            diagnostico = r.diagnostico
            tratamiento = r.tratamiento
            notas = r.notas
            receta = r.receta

            # Agregar URLs de imágenes
            imagenes = [img.imagen.url for img in r.imagenes.all()]
        except:
            diagnostico = ''
            tratamiento = ''
            notas = ''
            receta = ''
            imagenes = []

        citas_data.append({
            "id": c.id,
            "fecha": c.fecha.strftime('%Y-%m-%d'),
            "hora": c.hora.strftime('%H:%M'),
            "motivo": c.motivo or '',
            "respuesta": {
                "diagnostico": diagnostico,
                "tratamiento": tratamiento,
                "notas": notas,
                "receta": receta,
                "imagenes": imagenes,
            }
        })

    return JsonResponse({"citas": citas_data})


@login_required
def generar_pdf_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if not cita.estado:
        return HttpResponse("La cita aún no está completada.", status=400)

    respuesta = cita.respuesta
    paciente = cita.paciente
    imagenes = respuesta.imagenes.all() if respuesta else []

    html = render_to_string("clinica/pdf/cita_pdf.html", {
        "cita": cita,
        "paciente": paciente,
        "respuesta": respuesta,
        "imagenes": imagenes,
        "fecha_actual": datetime.now(),
    })

    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
    }

    # pdf = pdfkit.from_string(html, False, options=options)
    import os
    #config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
#    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)


    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="cita_{cita.id}.pdf"'
    return response



@login_required
def home(request):

    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    # Citas de hoy
    citas_hoy = Cita.objects.filter(fecha=hoy).order_by("hora")

    # Citas de la semana
    citas_semana = Cita.objects.filter(
        fecha__range=[inicio_semana, fin_semana]
    ).order_by("fecha", "hora")

    # Próxima cita del día
    proxima_cita = citas_hoy.first() if citas_hoy.exists() else None

    return render(request, "clinica/home.html", {
        "citas_hoy": citas_hoy,
        "citas_semana": citas_semana,
        "proxima_cita": proxima_cita,
    })

def eliminar_imagen_respuesta(request, img_id):
    imagen = get_object_or_404(ImagenRespuestaCita, id=img_id)
    cita_id = imagen.respuesta.cita.id
    imagen.delete()
    return redirect("clinica:atender_cita", cita_id=cita_id)

def atender_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    paciente = cita.paciente

    # Crear respuesta si no existe
    respuesta, created = RespuestaCita.objects.get_or_create(cita=cita)

    # ================================
    # NUEVO: Citas anteriores del paciente
    # ================================
    citas_anteriores = (
        Cita.objects
        .filter(paciente=paciente)
        .exclude(id=cita.id)
        .order_by('-fecha')   # más recientes primero
    )

    if request.method == "POST":
        # --- GUARDAR RESPUESTA ---
        respuesta.diagnostico = request.POST.get("diagnostico")
        respuesta.tratamiento = request.POST.get("tratamiento")
        respuesta.notas = request.POST.get("notas")
        respuesta.receta = request.POST.get("receta")
        respuesta.save()

        # --- GUARDAR IMÁGENES ---
        files = request.FILES.getlist("imagenes")
        for f in files:
            ImagenRespuestaCita.objects.create(
                respuesta=respuesta,
                imagen=f
            )

        # --- GUARDAR DATOS DEL PACIENTE ---
        fields = [
            "alergias_conocidas", "emfermedades_previas", "antecentes_quirurgicos",
            "antecedentes_familiares", "medicamentos_actuales", "habitos",
            "relato_clinico",
            "edad", "peso", "altura", "presion_arterial", "frecuencia_cardiaca",
            "frecuencia_respiratoria", "temperatura", "tipo_de_sangre",
            "descripcion_examen_fisico",
            "nombre_contacto_emergencia1", "telefono_contacto_emergencia1",
            "relacion_contacto_emergencia1",
            "nombre_contacto_emergencia2", "telefono_contacto_emergencia2",
            "relacion_contacto_emergencia2",
            "nombre_contacto_emergencia3", "telefono_contacto_emergencia3",
            "relacion_contacto_emergencia3",
        ]

        for field in fields:
            setattr(paciente, field, request.POST.get(field))

        paciente.save()

        # Cambiar estado a completada
        cita.estado = True
        cita.save()

        return redirect("clinica:atender_cita", cita_id=cita.id)

    # ================================
    # RETORNO FINAL CON TODO LO NECESARIO
    # ================================
    return render(request, "clinica/atender_cita.html", {
        "cita": cita,
        "paciente": paciente,
        "respuesta": respuesta,
        "citas_anteriores": citas_anteriores,  # 🔥 IMPORTANTE
    })



def lista_citas(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            nueva_cita = form.save()  # guardamos la cita
            # ================================
            #   CREAR DailyActivity AUTOMÁTICO
            # ================================
            # Fecha
            fecha_actividad = nueva_cita.fecha
            # Hora inicial
            hora_ini = datetime.combine(nueva_cita.fecha, nueva_cita.hora)
            # Hora + 30 minutos
            hora_fin = hora_ini + timedelta(minutes=30)
            # Convertir a formato "9:00" (sin segundos)
            hora_ini_str = hora_ini.strftime("%H:%M")
            hora_fin_str = hora_fin.strftime("%H:%M")
            # Título con el formato requerido
            titulo = f"{hora_ini_str} - {hora_fin_str} | {nueva_cita.paciente.nombre}"
            # Descripción = motivo de la cita
            descripcion = nueva_cita.motivo

            # Crear actividad
            DailyActivity.objects.create(
                user=request.user,
                date=fecha_actividad,
                title=titulo,
                description=descripcion
            )
            return redirect('clinica:lista_citas')
    else:
        form = CitaForm()

    citas = Cita.objects.all().order_by('-fecha')
    pacientes = Paciente.objects.all()

    return render(request, 'clinica/citas_medicas.html', {
        'citas': citas,
        'form': form,
        'pacientes': pacientes,
    })


def editar_cita(request):
    if request.method == "POST":
        cita_id = request.POST.get("id")

        # Obtener cita
        cita = get_object_or_404(Cita, id=cita_id)

        # Actualizar campos
        cita.paciente_id = request.POST.get("paciente")
        cita.fecha = request.POST.get("fecha")
        cita.hora = request.POST.get("hora")
        cita.motivo = request.POST.get("motivo")
        cita.estado = request.POST.get("estado") == "True"  # convierte string a booleano

        cita.save()

        messages.success(request, "La cita fue actualizada correctamente.")
        return redirect("clinica:lista_citas")  # <-- cambia si tu URL tiene otro nombre

    messages.error(request, "Método inválido.")
    return redirect("clinica:lista_citas")


def eliminar_cita(request, doc_id):
    cita = get_object_or_404(Cita, id=doc_id)
    cita.delete()
    return redirect('clinica:lista_citas')

#####################################################################################

from django.shortcuts import render, redirect
from .models import Paciente



def detalle_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Traer todas las citas de este paciente, más recientes primero
    citas_anteriores = paciente.citas.all().order_by('-fecha', '-hora')

    return render(request, "clinica/detalle_paciente.html", {
        "paciente": paciente,
        "citas_anteriores": citas_anteriores,
    })



def lista_pacientes(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clinica:lista_pacientes")
    else:
        form = PacienteForm()

    # Traer todos los pacientes con sus citas (más eficiente)
    pacientes = Paciente.objects.prefetch_related('citas')

    return render(request, "clinica/lista_pacientes.html", {
        "pacientes": pacientes,
        "form": form
    })




def eliminar_paciente(request, doc_id):
    doc = get_object_or_404(Paciente, id=doc_id)
    doc.delete()
    return redirect('clinica:lista_pacientes')


def editar_paciente(request):
    if request.method == "POST":
        paciente_id = request.POST.get("id")
        paciente = get_object_or_404(Paciente, id=paciente_id)

        # Actualizar campos del Paciente
        paciente.nombre = request.POST.get("nombre")
        paciente.email = request.POST.get("email")
        paciente.dni = request.POST.get("dni")
        paciente.telefono = request.POST.get("telefono")
        paciente.direccion = request.POST.get("direccion")

        # ANAMNESIS
        paciente.alergias_conocidas = request.POST.get("alergias_conocidas")
        paciente.emfermedades_previas = request.POST.get("emfermedades_previas")
        paciente.antecentes_quirurgicos = request.POST.get("antecentes_quirurgicos")
        paciente.antecedentes_familiares = request.POST.get("antecedentes_familiares")
        paciente.medicamentos_actuales = request.POST.get("medicamentos_actuales")
        paciente.habitos = request.POST.get("habitos")
        paciente.relato_clinico = request.POST.get("relato_clinico")

        # EXAMEN FÍSICO
        paciente.edad = request.POST.get("edad")
        paciente.peso = request.POST.get("peso")
        paciente.altura = request.POST.get("altura")
        paciente.presion_arterial = request.POST.get("presion_arterial")
        paciente.frecuencia_cardiaca = request.POST.get("frecuencia_cardiaca")
        paciente.frecuencia_respiratoria = request.POST.get("frecuencia_respiratoria")
        paciente.temperatura = request.POST.get("temperatura")
        paciente.tipo_de_sangre = request.POST.get("tipo_de_sangre")
        paciente.descripcion_examen_fisico = request.POST.get("descripcion_examen_fisico")

        # CONTACTO DE EMERGENCIA
        paciente.nombre_contacto_emergencia1 = request.POST.get("nombre_contacto_emergencia1")
        paciente.telefono_contacto_emergencia1 = request.POST.get("telefono_contacto_emergencia1")
        paciente.relacion_contacto_emergencia1 = request.POST.get("relacion_contacto_emergencia1")
        paciente.nombre_contacto_emergencia2 = request.POST.get("nombre_contacto_emergencia2")
        paciente.telefono_contacto_emergencia2 = request.POST.get("telefono_contacto_emergencia2")
        paciente.relacion_contacto_emergencia2 = request.POST.get("relacion_contacto_emergencia2")
        paciente.nombre_contacto_emergencia3 = request.POST.get("nombre_contacto_emergencia3")
        paciente.telefono_contacto_emergencia3 = request.POST.get("telefono_contacto_emergencia3")
        paciente.relacion_contacto_emergencia3 = request.POST.get("relacion_contacto_emergencia3")

        paciente.save()

        # -----------------------------
        # GUARDAR MULTIPLES ARCHIVOS
        # -----------------------------
        archivos = request.FILES.getlist('archivos')

        for archivo in archivos:
            ArchivoPaciente.objects.create(
                paciente=paciente,
                archivo=archivo,
            )

        messages.success(request, "Paciente actualizado correctamente.")

        return redirect('clinica:lista_pacientes')

    return redirect('clinica:lista_pacientes')


def obtener_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)

    # Obtener archivos
    archivos = ArchivoPaciente.objects.filter(paciente=paciente)

    archivos_data = [
        {
            "id": a.id,
            "url": a.archivo.url,
            "nombre": a.archivo.name.split("/")[-1]
        }
        for a in archivos
    ]

    data = {
        "id": paciente.id,
        "nombre": paciente.nombre,
        "email": paciente.email,
        "dni": paciente.dni,
        "telefono": paciente.telefono,
        "direccion": paciente.direccion,

        # ANAMNESIS
        "alergias_conocidas": paciente.alergias_conocidas,
        "emfermedades_previas": paciente.emfermedades_previas,
        "antecentes_quirurgicos": paciente.antecentes_quirurgicos,
        "antecedentes_familiares": paciente.antecedentes_familiares,
        "medicamentos_actuales": paciente.medicamentos_actuales,
        "habitos": paciente.habitos,
        "relato_clinico": paciente.relato_clinico,

        # EXAMEN FÍSICO
        "edad": paciente.edad,
        "peso": paciente.peso,
        "altura": paciente.altura,
        "presion_arterial": paciente.presion_arterial,
        "frecuencia_cardiaca": paciente.frecuencia_cardiaca,
        "frecuencia_respiratoria": paciente.frecuencia_respiratoria,
        "temperatura": paciente.temperatura,
        "tipo_de_sangre": paciente.tipo_de_sangre,
        "descripcion_examen_fisico": paciente.descripcion_examen_fisico,

        # ARCHIVOS
        "archivos": archivos_data
    }

    return JsonResponse(data)
