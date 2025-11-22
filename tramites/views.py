from .models import SeguimientoTramite, Tramite, GastoTramite
from .forms import TramiteForm, SeguimientoTramiteForm, GastoTramiteForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from partidas_planos.models import User
from django.db import connection
import openpyxl
from django.http import HttpResponse
from control_expediente.models import RegistroActividad
from django.utils import timezone


def exportar_gastos_tramite_excel(request, caso_id):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Gastos"

    # Encabezados
    headers = ["Kardex", "Fecha", "Detalle", "Código Pago", "Gasto (S/)", "Gasto ($)"]
    ws.append(headers)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.kardex,
                g.fecha,
                g.detalle,
                g.codigo_pago,
                g.gastos_soles,
                g.gastos_dolares
            FROM tramites_gastotramite AS g
            INNER JOIN tramites_seguimientotramite AS s ON g.seguimiento_id = s.id
            INNER JOIN tramites_tramite AS c ON s.caso_id = c.id
            WHERE c.id = %s
            
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
def lista_tramite(request):
    from django.db.models import OuterRef, Subquery, DateField, TextField
    from datetime import date

    hoy = date.today()

    # ==================================================
    # 🔹 SUBCONSULTAS OPTIMIZADAS (FK correcta: caso)
    # ==================================================
    subquery_seguimiento_alerta = (
        SeguimientoTramite.objects
        .filter(caso=OuterRef('pk'), fecha_alerta__gte=hoy)
        .order_by('fecha_alerta', '-fecha_registro')
    )

    subquery_seguimiento_id = subquery_seguimiento_alerta.values('id')[:1]
    subquery_fecha_alerta = subquery_seguimiento_alerta.values('fecha_alerta')[:1]

    subquery_pendiente_alerta = (
        SeguimientoTramite.objects
        .filter(id=Subquery(subquery_seguimiento_id))
        .values('pendiente')[:1]
    )

    # ==================================================
    # 🔹 CONSULTA PRINCIPAL
    # ==================================================
    caso_judiciales = (
        Tramite.objects
        .annotate(
            proxima_alerta=Subquery(subquery_fecha_alerta, output_field=DateField()),
            pendiente_alerta=Subquery(subquery_pendiente_alerta, output_field=TextField())
        )
        .filter(concluido=True)
        .select_related('responsable2')  # ✅ campo correcto
        .order_by('kardex')
    )

    # ==================================================
    # 🔹 CALCULAR COLOR DE ALERTA
    # ==================================================
    for t in caso_judiciales:
        if t.proxima_alerta:
            dias_restantes = (t.proxima_alerta - hoy).days
            if dias_restantes <= 5:
                t.alerta_color = "danger"
            elif dias_restantes <= 15:
                t.alerta_color = "warning"
            else:
                t.alerta_color = "success"
        else:
            t.alerta_color = "secondary"

    # ==================================================
    # 🔹 FORMULARIO Y DEMÁS DATOS
    # ==================================================
    if request.method == 'POST':
        post_data = request.POST.copy()
        if post_data.get('tramite_tipo') == 'Otros':
            otro_valor = post_data.get('otros_tramite')
            if otro_valor:
                post_data['tramite_tipo'] = otro_valor

        form = TramiteForm(post_data)
        if form.is_valid():
            nuevo = form.save(commit=False)
            nuevo.concluido = True
            nuevo.save()

            RegistroActividad.objects.create(
                nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha=timezone.now(),
                actividad=f"[TRÁMITES] Registró un nuevo trámite: {nuevo.kardex}"
            )

            return redirect('tramites:lista_tramite')
        else:
            print("Errores en el formulario:", form.errors)
    else:
        form = TramiteForm()

    usuarios_legales = (
        User.objects.filter(is_active=True)
        .exclude(username__in=['surcodev', 'plupa', 'cdiaz', 'nelly'])
        .order_by('first_name')
    )

    tipo_tramite = (
        Tramite.objects.exclude(tramite_tipo__isnull=True)
        .exclude(tramite_tipo__exact="")
        .values_list('tramite_tipo', flat=True)
        .distinct()
        .order_by('tramite_tipo')
    )

    return render(request, 'tramites/home.html', {
        'form': form,
        'caso_judiciales': caso_judiciales,
        'especialidades': tipo_tramite,
        'usuarios_legales': usuarios_legales,
    })




