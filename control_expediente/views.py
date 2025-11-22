from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.db.models import DateTimeField, ExpressionWrapper, F
from decimal import Decimal
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import connection
import openpyxl
from django.http import HttpResponse
from datetime import date


def exportar_gastos_excel(request, caso_id):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Gastos"

    # Encabezados
    headers = ["Expediente", "Resolución", "Fecha", "Detalle", "Código Pago", "Gasto (S/)", "Gasto ($)"]
    ws.append(headers)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.expediente,
                s.resolucion,
                g.fecha,
                g.detalle,
                g.codigo_pago,
                g.gastos_soles,
                g.gastos_dolares
            FROM control_expediente_gasto AS g
            INNER JOIN control_expediente_seguimiento AS s ON g.seguimiento_id = s.id
            INNER JOIN control_expediente_casojudicial AS c ON s.caso_id = c.id
            WHERE c.id = %s
            ORDER BY s.resolucion ASC
        """, [caso_id])
        for row in cursor.fetchall():
            ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="gastos_expediente_{caso_id}.xlsx"'
    wb.save(response)

def exportar_gastos_fiscal_excel(request, caso_id):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Gastos"

    # Encabezados
    headers = ["Expediente Penal", "Resolución", "Fecha", "Detalle", "Código Pago", "Gasto (S/)", "Gasto ($)"]
    ws.append(headers)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.carpeta_fiscal,
                s.resolucion,
                g.fecha,
                g.detalle,
                g.codigo_pago,
                g.gastos_soles,
                g.gastos_dolares
            FROM control_expediente_gastofiscal AS g
            INNER JOIN control_expediente_seguimientofiscal AS s ON g.seguimiento_id = s.id
            INNER JOIN control_expediente_carpetafiscal AS c ON s.caso_id = c.id
            WHERE c.id = %s
            ORDER BY s.resolucion ASC
        """, [caso_id])
        for row in cursor.fetchall():
            ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="gastos_expediente_{caso_id}.xlsx"'
    wb.save(response)
    return response



@login_required
def lista_registros_actividad(request):
    registro_actividad = RegistroActividad.objects.all().order_by('-fecha')
    
    usuarios_legales = (
        User.objects.filter(is_active=True)
        .exclude(username__in=['plupa', 'cdiaz'])
        .order_by('first_name')
    )

    return render(request, 'control_expediente/registro_actividad.html', {
        'registro_actividad': registro_actividad,
        'usuarios_legales': usuarios_legales,
    })


