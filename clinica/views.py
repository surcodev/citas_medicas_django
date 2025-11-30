from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse


def lista_citas(request):

    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clinica:lista_citas')  # redirige para evitar re-envío del formulario
    else:
        form = CitaForm()

    citas = Cita.objects.all()
    pacientes = Paciente.objects.all()

    return render(request, 'clinica/citas_medicas.html', {
        'citas': citas,
        'form': form,
        'pacientes': pacientes,   # <- aquí
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

def lista_pacientes(request):

    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')  # redirige para evitar re-envío del formulario
    else:
        form = PacienteForm()

    pacientes = Paciente.objects.all()

    return render(request, 'clinica/lista_pacientes.html', {
        'pacientes': pacientes,
        'form': form
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