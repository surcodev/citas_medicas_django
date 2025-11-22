from .models import Anios, Q1_T1
from .forms import AniosForm, Q1_T1Form
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

def hoja_requerimiento_home(request):
    ngs = Anios.objects.filter(flag=True)
    print(ngs)
    form = AniosForm()
    return render(request, 'hoja_requerimiento/home.html', {
        'ngs': ngs,
        'form': form,
    })


@login_required
def lista_q1_n1(request):
    form = Q1_T1Form()

    if request.method == 'POST':
        form = Q1_T1Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('hoja_requerimiento:lista_q1_t1')

    gastoN1 = Q1_T1.objects.all()
    nombreN1 = Anios.objects.first()
    return render(request, 'hoja_requerimiento/lista_q1_t1.html', {
        'form': form,
        'gasto_general': gastoN1,
        'nombreN1': nombreN1
    })