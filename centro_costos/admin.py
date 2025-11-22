from django.contrib import admin
from .models import *

@admin.register(CentroDeCostos)
class CentroDeCostosAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(TipoDeGasto)
class TipoDeGastoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'centro_de_costos', 'tipo', 'responsable', 'fecha_registro')
    list_filter = ('tipo', 'centro_de_costos')
    search_fields = ('nombre', 'codigo', 'responsable')

@admin.register(GastoTA2020)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('actividad', 'fecha', 'documento', 'debe', 'haber', 'tipo_gasto', 'fecha_registro')
    list_filter = ('actividad', 'tipo_gasto', 'fecha')
    search_fields = ('nombre', 'detalle', 'documento')

@admin.register(NuevoGasto)
class NuevoGastoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'flag')
    list_filter = ('flag',)
    search_fields = ('nombre',)

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################

@admin.register(GastoN1)
class GastoN1Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto')

# CC CANTA CALLAO
@admin.register(GastoN2)
class GastoN2Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto')

@admin.register(GastoN3)
class GastoN3Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto')

# VENEZUELA
@admin.register(GastoN4)
class GastoN4Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto')

# PANDO
@admin.register(GastoN5)
class GastoN5Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto') 

@admin.register(GastoN6)
class GastoN6Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto') 

@admin.register(GastoN7)
class GastoN7Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto')

# CC NELLY
@admin.register(GastoN8)
class GastoN8Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'tipo_gasto')
    list_filter = ('fecha', 'tipo_gasto')

@admin.register(GastoN9)
class GastoN9Admin(admin.ModelAdmin):
    list_display = ('expediente', 'fecha', 'monto_soles', 'monto_dolares')
    search_fields = ('expediente', 'juzgado')
    list_filter = ('expediente', 'juzgado')

@admin.register(GastoN10)
class GastoN10Admin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'actividad', 'tipo_gasto', 'monto_soles', 'monto_dolares')
    search_fields = ('codigo', 'detalle', 'actividad', 'tipo_gasto')
    list_filter = ('fecha', 'actividad', 'tipo_gasto')
