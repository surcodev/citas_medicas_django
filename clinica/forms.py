from django import forms
from .models import *
from datetime import time, timedelta, datetime

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agregar la clase form-control a todos los campos
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['autocomplete'] = 'off'



class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ingrese el motivo de la cita...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Texto vacío del selector de pacientes
        self.fields['paciente'].empty_label = "Seleccionar paciente"

        # Generar intervalos de 30 min desde 08:00 hasta 17:30
        opciones_horas = []
        inicio = datetime.strptime("08:00", "%H:%M")
        fin = datetime.strptime("17:30", "%H:%M")

        actual = inicio
        while actual <= fin:
            inicio_str = actual.strftime("%H:%M")
            fin_intervalo = (actual + timedelta(minutes=30)).strftime("%H:%M")
            opciones_horas.append((inicio_str, f"{inicio_str} - {fin_intervalo}"))
            actual += timedelta(minutes=30)

        # Reemplazar widget de hora por un <select>
        self.fields["hora"] = forms.ChoiceField(
            choices=opciones_horas,
            widget=forms.Select(attrs={'class': 'form-control'})
        )

        # Agregar clases a los demás campos
        for name, field in self.fields.items():
            if name != "hora":  # evitar sobrescribir la clase del select
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['autocomplete'] = 'off'