from django.views.decorators.cache import never_cache
#@never_cache
@login_required
def lista_expediente(request):
    form = CasoJudicialForm()

    if request.method == 'POST':
        form = CasoJudicialForm(request.POST)
        if form.is_valid():
            nuevo = form.save(commit=False)
            nuevo.concluido = True
            nuevo.save()

            RegistroActividad.objects.create(
                nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha=timezone.now(),
                actividad=f"[EXP GENERAL] Registró un nuevo expediente: {nuevo.expediente}"
            )
            return redirect('control_expediente:lista_expediente')

    # ==============================
    # 🔹 CONSULTA OPTIMIZADA Y ROBUSTA
    # ==============================
    from django.db.models import OuterRef, Subquery, DateField, TextField
    from datetime import date
    from .models import CasoJudicial, Seguimiento

    hoy = date.today()

    # 1) Subconsulta para obtener el seguimiento con la próxima fecha_alerta (>= hoy)
    #    Orden: fecha_alerta asc (el más cercano). Si hay empates en fecha, tomamos el más reciente por fecha_registro DESC
    subquery_seguimiento_alerta = (
        Seguimiento.objects
        .filter(caso=OuterRef('pk'), fecha_alerta__gte=hoy)
        .order_by('fecha_alerta', '-fecha_registro')
    )

    # 2) De esa subconsulta sacamos el id del seguimiento seleccionado
    subquery_seguimiento_id = subquery_seguimiento_alerta.values('id')[:1]

    # 3) Subquery para obtener la fecha_alerta (de la fila seleccionada)
    subquery_fecha_alerta = subquery_seguimiento_alerta.values('fecha_alerta')[:1]

    # 4) Usamos el id para traer el pendiente exactamente de esa fila
    subquery_pendiente_alerta = (
        Seguimiento.objects
        .filter(id=Subquery(subquery_seguimiento_id))
        .values('pendiente')[:1]
    )

    # 5) Anotamos en CasoJudicial
    caso_judiciales = (
        CasoJudicial.objects
        .annotate(
            proxima_alerta=Subquery(subquery_fecha_alerta, output_field=DateField()),
            pendiente_alerta=Subquery(subquery_pendiente_alerta, output_field=TextField())
        )
        .exclude(concluido=False)
        .select_related('responsable')
        .order_by('codigo')  # 👈 orden ascendente por item
    )

    # Calculamos color de alerta (rápido en memoria)
    for cj in caso_judiciales:
        if cj.proxima_alerta:
            dias_restantes = (cj.proxima_alerta - hoy).days
            if dias_restantes <= 5:
                cj.alerta_color = "danger"
            elif dias_restantes <= 15:
                cj.alerta_color = "warning"
            else:
                cj.alerta_color = "success"
        else:
            cj.alerta_color = "secondary"

    # Especialidades únicas (para filtro)
    especialidades_unicas = (
        CasoJudicial.objects
        .exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    usuarios_legales = User.objects.filter(role=User.LEGAL, is_active=True).order_by('first_name')

    return render(request, 'control_expediente/home.html', {
        'form': form,
        'caso_judiciales': caso_judiciales,
        'especialidades': especialidades_unicas,
        'usuarios_legales': usuarios_legales,
    })

#####################################################################################################

@login_required
def lista_concluidos(request):
    form = CasoJudicialForm()

    if request.method == 'POST':
        form = CasoJudicialForm(request.POST)
        if form.is_valid():
            nuevo = form.save()
            RegistroActividad.objects.create(
                nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha=timezone.now(),
                actividad=f"Registró un nuevo expediente: {nuevo.expediente}"
            )
            return redirect('control_expediente:lista_concluidos')

    # ==============================
    # 🔹 OPTIMIZACIÓN AQUÍ
    # ==============================
    hoy = date.today()

    from .models import Seguimiento

    # Traemos todos los casos con la próxima fecha_alerta calculada
    caso_judiciales = (
        CasoJudicial.objects
        .exclude(concluido=True)
        .prefetch_related('seguimientos')
    )


    especialidades_unicas = (
        CasoJudicial.objects.exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    usuarios_legales = User.objects.filter(role=User.LEGAL, is_active=True).order_by('first_name')

    return render(request, 'control_expediente/concluidos.html', {
        'form': form,
        'caso_judiciales': caso_judiciales,
        'especialidades': especialidades_unicas,
        'usuarios_legales': usuarios_legales,
    })


def ver_seguimiento_concluido(request, caso_id):
    caso = get_object_or_404(CasoJudicial, id=caso_id)

    # Formularios por defecto
    seguimiento_form = SeguimientoForm()
    gasto_form = GastoForm()

    if request.method == 'POST':
        tipo_formulario = request.POST.get('tipo_formulario')
        seguimiento_id = request.POST.get('seguimiento_id')

        # NUEVO GASTO A SEGUIMIENTO
        if tipo_formulario == 'gasto' and seguimiento_id:
            seguimiento = get_object_or_404(Seguimiento, id=seguimiento_id)
            gasto_form = GastoForm(request.POST, request.FILES)
            if gasto_form.is_valid():
                nuevo_gasto = gasto_form.save(commit=False)
                nuevo_gasto.seguimiento = seguimiento

                # Guardar el nombre del editor actual
                nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
                nuevo_gasto.editor = nombre_editor if nombre_editor else request.user.username
                nuevo_gasto.save()

                RegistroActividad.objects.create(
                    nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha=timezone.now(),
                    actividad=f"Registró un nuevo gasto: {nuevo_gasto.seguimiento.caso.expediente}"
                )

                return redirect('control_expediente:ver_seguimiento', caso_id=caso.id)

        # EDITAR SEGUIMIENTO EXISTENTE
        elif tipo_formulario == 'editar_seguimiento' and seguimiento_id:
            seguimiento = get_object_or_404(Seguimiento, id=seguimiento_id)
            seguimiento_form = SeguimientoForm(request.POST, request.FILES, instance=seguimiento)
            if seguimiento_form.is_valid():
                seguimiento_editado = seguimiento_form.save(commit=False)
                seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
                seguimiento_editado.save()
                return redirect('control_expediente:ver_seguimiento', caso_id=caso.id)

        # NUEVO SEGUIMIENTO
        else:
            seguimiento_form = SeguimientoForm(request.POST, request.FILES)
            if seguimiento_form.is_valid():
                nuevo_seguimiento = seguimiento_form.save(commit=False)
                nuevo_seguimiento.caso = caso
                nuevo_seguimiento.usuario = request.user
                nuevo_seguimiento.editor = f"{request.user.first_name} {request.user.last_name}"
                nuevo_seguimiento.save()
                return redirect('control_expediente:ver_seguimiento', caso_id=caso.id)

    # --- 🔹 Obtener los seguimientos del caso ---
    seguimientos = (
        caso.seguimientos
        .annotate(
            fecha_seguimiento_cast=ExpressionWrapper(F('fecha_seguimiento'), output_field=DateTimeField()),
            fecha_registro_cast=ExpressionWrapper(F('fecha_registro'), output_field=DateTimeField())
        )
        .prefetch_related('gastos')
        .order_by('-fecha_seguimiento_cast', '-fecha_registro_cast')
    )

    # --- 🔹 Obtener la fecha del primer gasto del caso ---
    primer_gasto = (
        Gasto.objects
        .filter(seguimiento__caso=caso)
        .order_by('fecha')
        .first()
    )
    primera_fecha_gasto = primer_gasto.fecha if primer_gasto else None

    # --- 🔹 Calcular totales ---
    total_soles = 0
    total_dolares = 0
    for seguimiento in seguimientos:
        for gasto in seguimiento.gastos.all():
            total_soles += gasto.gastos_soles or 0
            total_dolares += gasto.gastos_dolares or 0

        if seguimiento.usuario:
            seguimiento.nombre_usuario = f"{seguimiento.usuario.first_name} {seguimiento.usuario.last_name}"
        else:
            seguimiento.nombre_usuario = "—"

    especialidades_unicas = (
        CasoJudicial.objects.exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    # --- 🔹 Consulta SQL filtrando desde la fecha del primer gasto ---
    with connection.cursor() as cursor:
        if primera_fecha_gasto:
            cursor.execute("""
                SELECT 
                    c.expediente,
                    s.resolucion,
                    g.fecha,
                    g.detalle,
                    g.codigo_pago,
                    g.gastos_soles,
                    g.gastos_dolares
                FROM control_expediente_gasto AS g
                INNER JOIN control_expediente_seguimiento AS s ON g.seguimiento_id = s.id
                INNER JOIN control_expediente_casojudicial AS c ON s.caso_id = c.id
                WHERE c.id = %s AND g.fecha >= %s
                ORDER BY s.resolucion ASC
            """, [caso_id, primera_fecha_gasto])
        else:
            cursor.execute("""
                SELECT 
                    c.expediente,
                    s.resolucion,
                    g.fecha,
                    g.detalle,
                    g.codigo_pago,
                    g.gastos_soles,
                    g.gastos_dolares
                FROM control_expediente_gasto AS g
                INNER JOIN control_expediente_seguimiento AS s ON g.seguimiento_id = s.id
                INNER JOIN control_expediente_casojudicial AS c ON s.caso_id = c.id
                WHERE c.id = %s
                ORDER BY s.resolucion ASC
            """, [caso_id])
        rows = cursor.fetchall()

    gastos_expediente = [
        {
            "expediente": row[0],
            "resolucion": row[1],
            "fecha": row[2],
            "detalle": row[3],
            "codigo_pago": row[4],
            "gastos_soles": row[5],
            "gastos_dolares": row[6],
        }
        for row in rows
    ]

    print(primera_fecha_gasto)

    context = {
        'caso': caso,
        'seguimientos': seguimientos,
        'form': seguimiento_form,
        'form2': gasto_form,
        'total_soles': total_soles,
        'total_dolares': total_dolares,
        'nombre_usuario': f"{request.user.first_name} {request.user.last_name}",
        'especialidades': especialidades_unicas,
        'gastos_expediente': gastos_expediente,
        'primera_fecha_gasto': primera_fecha_gasto,
    }

    return render(request, 'control_expediente/seguimientos_y_gastos_concluidos.html', context)

def editar_expediente_general_concluido(request):
    if request.method == 'POST':
        cj_id = request.POST.get('id')
        cj = get_object_or_404(CasoJudicial, id=cj_id)
        
        cj.concluido = not cj.concluido  # Alterna el valor de concluido
        cj.save()

        return redirect('control_expediente:lista_concluidos')

#####################################################################################################

def editar_expediente(request):
    if request.method == 'POST':
        cj_id = request.POST.get('id')
        cj = get_object_or_404(CasoJudicial, id=cj_id)

        print("CJ ID: ", cj_id)
        print("CJ ID: ", cj)

        form = CasoJudicialForm(request.POST, instance=cj)
        
        if form.is_valid():
            form.save()

            RegistroActividad.objects.create(
                nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha = timezone.now(),
                actividad = f"[EXP. GENERAL] Modificó el expediente: {form.save().expediente}"
            )

            return redirect('control_expediente:lista_expediente')
        else:
            return redirect('control_expediente:lista_expediente')
    return redirect('control_expediente:lista_expediente')

def eliminar_expediente(request, doc_id):
    doc = get_object_or_404(CasoJudicial, id=doc_id)
    doc.delete()

    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"[EXP. GENERAL] Eliminó el expediente: {doc.expediente}"
    )

    return redirect('control_expediente:lista_expediente')


def eliminar_exp_concluido(request, doc_id):
    doc = get_object_or_404(CasoJudicial, id=doc_id)
    doc.delete()

    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"[EXP GEN. CONCLUIDO] Eliminó el expediente: {doc.expediente}"
    )

    return redirect('control_expediente:lista_concluidos')


#####################################################################################################

def ver_seguimiento(request, caso_id):
    caso = get_object_or_404(CasoJudicial, id=caso_id)

    # Formularios por defecto
    seguimiento_form = SeguimientoForm()
    gasto_form = GastoForm()

    if request.method == 'POST':
        tipo_formulario = request.POST.get('tipo_formulario')
        seguimiento_id = request.POST.get('seguimiento_id')

        # NUEVO GASTO A SEGUIMIENTO
        if tipo_formulario == 'gasto' and seguimiento_id:
            seguimiento = get_object_or_404(Seguimiento, id=seguimiento_id)
            gasto_form = GastoForm(request.POST, request.FILES)
            if gasto_form.is_valid():
                nuevo_gasto = gasto_form.save(commit=False)
                nuevo_gasto.seguimiento = seguimiento

                # Guardar el nombre del editor actual
                nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
                nuevo_gasto.editor = nombre_editor if nombre_editor else request.user.username
                nuevo_gasto.save()

                RegistroActividad.objects.create(
                    nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha=timezone.now(),
                    actividad=f"[EXP. GENERAL] Registró un nuevo gasto en el expediente: {nuevo_gasto.seguimiento.caso.expediente}"
                )

                return redirect('control_expediente:ver_seguimiento', caso_id=caso.id)

        # EDITAR SEGUIMIENTO EXISTENTE
        elif tipo_formulario == 'editar_seguimiento' and seguimiento_id:
            seguimiento = get_object_or_404(Seguimiento, id=seguimiento_id)
            seguimiento_form = SeguimientoForm(request.POST, request.FILES, instance=seguimiento)
            if seguimiento_form.is_valid():
                seguimiento_editado = seguimiento_form.save(commit=False)
                seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
                seguimiento_editado.save()

                RegistroActividad.objects.create(
                    nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha=timezone.now(),
                    actividad=f"[EXP. GENERAL] Editó seguimiento del expediente: {nuevo_gasto.seguimiento.caso.expediente}"
                )

                return redirect('control_expediente:ver_seguimiento', caso_id=caso.id)

        # NUEVO SEGUIMIENTO
        else:
            seguimiento_form = SeguimientoForm(request.POST, request.FILES)
            if seguimiento_form.is_valid():
                nuevo_seguimiento = seguimiento_form.save(commit=False)
                nuevo_seguimiento.caso = caso
                nuevo_seguimiento.usuario = request.user
                nuevo_seguimiento.editor = f"{request.user.first_name} {request.user.last_name}"
                nuevo_seguimiento.save()

                RegistroActividad.objects.create(
                    nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha=timezone.now(),
                    actividad=f"[EXP. GENERAL] Agregó nuevo seguimiento en el expediente : {nuevo_seguimiento.caso.expediente}"
                )

                return redirect('control_expediente:ver_seguimiento', caso_id=caso.id)

    # --- 🔹 Obtener los seguimientos del caso ---
    seguimientos = (
        caso.seguimientos
        .annotate(
            fecha_seguimiento_cast=ExpressionWrapper(F('fecha_seguimiento'), output_field=DateTimeField()),
            fecha_registro_cast=ExpressionWrapper(F('fecha_registro'), output_field=DateTimeField())
        )
        .prefetch_related('gastos')
        .order_by('-fecha_seguimiento_cast', '-fecha_registro_cast')
    )

    # --- 🔹 Obtener la fecha del primer gasto del caso ---
    primer_gasto = (
        Gasto.objects
        .filter(seguimiento__caso=caso)
        .order_by('fecha')
        .first()
    )
    primera_fecha_gasto = primer_gasto.fecha if primer_gasto else None

    # --- 🔹 Calcular totales ---
    total_soles = 0
    total_dolares = 0
    for seguimiento in seguimientos:
        for gasto in seguimiento.gastos.all():
            total_soles += gasto.gastos_soles or 0
            total_dolares += gasto.gastos_dolares or 0

        if seguimiento.usuario:
            seguimiento.nombre_usuario = f"{seguimiento.usuario.first_name} {seguimiento.usuario.last_name}"
        else:
            seguimiento.nombre_usuario = "—"

    especialidades_unicas = (
        CasoJudicial.objects.exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    # --- 🔹 Consulta SQL filtrando desde la fecha del primer gasto ---
    with connection.cursor() as cursor:
        if primera_fecha_gasto:
            cursor.execute("""
                SELECT 
                    c.expediente,
                    s.resolucion,
                    g.fecha,
                    g.detalle,
                    g.codigo_pago,
                    g.gastos_soles,
                    g.gastos_dolares
                FROM control_expediente_gasto AS g
                INNER JOIN control_expediente_seguimiento AS s ON g.seguimiento_id = s.id
                INNER JOIN control_expediente_casojudicial AS c ON s.caso_id = c.id
                WHERE c.id = %s AND g.fecha >= %s
                ORDER BY s.resolucion ASC
            """, [caso_id, primera_fecha_gasto])
        else:
            cursor.execute("""
                SELECT 
                    c.expediente,
                    s.resolucion,
                    g.fecha,
                    g.detalle,
                    g.codigo_pago,
                    g.gastos_soles,
                    g.gastos_dolares
                FROM control_expediente_gasto AS g
                INNER JOIN control_expediente_seguimiento AS s ON g.seguimiento_id = s.id
                INNER JOIN control_expediente_casojudicial AS c ON s.caso_id = c.id
                WHERE c.id = %s
                ORDER BY s.resolucion ASC
            """, [caso_id])
        rows = cursor.fetchall()

    gastos_expediente = [
        {
            "expediente": row[0],
            "resolucion": row[1],
            "fecha": row[2],
            "detalle": row[3],
            "codigo_pago": row[4],
            "gastos_soles": row[5],
            "gastos_dolares": row[6],
        }
        for row in rows
    ]

    print(primera_fecha_gasto)

    context = {
        'caso': caso,
        'seguimientos': seguimientos,
        'form': seguimiento_form,
        'form2': gasto_form,
        'total_soles': total_soles,
        'total_dolares': total_dolares,
        'nombre_usuario': f"{request.user.first_name} {request.user.last_name}",
        'especialidades': especialidades_unicas,
        'gastos_expediente': gastos_expediente,
        'primera_fecha_gasto': primera_fecha_gasto,
    }

    return render(request, 'control_expediente/seguimientos_y_gastos.html', context)

def editar_seguimiento(request):
    if request.method == 'POST':
        seguimiento_id = request.POST.get('id')
        print("ID recibido en POST:", seguimiento_id)

        seguimiento = get_object_or_404(Seguimiento, id=seguimiento_id)

        form = SeguimientoForm(request.POST, request.FILES, instance=seguimiento)
        
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)

            # Guardar el nombre del editor actual
            nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
            seguimiento_editado.editor = nombre_editor if nombre_editor else request.user.username
            seguimiento_editado.save()

            RegistroActividad.objects.create(
                    nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha = timezone.now(),
                    actividad = f"[EXP. GENERAL] Modificó seguimiento del expediente: {seguimiento_editado.caso.expediente}"
                )

            return redirect('control_expediente:ver_seguimiento', caso_id=seguimiento.caso.id)
        else:
            print("Errores al editar seguimiento:", form.errors)
            return redirect('control_expediente:ver_seguimiento', caso_id=seguimiento.caso.id)

    return redirect('control_expediente:ver_seguimiento', caso_id=0)

def eliminar_seguimiento(request, seguimiento_id):
    seguimiento = get_object_or_404(Seguimiento, id=seguimiento_id)
    caso_id = seguimiento.caso.id  # Guardamos antes de eliminar
    seguimiento.delete()

    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"[EXP. GENERAL] Eliminó seguimiento del expediente: {seguimiento.caso.expediente}"
    )

    return redirect('control_expediente:ver_seguimiento', caso_id=caso_id)

