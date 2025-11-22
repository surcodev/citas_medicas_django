from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from partidas_planos.models import User
from django.contrib.auth.hashers import make_password
from django.db.models.functions import Substr
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Sum, Q

from .forms import *
from .models import *

def home_ta(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'centro_costos/home_ta.html')
def home_cc(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'centro_costos/home_cc.html')

def centro_costos_home(request):
    ngs = NuevoGasto.objects.filter(flag=True)
    print(ngs)
    form = NuevoGastoForm()
    return render(request, 'centro_costos/home.html', {
        'ngs': ngs,
        'form': form,
    })

def agregar_nuevo_gasto(request):
    if request.method == 'POST':
        form = NuevoGastoForm(request.POST)
        if form.is_valid():
            try:
                nuevo_gasto = NuevoGasto.objects.filter(flag=False).first()  # Buscamos el primer flag=False
                if nuevo_gasto:
                    # Actualizamos los campos con los datos del formulario
                    nuevo_gasto.nombre = form.cleaned_data['nombre']
                    nuevo_gasto.flag = True
                    nuevo_gasto.save()
            except NuevoGasto.DoesNotExist:
                pass  # Si no existe ninguno con flag=False, no hacemos nada
    return redirect('centro_costos:home')


@login_required
def lista_actividades(request):
    form = ActividadForm()

    if request.method == 'POST':
        # Verificamos si se eligió "otros" y se escribió un nuevo centro de costos
        nuevo_centro = request.POST.get('nuevo_centro_de_costos', '').strip()
        if nuevo_centro:
            centro_obj, created = CentroDeCostos.objects.get_or_create(nombre=nuevo_centro)
            request.POST = request.POST.copy()
            request.POST['centro_de_costos'] = centro_obj.id

        form = ActividadForm(request.POST)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_actividades')

    actividades = Actividad.objects.all()
    centros_de_costos = CentroDeCostos.objects.all()

    return render(request, 'centro_costos/lista_actividades.html', {
        'form': form,
        'actividades': actividades,
        'centros_de_costos': centros_de_costos,
    })

@login_required
def editar_actividad(request):
    if request.method == 'POST':
        actividad_id = request.POST.get('id')
        actividad = get_object_or_404(Actividad, id=actividad_id)

        # Creamos el formulario con los datos enviados
        form = ActividadForm(request.POST, instance=actividad)

        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_actividades')
        else:
            centros_de_costos = CentroDeCostos.objects.all()
            print(form.errors)
            return render(request, 'centro_costos/lista_actividades.html', {
                'form': form,
                'centros_de_costos': centros_de_costos,
                'errores': form.errors,
            })

    # Si es GET, cargamos el proyecto y los centros disponibles
    actividad_id = request.GET.get('id')
    actividad = get_object_or_404(Actividad, id=actividad_id)
    centros_de_costos = CentroDeCostos.objects.all()

    return render(request, 'centro_costos/lista_actividades.html', {
        'actividad': actividad,
        'centros_de_costos': centros_de_costos,
    })