@login_required
def lista_tramite_concluidos(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        print(post_data)

        if post_data.get('tramite_tipo') == 'Otros':
            otro_valor = post_data.get('otros_tramite')
            if otro_valor:
                post_data['tramite_tipo'] = otro_valor

        form = TramiteForm(post_data)

        if form.is_valid():
            form.save()
            return redirect('tramites:lista_tramite_concluidos')
        else:
            print("Errores en el formulario:", form.errors)  # 👈 Aquí se imprimen los errores

    else:
        form = TramiteForm()

    caso_judiciales = Tramite.objects.all().order_by('kardex').filter(concluido=False)
    usuarios_legales = User.objects.filter(
        is_active=True
    ).exclude(username='user8').order_by('first_name')


    tipo_tramite = (
        Tramite.objects.exclude(tramite_tipo__isnull=True)
        .exclude(tramite_tipo__exact="")
        .values_list('tramite_tipo', flat=True)
        .distinct()
        .order_by('tramite_tipo')
    )

    return render(request, 'tramites/home_concluidos.html', {
        'form': form,
        'caso_judiciales': caso_judiciales,
        'especialidades': tipo_tramite,
        'usuarios_legales': usuarios_legales,
    })



def editar_tramite(request):
    if request.method == 'POST':
        cj_id = request.POST.get('id')
        cj = get_object_or_404(Tramite, id=cj_id)

        # Creamos una copia mutable del POST original
        post_data = request.POST.copy()

        # Si se seleccionó "Otros", sobrescribimos el valor de tramite_tipo
        if post_data.get('tramite_tipo') == 'Otros':
            otros_valor = post_data.get('otros_tramite')
            if otros_valor:
                post_data['tramite_tipo'] = otros_valor  # Reemplazamos el valor

        form = TramiteForm(post_data, instance=cj)

        if form.is_valid():
            form.save()

            RegistroActividad.objects.create(
                nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha=timezone.now(),
                actividad=f"[TRÁMITES] Modificó el trámite: {form.save().kardex}"
            )

            return redirect('tramites:lista_tramite')
        else:
            print(form.errors)
            return redirect('tramites:lista_tramite')

    return redirect('tramites:lista_tramite')


def editar_t_concluido(request):
    if request.method == 'POST':
        cj_id = request.POST.get('id')
        cj = get_object_or_404(Tramite, id=cj_id)

        cj.concluido = not cj.concluido  # Alterna el valor de concluido
        cj.save()

    return redirect('tramites:lista_tramite_concluidos')


@login_required
def eliminar_tramite(request, doc_id):
    doc = get_object_or_404(Tramite, id=doc_id)

    # Guardamos el kardex antes de eliminar
    kardex = doc.kardex
    # Eliminamos el trámite
    doc.delete()

    # Registramos la actividad
    RegistroActividad.objects.create(
        nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
        fecha=timezone.now(),
        actividad=f"[TRÁMITES] Eliminó el trámite: {kardex}"
    )
    return redirect('tramites:lista_tramite')

####################################################################

def ver_seguimiento_tramite(request, caso_id):
    caso = get_object_or_404(Tramite, id=caso_id)

    # Formularios por defecto
    seguimiento_form = SeguimientoTramiteForm()
    gasto_form = GastoTramiteForm()

    if request.method == 'POST':
        tipo_formulario = request.POST.get('tipo_formulario')
        seguimiento_id = request.POST.get('seguimiento_id')

        # Agregar gastoTramite a seguimientoTramite
        if tipo_formulario == 'gasto' and seguimiento_id:
            print("Agregar gasto al seguimiento ID:", seguimiento_id)
            seguimiento = get_object_or_404(SeguimientoTramite, id=seguimiento_id)
            gasto_form = GastoTramiteForm(request.POST, request.FILES)
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
                    actividad=f"[TRÁMITES] Registró nuevo gasto en el trámite: {nuevo_gasto.seguimiento.caso.kardex}"
                )
                
                return redirect('tramites:ver_seguimiento_tramite', caso_id=caso.id)

        # Editar seguimiento existente
        elif tipo_formulario == 'editar_seguimiento' and seguimiento_id:
            seguimiento = get_object_or_404(SeguimientoTramite, id=seguimiento_id)
            seguimiento_form = SeguimientoTramiteForm(request.POST, request.FILES, instance=seguimiento)
            if seguimiento_form.is_valid():
                seguimiento_editado = seguimiento_form.save(commit=False)
                seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
                seguimiento_editado.save()

                RegistroActividad.objects.create(
                    nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha=timezone.now(),
                    actividad=f"[TRÁMITES] Modificó un seguimiento en el trámite: {nuevo_gasto.save().kardex}"
                )

                print("Seguimiento editado:", seguimiento_editado)

                return redirect('tramites:ver_seguimiento_tramite', caso_id=caso.id)

        # Crear nuevo seguimiento
        else:
            seguimiento_form = SeguimientoTramiteForm(request.POST, request.FILES)
            if seguimiento_form.is_valid():
                nuevo_seguimiento = seguimiento_form.save(commit=False)
                nuevo_seguimiento.caso = caso
                nuevo_seguimiento.usuario = request.user
                nuevo_seguimiento.editor = f"{request.user.first_name} {request.user.last_name}"
                nuevo_seguimiento.save()

                RegistroActividad.objects.create(
                    nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                    fecha=timezone.now(),
                    actividad=f"[TRÁMITES] Agregó un nuevo seguimiento en el trámite: {nuevo_seguimiento.caso.kardex}"
                )

                return redirect('tramites:ver_seguimiento_tramite', caso_id=caso.id)

    # Consultas para mostrar en plantilla
    seguimientos = (
        caso.seguimientos_tramites.all()
        .prefetch_related('gastos_tramites')
        .order_by('-fecha_seguimiento')
    )
    #presentaciones = caso.presentaciones.prefetch_related(presentaciones_prefetch)

    # --- 🔹 Obtener la fecha del primer gasto del caso ---
    primer_gasto = (
        GastoTramite.objects
        .filter(seguimiento__caso=caso)
        .order_by('fecha')
        .first()
    )
    primera_fecha_gasto = primer_gasto.fecha if primer_gasto else None

    # Totales
    total_soles = 0
    total_dolares = 0

    for seguimiento in seguimientos:
        for gasto in seguimiento.gastos_tramites.all():
            total_soles += gasto.gastos_soles or 0
            total_dolares += gasto.gastos_dolares or 0

        # Mostrar nombre del creador
        if seguimiento.usuario:
            seguimiento.nombre_usuario = f"{seguimiento.usuario.first_name} {seguimiento.usuario.last_name}"
        else:
            seguimiento.nombre_usuario = "—"

    # --- 🔹 Consulta SQL filtrando desde la fecha del primer gasto ---
    with connection.cursor() as cursor:
        query_base = """
            SELECT 
                c.kardex,
                g.fecha,
                g.detalle,
                g.codigo_pago,
                g.gastos_soles,
                g.gastos_dolares
            FROM tramites_gastotramite AS g
            INNER JOIN tramites_seguimientotramite AS s ON g.seguimiento_id = s.id
            INNER JOIN tramites_tramite AS c ON s.caso_id = c.id
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
            "fecha": row[1],
            "detalle": row[2],
            "codigo_pago": row[3],
            "gastos_soles": row[4],
            "gastos_dolares": row[5],
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
        'primera_fecha_gasto': primera_fecha_gasto,
        'gastos_expediente': gastos_expediente,
    }

    return render(request, 'tramites/seguimientos_tramites_y_gastos.html', context)


def ver_seguimiento_t_concluido(request, caso_id):
    caso = get_object_or_404(Tramite, id=caso_id)

    # Formularios por defecto
    seguimiento_form = SeguimientoTramiteForm()
    gasto_form = GastoTramiteForm()

    if request.method == 'POST':
        tipo_formulario = request.POST.get('tipo_formulario')
        seguimiento_id = request.POST.get('seguimiento_id')

        # Agregar gastoTramite a seguimientoTramite
        if tipo_formulario == 'gasto' and seguimiento_id:
            seguimiento = get_object_or_404(SeguimientoTramite, id=seguimiento_id)
            gasto_form = GastoTramiteForm(request.POST, request.FILES)
            if gasto_form.is_valid():
                nuevo_gasto = gasto_form.save(commit=False)
                nuevo_gasto.seguimiento = seguimiento

                # Guardar el nombre del editor actual
                nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
                nuevo_gasto.editor = nombre_editor if nombre_editor else request.user.username
                nuevo_gasto.save()
                
                return redirect('tramites:ver_seguimiento_t_concluido', caso_id=caso.id)

        # Editar seguimiento existente
        elif tipo_formulario == 'editar_seguimiento' and seguimiento_id:
            seguimiento = get_object_or_404(SeguimientoTramite, id=seguimiento_id)
            seguimiento_form = SeguimientoTramiteForm(request.POST, request.FILES, instance=seguimiento)
            if seguimiento_form.is_valid():
                seguimiento_editado = seguimiento_form.save(commit=False)
                seguimiento_editado.editor = f"{request.user.first_name} {request.user.last_name}"
                seguimiento_editado.save()
                return redirect('tramites:ver_seguimiento_t_concluido', caso_id=caso.id)

        # Crear nuevo seguimiento
        else:
            seguimiento_form = SeguimientoTramiteForm(request.POST, request.FILES)
            if seguimiento_form.is_valid():
                nuevo_seguimiento = seguimiento_form.save(commit=False)
                nuevo_seguimiento.caso = caso
                nuevo_seguimiento.usuario = request.user
                nuevo_seguimiento.editor = f"{request.user.first_name} {request.user.last_name}"
                nuevo_seguimiento.save()
                return redirect('tramites:ver_seguimiento_t_concluido', caso_id=caso.id)

    # Consultas para mostrar en plantilla
    seguimientos = (
        caso.seguimientos_tramites.all()
        .prefetch_related('gastos_tramites')
        .order_by('-fecha_seguimiento')
    )
    #presentaciones = caso.presentaciones.prefetch_related(presentaciones_prefetch)

    # --- 🔹 Obtener la fecha del primer gasto del caso ---
    primer_gasto = (
        GastoTramite.objects
        .filter(seguimiento__caso=caso)
        .order_by('fecha')
        .first()
    )
    primera_fecha_gasto = primer_gasto.fecha if primer_gasto else None

    # Totales
    total_soles = 0
    total_dolares = 0

    for seguimiento in seguimientos:
        for gasto in seguimiento.gastos_tramites.all():
            total_soles += gasto.gastos_soles or 0
            total_dolares += gasto.gastos_dolares or 0

        # Mostrar nombre del creador
        if seguimiento.usuario:
            seguimiento.nombre_usuario = f"{seguimiento.usuario.first_name} {seguimiento.usuario.last_name}"
        else:
            seguimiento.nombre_usuario = "—"

    # --- 🔹 Consulta SQL filtrando desde la fecha del primer gasto ---
    with connection.cursor() as cursor:
        query_base = """
            SELECT 
                c.kardex,
                g.fecha,
                g.detalle,
                g.codigo_pago,
                g.gastos_soles,
                g.gastos_dolares
            FROM tramites_gastotramite AS g
            INNER JOIN tramites_seguimientotramite AS s ON g.seguimiento_id = s.id
            INNER JOIN tramites_tramite AS c ON s.caso_id = c.id
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
            "fecha": row[1],
            "detalle": row[2],
            "codigo_pago": row[3],
            "gastos_soles": row[4],
            "gastos_dolares": row[5],
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
        'primera_fecha_gasto': primera_fecha_gasto,
        'gastos_expediente': gastos_expediente,
    }

    return render(request, 'tramites/seguimientos_tg_concluidos.html', context)