def to_decimal(value, default="0"):
    """Convierte un valor a Decimal de forma segura."""
    try:
        if value in [None, ""]:
            return Decimal(default)
        return Decimal(str(value).replace(",", "."))  # Acepta "3,5"
    except (InvalidOperation, ValueError):
        return Decimal(default)

def editar_gasto(request):
    if request.method == 'POST':
        gasto_id = request.POST.get('id')
        gasto = get_object_or_404(Gasto, id=gasto_id)

        # Valores anteriores
        gasto_anterior_soles = gasto.gastos_soles or Decimal("0")
        gasto_anterior_dolares = gasto.gastos_dolares or Decimal("0")

        # Nuevos valores desde el formulario
        gasto_nuevo_soles = to_decimal(request.POST.get('gastos_soles'))
        gasto_nuevo_dolares = to_decimal(request.POST.get('gastos_dolares'))

        gasto.fecha = request.POST.get('fecha')
        gasto.detalle = request.POST.get('detalle')
        gasto.codigo_pago = request.POST.get('codigo_pago')
        gasto.tipo_gasto = request.POST.get('tipo_gasto')
        gasto.gastos_soles = gasto_nuevo_soles
        gasto.gastos_dolares = gasto_nuevo_dolares

        if 'pdf' in request.FILES:
            gasto.pdf = request.FILES['pdf']

        gasto.save()

        # print(request.POST.get('tipo_gasto'))
        # if request.POST.get('tipo_gasto') == 'Caja Chica':
        #     # Actualizar saldo del usuario
        #     request.user.saldo += gasto_anterior_soles + (gasto_anterior_dolares * Decimal("3.5"))
        #     request.user.saldo -= gasto_nuevo_soles + (gasto_nuevo_dolares * Decimal("3.5"))
        #     request.user.save()
        # else:
        #     request.user.saldo += gasto_anterior_soles + (gasto_anterior_dolares * Decimal("3.5"))

        RegistroActividad.objects.create(
            nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
            fecha=timezone.now(),
            actividad=f"[EXP. GENERAL] Modificó gasto del expediente: {gasto.seguimiento.caso.expediente}"
        )

        return redirect('control_expediente:ver_seguimiento', caso_id=gasto.seguimiento.caso.id)