def eliminar_actividad(request, doc_id):
    doc = get_object_or_404(Actividad, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_actividades')

#########################################################################################
from django.core.cache import cache

@login_required
def lista_gasto_ta_2020(request):
    form = GastoTA2020Form()

    if request.method == 'POST':
        # Verificamos si se eligió "otros" y se escribió un nuevo tipo de gasto
        nuevo_tipo = request.POST.get('nuevo_tipo_gasto', '').strip()
        if nuevo_tipo:
            tipo_obj, created = TipoDeGasto.objects.get_or_create(nombre=nuevo_tipo)
            request.POST = request.POST.copy()
            request.POST['tipo_gasto'] = tipo_obj.id

        form = GastoTA2020Form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_gastos')

    gastos = GastoTA2020.objects.all().order_by('fecha')
    # gastos = GastoTA2020.objects.filter(fecha__year=2023).order_by('fecha')
    tipos_de_gasto = TipoDeGasto.objects.all()
    actividades = Actividad.objects.all()

    return render(request, 'centro_costos/lista_gastos.html', {
        'form': form,
        'gastos': gastos,
        'tipos_de_gasto': tipos_de_gasto,
        'actividades': actividades,
    })

@login_required
def editar_gasto_ta_2020(request):
    if request.method == 'POST':
        gasto_id = request.POST.get('id')
        gasto = get_object_or_404(GastoTA2020, id=gasto_id)

        form = GastoTA2020Form(request.POST, instance=gasto)

        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_gastos')
        else:
            tipos_de_gasto = TipoDeGasto.objects.all()
            print(tipos_de_gasto)
            print(form.errors)
            return render(request, 'centro_costos/lista_gastos.html', {
                'form': form,
                'tipos_de_gasto': tipos_de_gasto,  # Asegúrate de que este esté presente en el contexto
                'errores': form.errors,
            })

    # Si es GET
    gasto_id = request.GET.get('id')
    gasto = get_object_or_404(Gasto, id=gasto_id)
    tipos_de_gasto = TipoDeGasto.objects.all()
    return render(request, 'centro_costos/lista_gastos.html', {
        'gasto': gasto,
        'tipos_de_gasto': tipos_de_gasto,  # También aquí debes pasar los tipos de gasto
    })

def eliminar_gasto_ta_2020(request, doc_id):
    doc = get_object_or_404(GastoTA2020, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastos')

#############################################################################

@login_required
def lista_canta_callao(request):
    form = CantaCallaoForm()

    if request.method == 'POST':
        form = CantaCallaoForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_canta_callao')

    canta_callao = CantaCallao.objects.annotate(
        anio=Substr('codigo', 8, 2),       # Año: caracteres 8 y 9 (por ejemplo, '19')
        idinterno=Substr('codigo', 4, 3),  # ID interno: caracteres 4-6 (por ejemplo, '001')
    ).order_by('anio', 'idinterno')
    return render(request, 'centro_costos/lista_canta_callao.html', {
        'form': form,
        'canta_callao': canta_callao,
    })

@login_required
def editar_canta_callao(request):
    if request.method == 'POST':
        canta_callao_id = request.POST.get('id')
        canta_callao = get_object_or_404(CantaCallao, id=canta_callao_id)

        form = CantaCallaoForm(request.POST, instance=canta_callao)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_canta_callao')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_canta_callao')

    return redirect('centro_costos:lista_canta_callao')

def eliminar_canta_callao(request, doc_id):
    doc = get_object_or_404(CantaCallao, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_canta_callao')

######################################################################################################
# LISTA GENERAL








from .models import *
from .forms import *

@login_required
def lista_gasto_ta_2024(request):
    form = GastoN1Form()

    if request.method == 'POST':
        form = GastoN1Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN1')  # O el nombre de tu vista actual
        else:
            # Imprimir errores en consola si el formulario no es válido
            print("Errores del formulario:", form.errors)

    gastoN1 = GastoN1.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN1 = nuevo_gastos[1] if nuevo_gastos.count() > 1 else None

    # --- Cálculo de totales ---
    total_soles_egresos = gastoN1.filter(es_ingreso=False).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles_ingresos = gastoN1.filter(es_ingreso=True).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles = total_soles_egresos - total_soles_ingresos

    total_dolares_egresos = gastoN1.filter(es_ingreso=False).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares_ingresos = gastoN1.filter(es_ingreso=True).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares = total_dolares_egresos - total_dolares_ingresos

    anios_unicos = (
        GastoN1.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'centro_costos/lista_gastoN1.html', {
        'form': form,
        'gasto_general': gastoN1,
        'nombreN1': nombreN1,
        'anios': anios_unicos,
        'total_soles': total_soles,
        'total_dolares': total_dolares,
    })

def editar_gasto_ta_2024(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN1, id=gasto_general_id)

        # Guardamos los valores originales
        fecha_original = gasto_general.fecha_registro
        editor_original = gasto_general.editor

        form = GastoN1Form(request.POST, request.FILES, instance=gasto_general)
        if form.is_valid():
            gasto_editado = form.save(commit=False)

            # Restauramos los valores originales
            gasto_editado.fecha_registro = fecha_original
            gasto_editado.editor = editor_original

            gasto_editado.save()
            return redirect('centro_costos:lista_gastoN1')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_gastoN1')

    return redirect('centro_costos:lista_gastoN1')


def eliminar_gasto_ta_2024(request, doc_id):
    doc = get_object_or_404(GastoN1, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN1')


@login_required
def lista_gastoN2(request):
    form = GastoN2Form()

    if request.method == 'POST':
        form = GastoN2Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN2')  # O el nombre de tu vista actual
        else:
            # Imprimir errores en consola si el formulario no es válido
            print("Errores del formulario:", form.errors)

    from django.db.models.functions import Substr, Cast
    from django.db.models import IntegerField
    gastoN2 = GastoN2.objects.annotate(
        numero=Cast(Substr('codigo', 4, 3), IntegerField()),
        anio=Cast(Substr('codigo', 8, 2), IntegerField()),
    ).order_by('-anio', '-numero')

    nuevo_gastos = NuevoGasto.objects.all()
    nombreN2 = nuevo_gastos[1] if nuevo_gastos.count() > 1 else None

    # --- Cálculo de totales ---
    total_soles_egresos = gastoN2.filter(es_ingreso=False).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles_ingresos = gastoN2.filter(es_ingreso=True).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles = total_soles_egresos - total_soles_ingresos

    total_dolares_egresos = gastoN2.filter(es_ingreso=False).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares_ingresos = gastoN2.filter(es_ingreso=True).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares = total_dolares_egresos - total_dolares_ingresos

    anios_unicos = (
        GastoN2.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'centro_costos/lista_gastoN2.html', {
        'form': form,
        'gasto_general': gastoN2,
        'nombreN2': nombreN2,
        'anios': anios_unicos,
        'total_soles': total_soles,
        'total_dolares': total_dolares,
    })


def editar_gastoN2(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN2, id=gasto_general_id)

        # Guardamos los valores originales
        fecha_original = gasto_general.fecha_registro
        editor_original = gasto_general.editor

        form = GastoN2Form(request.POST, request.FILES, instance=gasto_general)
        if form.is_valid():
            gasto_editado = form.save(commit=False)

            # Restauramos los valores originales
            gasto_editado.fecha_registro = fecha_original
            gasto_editado.editor = editor_original

            gasto_editado.save()
            return redirect('centro_costos:lista_gastoN2')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_gastoN2')
    return redirect('centro_costos:lista_gastoN2')

def eliminar_gastoN2(request, doc_id):
    doc = get_object_or_404(GastoN2, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN2')


@login_required
def lista_gastoN3(request):
    form = GastoN3Form()

    if request.method == 'POST':
        form = GastoN3Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN3')  # O el nombre de tu vista actual
        else:
            # Imprimir errores en consola si el formulario no es válido
            print("Errores del formulario:", form.errors)

    gastoN3 = GastoN3.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN3 = nuevo_gastos[2] if nuevo_gastos.count() > 1 else None

    # --- Cálculo de totales ---
    total_soles_egresos = gastoN3.filter(es_ingreso=False).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles_ingresos = gastoN3.filter(es_ingreso=True).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles = total_soles_egresos - total_soles_ingresos

    total_dolares_egresos = gastoN3.filter(es_ingreso=False).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares_ingresos = gastoN3.filter(es_ingreso=True).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares = total_dolares_egresos - total_dolares_ingresos

    anios_unicos = (
        GastoN3.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'centro_costos/lista_gastoN3.html', {
        'form': form,
        'gasto_general': gastoN3,
        'nombreN3': nombreN3,
        'anios': anios_unicos,
        'editores': GastoN3.objects.values_list('editor', flat=True).distinct(),
        'total_soles': total_soles,
        'total_dolares': total_dolares,
    })

# RIMAC
def editar_gastoN3(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN3, id=gasto_general_id)

        # Guardamos los valores originales
        fecha_original = gasto_general.fecha_registro
        editor_original = gasto_general.editor

        form = GastoN3Form(request.POST, request.FILES, instance=gasto_general)
        if form.is_valid():
            gasto_editado = form.save(commit=False)

            # Restauramos los valores originales
            gasto_editado.fecha_registro = fecha_original
            gasto_editado.editor = editor_original

            gasto_editado.save()
            return redirect('centro_costos:lista_gastoN3')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_gastoN3')

    return redirect('centro_costos:lista_gastoN3')


def eliminar_gastoN3(request, doc_id):
    doc = get_object_or_404(GastoN3, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN3')


@login_required
def lista_gastoN4(request):
    form = GastoN4Form()

    if request.method == 'POST':
        form = GastoN4Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN4')  # O el nombre de tu vista actual
        else:
            # Imprimir errores en consola si el formulario no es válido
            print("Errores del formulario:", form.errors)

    gastoN4 = GastoN4.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN4 = nuevo_gastos[3] if nuevo_gastos.count() > 1 else None

    # --- Cálculo de totales ---
    total_soles_egresos = gastoN4.filter(es_ingreso=False).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles_ingresos = gastoN4.filter(es_ingreso=True).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles = total_soles_egresos - total_soles_ingresos

    total_dolares_egresos = gastoN4.filter(es_ingreso=False).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares_ingresos = gastoN4.filter(es_ingreso=True).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares = total_dolares_egresos - total_dolares_ingresos

    anios_unicos = (
        GastoN4.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'centro_costos/lista_gastoN4.html', {
        'form': form,
        'gasto_general': gastoN4,
        'nombreN4': nombreN4,
        'anios': anios_unicos,
        'editores': GastoN4.objects.values_list('editor', flat=True).distinct(),
        'total_soles': total_soles,
        'total_dolares': total_dolares,
    })

def editar_gastoN4(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN4, id=gasto_general_id)

        # Guardamos los valores originales
        fecha_original = gasto_general.fecha_registro
        editor_original = gasto_general.editor

        form = GastoN4Form(request.POST, request.FILES, instance=gasto_general)
        if form.is_valid():
            gasto_editado = form.save(commit=False)

            # Restauramos los valores originales
            gasto_editado.fecha_registro = fecha_original
            gasto_editado.editor = editor_original

            gasto_editado.save()
            return redirect('centro_costos:lista_gastoN4')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_gastoN4')

    return redirect('centro_costos:lista_gastoN4')


def eliminar_gastoN4(request, doc_id):
    doc = get_object_or_404(GastoN4, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN4')


@login_required
def lista_gastoN5(request):
    form = GastoN5Form()

    if request.method == 'POST':
        form = GastoN5Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN5')  # O el nombre de tu vista actual
        else:
            # Imprimir errores en consola si el formulario no es válido
            print("Errores del formulario:", form.errors)

    gastoN5 = GastoN5.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN5 = nuevo_gastos[4] if nuevo_gastos.count() > 1 else None

    # --- Cálculo de totales ---
    total_soles_egresos = gastoN5.filter(es_ingreso=False).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles_ingresos = gastoN5.filter(es_ingreso=True).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles = total_soles_egresos - total_soles_ingresos

    total_dolares_egresos = gastoN5.filter(es_ingreso=False).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares_ingresos = gastoN5.filter(es_ingreso=True).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares = total_dolares_egresos - total_dolares_ingresos

    anios_unicos = (
        GastoN5.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'centro_costos/lista_gastoN5.html', {
        'form': form,
        'gasto_general': gastoN5,
        'nombreN5': nombreN5,
        'anios': anios_unicos,
        'editores': GastoN5.objects.values_list('editor', flat=True).distinct(),
        'total_soles': total_soles,
        'total_dolares': total_dolares,
    })

def editar_gastoN5(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN5, id=gasto_general_id)

        # Guardamos los valores originales
        fecha_original = gasto_general.fecha_registro
        editor_original = gasto_general.editor

        form = GastoN5Form(request.POST, request.FILES, instance=gasto_general)
        if form.is_valid():
            gasto_editado = form.save(commit=False)

            # Restauramos los valores originales
            gasto_editado.fecha_registro = fecha_original
            gasto_editado.editor = editor_original

            gasto_editado.save()
            return redirect('centro_costos:lista_gastoN5')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_gastoN5')

    return redirect('centro_costos:lista_gastoN5')


def eliminar_gastoN5(request, doc_id):
    doc = get_object_or_404(GastoN5, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN5')


@login_required
def lista_gastoN6(request):
    form = GastoN6Form()

    if request.method == 'POST':
        form = GastoN6Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN6')

    gastoN6 = GastoN6.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN6 = nuevo_gastos[5] if nuevo_gastos.count() > 5 else None
    return render(request, 'centro_costos/lista_gastoN6.html', {
        'form': form,
        'gasto_general': gastoN6,
        'nombreN6': nombreN6
    })

def editar_gastoN6(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN6, id=gasto_general_id)

        form = GastoN6Form(request.POST, request.FILES, instance=gasto_general)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_gastoN6')
        else:
            print(form.errors)  # Muy útil para debug
            return redirect('centro_costos:lista_gastoN6')  # o puedes mostrar un error

    return redirect('centro_costos:lista_gastoN6')


def eliminar_gastoN6(request, doc_id):
    doc = get_object_or_404(GastoN6, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN6')


@login_required
def lista_gastoN7(request):
    form = GastoN7Form()

    if request.method == 'POST':
        form = GastoN7Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN7')  # O el nombre de tu vista actual
        else:
            # Imprimir errores en consola si el formulario no es válido
            print("Errores del formulario:", form.errors)

    gastoN7 = GastoN7.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN7 = nuevo_gastos[6] if nuevo_gastos.count() > 1 else None

    # --- Cálculo de totales ---
    total_soles_egresos = gastoN7.filter(es_ingreso=False).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles_ingresos = gastoN7.filter(es_ingreso=True).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles = total_soles_egresos - total_soles_ingresos

    total_dolares_egresos = gastoN7.filter(es_ingreso=False).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares_ingresos = gastoN7.filter(es_ingreso=True).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares = total_dolares_egresos - total_dolares_ingresos

    anios_unicos = (
        GastoN7.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'centro_costos/lista_gastoN7.html', {
        'form': form,
        'gasto_general': gastoN7,
        'nombreN7': nombreN7,
        'anios': anios_unicos,
        'editores': GastoN7.objects.values_list('editor', flat=True).distinct(),
        'total_soles': total_soles,
        'total_dolares': total_dolares,
    })

def editar_gastoN7(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN7, id=gasto_general_id)

        # Guardamos los valores originales
        fecha_original = gasto_general.fecha_registro
        editor_original = gasto_general.editor

        form = GastoN7Form(request.POST, request.FILES, instance=gasto_general)
        if form.is_valid():
            gasto_editado = form.save(commit=False)

            # Restauramos los valores originales
            gasto_editado.fecha_registro = fecha_original
            gasto_editado.editor = editor_original

            gasto_editado.save()
            return redirect('centro_costos:lista_gastoN7')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_gastoN7')
    return redirect('centro_costos:lista_gastoN7')


def eliminar_gastoN7(request, doc_id):
    doc = get_object_or_404(GastoN7, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN7')


@login_required
def lista_gastoN8(request):
    form = GastoN8Form()

    if request.method == 'POST':
        form = GastoN8Form(request.POST, request.FILES)
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)
            seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
            seguimiento_editado.save()
            return redirect('centro_costos:lista_gastoN8')  # O el nombre de tu vista actual
        else:
            # Imprimir errores en consola si el formulario no es válido
            print("Errores del formulario:", form.errors)

    gastoN8 = GastoN8.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN8 = nuevo_gastos[7] if nuevo_gastos.count() > 1 else None

    # --- Cálculo de totales ---
    total_soles_egresos = gastoN8.filter(es_ingreso=False).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles_ingresos = gastoN8.filter(es_ingreso=True).aggregate(total=Sum('monto_soles'))['total'] or 0
    total_soles = total_soles_egresos - total_soles_ingresos

    total_dolares_egresos = gastoN8.filter(es_ingreso=False).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares_ingresos = gastoN8.filter(es_ingreso=True).aggregate(total=Sum('monto_dolares'))['total'] or 0
    total_dolares = total_dolares_egresos - total_dolares_ingresos

    anios_unicos = (
        GastoN8.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'centro_costos/lista_gastoN8.html', {
        'form': form,
        'gasto_general': gastoN8,
        'nombreN8': nombreN8,
        'anios': anios_unicos,
        'editores': GastoN8.objects.values_list('editor', flat=True).distinct(),
        'total_soles': total_soles,
        'total_dolares': total_dolares,
    })

def editar_gastoN8(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN8, id=gasto_general_id)

        # Guardamos los valores originales
        fecha_original = gasto_general.fecha_registro
        editor_original = gasto_general.editor

        form = GastoN8Form(request.POST, request.FILES, instance=gasto_general)
        if form.is_valid():
            gasto_editado = form.save(commit=False)

            # Restauramos los valores originales
            gasto_editado.fecha_registro = fecha_original
            gasto_editado.editor = editor_original

            gasto_editado.save()
            return redirect('centro_costos:lista_gastoN8')
        else:
            print(form.errors)
            return redirect('centro_costos:lista_gastoN8')

    return redirect('centro_costos:lista_gastoN8')



def eliminar_gastoN8(request, doc_id):
    doc = get_object_or_404(GastoN8, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN8')


@login_required
def lista_gastoN9(request):
    form = GastoN9Form()

    if request.method == 'POST':
        form = GastoN9Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_gastoN9')

    gastoN9 = GastoN9.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN9 = nuevo_gastos[8] if nuevo_gastos.count() > 8 else None

    anios_unicos = (
        GastoN9.objects
        .exclude(fecha__isnull=True)  # ✅ Excluye las fechas NULL
        .annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    expedientes_unicos = (
        GastoN9.objects
        .exclude(expediente__isnull=True)      # ✅ Excluye NULL
        .exclude(expediente__exact="")         # ✅ Excluye cadenas vacías
        .values_list('expediente', flat=True)
        .distinct()
        .order_by('expediente')               # ✅ Orden alfabético
    )

    return render(request, 'centro_costos/lista_gastoN9.html', {
        'form': form,
        'gasto_general': gastoN9,
        'nombreN9': nombreN9,
        'anios': anios_unicos,
        'expedientes_unicos': expedientes_unicos,
    })

def editar_gastoN9(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN9, id=gasto_general_id)

        form = GastoN9Form(request.POST, request.FILES, instance=gasto_general)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_gastoN9')
        else:
            print(form.errors)  # Muy útil para debug
            return redirect('centro_costos:lista_gastoN9')  # o puedes mostrar un error

    return redirect('centro_costos:lista_gastoN9')


def eliminar_gastoN9(request, doc_id):
    doc = get_object_or_404(GastoN9, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN9')


@login_required
def lista_gastoN10(request):
    form = GastoN10Form()

    if request.method == 'POST':
        form = GastoN1Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_gastoN10')

    gastoN10 = GastoN10.objects.all()
    nuevo_gastos = NuevoGasto.objects.all()
    nombreN10 = nuevo_gastos[9] if nuevo_gastos.count() > 9 else None
    return render(request, 'centro_costos/lista_gastoN10.html', {
        'form': form,
        'gasto_general': gastoN10,
        'nombreN10': nombreN10
    })

def editar_gastoN10(request):
    if request.method == 'POST':
        gasto_general_id = request.POST.get('id')
        gasto_general = get_object_or_404(GastoN10, id=gasto_general_id)

        form = GastoN10Form(request.POST, request.FILES, instance=gasto_general)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('centro_costos:lista_gastoN10')
        else:
            print(form.errors)  # Muy útil para debug
            return redirect('centro_costos:lista_gastoN10')  # o puedes mostrar un error

    return redirect('centro_costos:lista_gastoN10')


def eliminar_gastoN10(request, doc_id):
    doc = get_object_or_404(GastoN10, id=doc_id)
    doc.delete()
    return redirect('centro_costos:lista_gastoN10')
