from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.db.models.functions import ExtractYear, ExtractMonth
import locale

@login_required
def sistemas(request):
    return render(request, 'sistemas/index.html')

@login_required
def documentacion(request):
    return render(request, 'partidas_planos/home.html')

@login_required
def lista_partidas(request):
    form = PartidaForm()

    if request.method == 'POST':
        form = PartidaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_partidas')
        else:
            print("Errores del formulario:")
            print(form.errors)

    partidas = Partida.objects.all()

    #locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    # Años únicos
    anios_unicos = (
        Partida.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    # Meses únicos (número del mes)
    meses_unicos = (
        Partida.objects.annotate(mes=ExtractMonth('fecha'))
        .values_list('mes', flat=True)
        .distinct()
        .order_by('mes')
    )

    # Si quieres pasar los nombres de los meses, puedes hacerlo así:
    import calendar
    meses_con_nombre = [(i, calendar.month_name[i]) for i in meses_unicos if i]

    return render(request, 'partidas_planos/lista_partidas.html', {
        'form': form,
        'partidas': partidas,
        'anios': anios_unicos,
        'meses': meses_con_nombre,
    })


def editar_partida(request):
    if request.method == 'POST':
        partida_id = request.POST.get('id')
        partida = get_object_or_404(Partida, id=partida_id)

        form = PartidaForm(request.POST, request.FILES, instance=partida)
        # print(form)
        # print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('lista_partidas')
        else:
            print(form.errors)  # Muy útil para debug
            return redirect('lista_partidas')  # o puedes mostrar un error

    return redirect('lista_partidas')

def eliminar_partida(request, doc_id):
    doc = get_object_or_404(Partida, id=doc_id)
    doc.delete()
    return redirect('lista_partidas')


##########################################################################

@login_required
def lista_planos(request):
    form = PlanoForm()

    if request.method == 'POST':
        form = PlanoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_planos')

    planos = Plano.objects.all().order_by('fecha')

    # Años únicos
    anios_unicos = (
        Plano.objects.annotate(anio=ExtractYear('fecha'))
        .values_list('anio', flat=True)
        .distinct()
        .order_by('anio')
    )

    return render(request, 'partidas_planos/lista_planos.html', {
        'form': form,
        'planos': planos,
        'anios': anios_unicos,
    })

@login_required
def editar_plano(request):
    if request.method == 'POST':
        plano_id = request.POST.get('id')
        plano = get_object_or_404(Plano, id=plano_id)

        form = PlanoForm(request.POST, request.FILES, instance=plano)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('lista_planos')
        else:
            print(form.errors)
            return redirect('lista_planos')

    return redirect('lista_planos')

@login_required
def eliminar_plano(request, doc_id):
    plano = get_object_or_404(Plano, id=doc_id)
    plano.delete()
    return redirect('lista_planos')