@csrf_protect
def eliminar_gasto(request):
    gasto_id = request.POST.get('gasto_id')
    gasto = get_object_or_404(Gasto, id=gasto_id)
    caso_id = gasto.seguimiento.caso.id

    # --- Evitar error si saldo es None ---
    saldo_actual = request.user.saldo or Decimal("0")

    # --- Calcular monto a devolver ---
    monto = (gasto.gastos_soles or Decimal("0")) + ((gasto.gastos_dolares or Decimal("0")) * Decimal("3.5"))

    # --- Actualizar saldo del usuario ---
    request.user.saldo = saldo_actual + monto
    request.user.save()

    # --- Eliminar el gasto ---
    gasto.delete()

    # --- Registrar la actividad ---
    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"[EXP. GENERAL] Eliminó un gasto del expediente: {gasto.seguimiento.caso.expediente}"
    )

    return redirect('control_expediente:ver_seguimiento', caso_id=caso_id)

###############################################################################################
# CARPETA FISCAL                                                                              #
###############################################################################################
@login_required
def lista_carpeta_fiscal(request):
    form = CarpetaFiscalForm()

    if request.method == 'POST':
        form = CarpetaFiscalForm(request.POST)
        if form.is_valid():
            nuevo = form.save(commit=False)  # 👈 No lo guarda aún
            nuevo.concluido = True           # 👈 Fuerza el valor a 1 / True
            nuevo.save()    

            RegistroActividad.objects.create(
                nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha = timezone.now(),
                actividad = f"[CARPETA FISCAL] Registró un nuevo expediente: {form.save().carpeta_fiscal}"
            )

            return redirect('control_expediente:lista_carpeta_fiscal')
        else:
            print("Errores en el formulario:", form.errors)

    caso_judiciales = CarpetaFiscal.objects.all().exclude(concluido=False)
    registro_actividad = RegistroActividad.objects.all()

    especialidades_unicas = (
        CarpetaFiscal.objects.exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    usuarios_legales = User.objects.filter(role=User.LEGAL, is_active=True).order_by('first_name')

    return render(request, 'control_expediente/home_carpeta_fiscal.html', {
        'form': form,
        'caso_judiciales': caso_judiciales,
        'registro_actividad': registro_actividad,
        'especialidades': especialidades_unicas,
        'usuarios_legales': usuarios_legales,
    })

@login_required
def lista_concluidos_fiscal(request):
    form = CarpetaFiscalForm()

    if request.method == 'POST':
        form = CarpetaFiscalForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('control_expediente:lista_carpeta_fiscal')
        else:
            print("Errores en el formulario:", form.errors)

    caso_judiciales = CarpetaFiscal.objects.all().exclude(concluido=True)
    registro_actividad = RegistroActividad.objects.all()

    especialidades_unicas = (
        CarpetaFiscal.objects.exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    usuarios_legales = User.objects.filter(role=User.LEGAL, is_active=True).order_by('first_name')

    return render(request, 'control_expediente/home_carpeta_fiscal_concluidos.html', {
        'form': form,
        'caso_judiciales': caso_judiciales,
        'registro_actividad': registro_actividad,
        'especialidades': especialidades_unicas,
        'usuarios_legales': usuarios_legales,
    })

def editar_expediente_fiscal_concluido(request):
    if request.method == 'POST':
        cj_id = request.POST.get('id')
        cj = get_object_or_404(CarpetaFiscal, id=cj_id)
        
        # Cambiar True ↔ False
        cj.concluido = not cj.concluido
        cj.save()

        # Texto dinámico según el nuevo estado
        estado = "concluido" if cj.concluido else "no concluido"

        RegistroActividad.objects.create(
            nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
            fecha=timezone.now(),
            actividad=f"[EXP FISCAL] Marcó como {estado} el expediente: {cj.carpeta_fiscal}"
        )

        return redirect('control_expediente:lista_concluidos_fiscal')

def editar_carpeta_fiscal(request):
    if request.method == 'POST':
        cj_id = request.POST.get('id')
        cj = get_object_or_404(CarpetaFiscal, id=cj_id)

        form = CarpetaFiscalForm(request.POST, instance=cj)
        
        if form.is_valid():
            form.save()

            RegistroActividad.objects.create(
                nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha = timezone.now(),
                actividad = f"[CARPETA FISCAL] Modificó el expediente: {form.save().carpeta_fiscal}"
            )

            return redirect('control_expediente:lista_carpeta_fiscal')
        else:
            return redirect('control_expediente:lista_carpeta_fiscal')
    return redirect('control_expediente:lista_carpeta_fiscal')

def eliminar_carpeta_fiscal(request, doc_id):
    doc = get_object_or_404(CarpetaFiscal, id=doc_id)
    doc.delete()

    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"[CARPETA FISCAL] Eliminó el expediente: {doc.carpeta_fiscal}"
    )

    return redirect('control_expediente:lista_carpeta_fiscal')

def eliminar_concluidos_fiscal(request, doc_id):
    doc = get_object_or_404(CarpetaFiscal, id=doc_id)
    doc.delete()

    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"[CARPETA FISCAL] Eliminó el expediente: {doc.carpeta_fiscal}"
    )

    return redirect('control_expediente:lista_concluidos_fiscal')