def editar_seguimiento_tramite(request):
    if request.method == 'POST':
        seguimiento_id = request.POST.get('id')
        seguimiento = get_object_or_404(SeguimientoTramite, id=seguimiento_id)

        form = SeguimientoTramiteForm(request.POST, request.FILES, instance=seguimiento)
        
        if form.is_valid():
            seguimiento_editado = form.save(commit=False)

            # Guardar el nombre del editor actual
            nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
            seguimiento_editado.editor = nombre_editor if nombre_editor else request.user.username

            seguimiento_editado.save()

            RegistroActividad.objects.create(
                nombre=f"{request.user.first_name} {request.user.last_name}".strip(),
                fecha=timezone.now(),
                actividad=f"[TRÁMITES] Modificó seguimiento en el trámite: {seguimiento_editado.caso.kardex}"
            )


            return redirect('tramites:ver_seguimiento_tramite', caso_id=seguimiento.caso.id)
        else:
            print("Errores al editar seguimiento tramite:", form.errors)
            return redirect('tramites:ver_seguimiento_tramite', caso_id=seguimiento.caso.id)

    return redirect('tramites:ver_seguimiento_tramite', caso_id=0)

def eliminar_seguimiento_tramite(request, seguimiento_tramite_id):
    seguimiento = get_object_or_404(SeguimientoTramite, id=seguimiento_tramite_id)
    caso_id = seguimiento.caso.id  # Guardamos antes de eliminar
    seguimiento.delete()
    return redirect('tramites:ver_seguimiento_tramite', caso_id=caso_id)

def editar_gasto_tramite(request):
    if request.method == 'POST':
        gasto_id = request.POST.get('id')
        gasto = get_object_or_404(GastoTramite, id=gasto_id)

        gasto.fecha = request.POST.get('fecha')
        gasto.detalle = request.POST.get('detalle')
        gasto.codigo_pago = request.POST.get('codigo_pago')
        gasto.gastos_soles = request.POST.get('gastos_soles') or 0
        gasto.gastos_dolares = request.POST.get('gastos_dolares') or 0

        if 'pdf' in request.FILES:
            gasto.pdf = request.FILES['pdf']

        # Guardar el nombre del editor actual
        nombre_editor = f"{request.user.first_name} {request.user.last_name}".strip()
        gasto.editor = nombre_editor if nombre_editor else request.user.username
        gasto.save()

        return redirect('tramites:ver_seguimiento_tramite', caso_id=gasto.seguimiento.caso.id)

def eliminar_gasto_tramite(request):
    gasto_id = request.POST.get('gasto_id')
    gasto = get_object_or_404(GastoTramite, id=gasto_id)
    caso_id = gasto.seguimiento.caso.id
    gasto.delete()
    return redirect('tramites:ver_seguimiento_tramite', caso_id=caso_id)