def ver_seguimiento_carpeta_fiscal(request, caso_id):
    caso = get_object_or_404(CarpetaFiscal, id=caso_id)

    # Formularios por defecto
    seguimiento_form = SeguimientoFiscalForm()
    gasto_form = GastoFiscalForm()

    if request.method == 'POST':
        tipo_formulario = request.POST.get('tipo_formulario')
        seguimiento_id = request.POST.get('seguimiento_id')

        # Agregar gasto a seguimiento
        if tipo_formulario == 'gasto' and seguimiento_id:
            seguimiento = get_object_or_404(SeguimientoFiscal, id=seguimiento_id)
            gasto_form = GastoFiscalForm(request.POST, request.FILES)
            if gasto_form.is_valid():
                nuevo_gasto = gasto_form.save(commit=False)
                nuevo_gasto.seguimiento = seguimiento

                # Guardar el nombre del editor actual
                nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
                nuevo_gasto.editor = nombre_editor if nombre_editor else request.user.username
                nuevo_gasto.save()

                RegistroActividad.objects.create(
                    nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha = timezone.now(),
                    actividad = f"[CARPETA FISCAL] Registró un nuevo gasto en: {nuevo_gasto.seguimiento.caso.carpeta_fiscal}"
                )

                return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso.id)

        # Editar seguimiento existente
        elif tipo_formulario == 'editar_seguimiento' and seguimiento_id:
            seguimiento = get_object_or_404(SeguimientoFiscal, id=seguimiento_id)

            # Detectar si el PDF debe eliminarse
            if request.POST.get('eliminar_pdf') == 'true' and seguimiento.pdf:
                seguimiento.pdf.delete(save=False)
                seguimiento.pdf = None

            # Si se sube un nuevo PDF, se reemplaza
            nuevo_pdf = request.FILES.get('pdf')
            if nuevo_pdf:
                if seguimiento.pdf:
                    seguimiento.pdf.delete(save=False)
                seguimiento.pdf = nuevo_pdf

            # Actualizar con el resto de campos del formulario
            seguimiento_form = SeguimientoFiscalForm(request.POST, request.FILES, instance=seguimiento)
            if seguimiento_form.is_valid():
                seguimiento_editado = seguimiento_form.save(commit=False)
                seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
                seguimiento_editado.save()
                return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso.id)


        # Crear nuevo seguimiento
        else:
            seguimiento_form = SeguimientoFiscalForm(request.POST, request.FILES)
            if seguimiento_form.is_valid():
                nuevo_seguimiento = seguimiento_form.save(commit=False)
                nuevo_seguimiento.caso = caso
                nuevo_seguimiento.usuario = request.user
                nuevo_seguimiento.editor = f"{request.user.first_name} {request.user.last_name}"
                nuevo_seguimiento.save()
                return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso.id)
            else:
                print("Errores en el formulario de seguimiento:")
                print(seguimiento_form.errors)

    # Consultas para mostrar en plantilla
    seguimientos = (
        caso.seguimientos_penal.all()
        .prefetch_related('gastos_fiscal')
        .order_by('-fecha_seguimiento')
    )

    # --- 🔹 Obtener la fecha del primer gasto del caso ---
    primer_gasto = (
        GastoFiscal.objects
        .filter(seguimiento__caso=caso)
        .order_by('fecha')
        .first()
    )
    primera_fecha_gasto = primer_gasto.fecha if primer_gasto else None

    # Totales
    total_soles = 0
    total_dolares = 0

    for seguimiento in seguimientos:
        for gasto in seguimiento.gastos_fiscal.all():
            total_soles += gasto.gastos_soles or 0
            total_dolares += gasto.gastos_dolares or 0

        # Mostrar nombre del creador
        if seguimiento.usuario:
            seguimiento.nombre_usuario = f"{seguimiento.usuario.first_name} {seguimiento.usuario.last_name}"
        else:
            seguimiento.nombre_usuario = "—"

    especialidades_unicas = (
        CarpetaFiscal.objects.exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    # --- 🔹 Consulta SQL filtrando desde la fecha del primer gasto ---
    with connection.cursor() as cursor:
        query_base = """
            SELECT 
                c.carpeta_fiscal,
                s.resolucion,
                g.fecha,
                g.detalle,
                g.codigo_pago,
                g.gastos_soles,
                g.gastos_dolares
            FROM control_expediente_gastofiscal AS g
            INNER JOIN control_expediente_seguimientofiscal AS s ON g.seguimiento_id = s.id
            INNER JOIN control_expediente_carpetafiscal AS c ON s.caso_id = c.id
            WHERE c.id = %s
        """

        params = [caso_id]

        if primera_fecha_gasto:
            query_base += " AND g.fecha >= %s"
            params.append(primera_fecha_gasto)

        query_base += " ORDER BY g.fecha ASC"

        cursor.execute(query_base, params)
        rows = cursor.fetchall()

    gastos_expediente = [
        {
            "expediente": row[0],
            "resolucion": row[1],
            "fecha": row[2],
            "detalle": row[3],
            "codigo_pago": row[4],
            "gastos_soles": row[5],
            "gastos_dolares": row[6],
        }
        for row in rows
    ]

    context = {
        'caso': caso,
        'seguimientos': seguimientos,
        'form': seguimiento_form,
        'form2': gasto_form,
        'total_soles': total_soles,
        'total_dolares': total_dolares,
        'nombre_usuario': f"{request.user.first_name} {request.user.last_name}",
        'especialidades': especialidades_unicas,
        'primera_fecha_gasto': primera_fecha_gasto,
        'gastos_expediente': gastos_expediente,
    }

    return render(request, 'control_expediente/seguimientos_y_gastos_fiscal.html', context)

def ver_seguimiento_fiscal_concluido(request, caso_id):
    caso = get_object_or_404(CarpetaFiscal, id=caso_id)

    # Formularios por defecto
    seguimiento_form = SeguimientoFiscalForm()
    gasto_form = GastoFiscalForm()

    if request.method == 'POST':
        tipo_formulario = request.POST.get('tipo_formulario')
        seguimiento_id = request.POST.get('seguimiento_id')

        # Agregar gasto a seguimiento
        if tipo_formulario == 'gasto' and seguimiento_id:
            seguimiento = get_object_or_404(SeguimientoFiscal, id=seguimiento_id)
            gasto_form = GastoFiscalForm(request.POST, request.FILES)
            if gasto_form.is_valid():
                nuevo_gasto = gasto_form.save(commit=False)
                nuevo_gasto.seguimiento = seguimiento

                # Guardar el nombre del editor actual
                nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
                nuevo_gasto.editor = nombre_editor if nombre_editor else request.user.username
                nuevo_gasto.save()

                RegistroActividad.objects.create(
                    nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha = timezone.now(),
                    actividad = f"[CARPETA FISCAL] Registró un nuevo gasto en: {nuevo_gasto.seguimiento.caso.carpeta_fiscal}"
                )

                return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso.id)

        # Editar seguimiento existente
        elif tipo_formulario == 'editar_seguimiento' and seguimiento_id:
            seguimiento = get_object_or_404(SeguimientoFiscal, id=seguimiento_id)

            # Detectar si el PDF debe eliminarse
            if request.POST.get('eliminar_pdf') == 'true' and seguimiento.pdf:
                seguimiento.pdf.delete(save=False)
                seguimiento.pdf = None

            # Si se sube un nuevo PDF, se reemplaza
            nuevo_pdf = request.FILES.get('pdf')
            if nuevo_pdf:
                if seguimiento.pdf:
                    seguimiento.pdf.delete(save=False)
                seguimiento.pdf = nuevo_pdf

            # Actualizar con el resto de campos del formulario
            seguimiento_form = SeguimientoFiscalForm(request.POST, request.FILES, instance=seguimiento)
            if seguimiento_form.is_valid():
                seguimiento_editado = seguimiento_form.save(commit=False)
                seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
                seguimiento_editado.save()
                return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso.id)


        # Crear nuevo seguimiento
        else:
            seguimiento_form = SeguimientoFiscalForm(request.POST, request.FILES)
            if seguimiento_form.is_valid():
                nuevo_seguimiento = seguimiento_form.save(commit=False)
                nuevo_seguimiento.caso = caso
                nuevo_seguimiento.usuario = request.user
                nuevo_seguimiento.editor = f"{request.user.first_name} {request.user.last_name}"
                nuevo_seguimiento.save()
                return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso.id)
            else:
                print("Errores en el formulario de seguimiento:")
                print(seguimiento_form.errors)

    # Consultas para mostrar en plantilla
    seguimientos = (
        caso.seguimientos_penal.all()
        .prefetch_related('gastos_fiscal')
        .order_by('-fecha_seguimiento')
    )

    # --- 🔹 Obtener la fecha del primer gasto del caso ---
    primer_gasto = (
        GastoFiscal.objects
        .filter(seguimiento__caso=caso)
        .order_by('fecha')
        .first()
    )
    primera_fecha_gasto = primer_gasto.fecha if primer_gasto else None

    # Totales
    total_soles = 0
    total_dolares = 0

    for seguimiento in seguimientos:
        for gasto in seguimiento.gastos_fiscal.all():
            total_soles += gasto.gastos_soles or 0
            total_dolares += gasto.gastos_dolares or 0

        # Mostrar nombre del creador
        if seguimiento.usuario:
            seguimiento.nombre_usuario = f"{seguimiento.usuario.first_name} {seguimiento.usuario.last_name}"
        else:
            seguimiento.nombre_usuario = "—"

    especialidades_unicas = (
        CarpetaFiscal.objects.exclude(especialidad__isnull=True)
        .exclude(especialidad__exact="")
        .values_list('especialidad', flat=True)
        .distinct()
        .order_by('especialidad')
    )

    # --- 🔹 Consulta SQL filtrando desde la fecha del primer gasto ---
    with connection.cursor() as cursor:
        query_base = """
            SELECT 
                c.carpeta_fiscal,
                s.resolucion,
                g.fecha,
                g.detalle,
                g.codigo_pago,
                g.gastos_soles,
                g.gastos_dolares
            FROM control_expediente_gastofiscal AS g
            INNER JOIN control_expediente_seguimientofiscal AS s ON g.seguimiento_id = s.id
            INNER JOIN control_expediente_carpetafiscal AS c ON s.caso_id = c.id
            WHERE c.id = %s
        """

        params = [caso_id]

        if primera_fecha_gasto:
            query_base += " AND g.fecha >= %s"
            params.append(primera_fecha_gasto)

        query_base += " ORDER BY g.fecha ASC"

        cursor.execute(query_base, params)
        rows = cursor.fetchall()

    gastos_expediente = [
        {
            "expediente": row[0],
            "resolucion": row[1],
            "fecha": row[2],
            "detalle": row[3],
            "codigo_pago": row[4],
            "gastos_soles": row[5],
            "gastos_dolares": row[6],
        }
        for row in rows
    ]

    context = {
        'caso': caso,
        'seguimientos': seguimientos,
        'form': seguimiento_form,
        'form2': gasto_form,
        'total_soles': total_soles,
        'total_dolares': total_dolares,
        'nombre_usuario': f"{request.user.first_name} {request.user.last_name}",
        'especialidades': especialidades_unicas,
        'primera_fecha_gasto': primera_fecha_gasto,
        'gastos_expediente': gastos_expediente,
    }

    return render(request, 'control_expediente/seguimientos_y_gastos_fiscal_concluidos.html', context)


def editar_seguimiento_carpeta_fiscal(request):
    if request.method == 'POST':
        seguimiento_id = request.POST.get('id')
        print("ID recibido en POST:", seguimiento_id)

        seguimiento = get_object_or_404(SeguimientoFiscal, id=seguimiento_id)

        form = SeguimientoFiscalForm(request.POST, request.FILES, instance=seguimiento)
        
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)

            # Guardar el nombre del editor actual
            nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
            seguimiento_editado.editor = nombre_editor if nombre_editor else request.user.username
            seguimiento_editado.save()

            RegistroActividad.objects.create(
                    nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha = timezone.now(),
                    actividad = f"[CARPETA FISCAL] Modificó seguimiento del expediente: {seguimiento_editado.caso.carpeta_fiscal}"
                )

            return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=seguimiento.caso.id)
        else:
            print("Errores al editar seguimiento:", form.errors)
            return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=seguimiento.caso.id)

    return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=0)

def eliminar_seguimiento_carpeta_fiscal(request, seguimiento_id):
    seguimiento = get_object_or_404(SeguimientoFiscal, id=seguimiento_id)
    caso_id = seguimiento.caso.id  # Guardamos antes de eliminar
    seguimiento.delete()

    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"Eliminó seguimiento: {seguimiento.resolucion}"
    )

    return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso_id)

def editar_ce_gasto_carpeta_fiscal(request):
    print("asd123")
    if request.method == 'POST':
        gasto_id = request.POST.get('id')
        gasto = get_object_or_404(GastoFiscal, id=gasto_id)
        gasto.fecha = request.POST.get('fecha')
        gasto.detalle = request.POST.get('detalle')
        gasto.codigo_pago = request.POST.get('codigo_pago')
        gasto.gastos_soles = request.POST.get('gastos_soles') or 0
        gasto.gastos_dolares = request.POST.get('gastos_dolares') or 0

        if 'pdf' in request.FILES:
            gasto.pdf = request.FILES['pdf']

        gasto.save()

        RegistroActividad.objects.create(
                    nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha = timezone.now(),
                    actividad = f"Modificó un gasto del expediente: {gasto.seguimiento.caso.carpeta_fiscal}"
        )

        return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=gasto.seguimiento.caso.id)

def eliminar_gasto_carpeta_fiscal(request):
    gasto_id = request.POST.get('gasto_id')
    gasto = get_object_or_404(GastoFiscal, id=gasto_id)
    caso_id = gasto.seguimiento.caso.id
    gasto.delete()

    RegistroActividad.objects.create(
                    nombre = f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha = timezone.now(),
                    actividad = f"Eliminó un gasto del expediente: {gasto.seguimiento.caso.carpeta_fiscal}"
    )

    return redirect('control_expediente:ver_seguimiento_carpeta_fiscal', caso_id=caso_id)
