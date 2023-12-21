from import_export import resources
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from .models import Conductor,Sede, Propietario,Encomienda,Bus,Programacion

# Register your models here.

admin.site.register(Propietario)
admin.site.register(Conductor)
admin.site.register(Encomienda)

class BusResource(resources.ModelResource):
    fields = ('propietario', 'numero_bus', 'placa_bus', 'asientos', 'estado',)
    class Meta:
        model = Bus

class ProgramacionResource(resources.ModelResource):
    fields = ('codigo','bus','origen','destino','programacion','precio','estado','fecha_creado', 'fecha_actualizado',)
    class Meta:
        model = Programacion


class EncomiendaResource(resources.ModelResource):
    fields = ('programacion', 'nombre_envio', 'cedula_envio', 'telefono_envio', 'nombre_recibido', 'cedula_recibido','telefono_recibido', 'caracteristicas', 'estado',)
    class Meta:
        model = Encomienda

class BusAdmin(admin.ModelAdmin):
    list_display = ('propietario','placa_bus','numero_bus','asientos','estado',)
    search_fields = ('propietario','numero_bus',)
#buses

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('sede', 'tipo', )
    search_fields = ('sede','tipo', )

@admin.register(Bus)
class BusAdmin(ImportExportModelAdmin):
    resource_class = BusResource
    list_display = ('propietario','placa_bus','numero_bus','asientos','estado',)

    def admin_bus(self, obj):
        return 'Administración de Buses'

    search_fields = ('propietario','numero_bus',)

@admin.register(Programacion)
class ProgramacionAdmin(ImportExportModelAdmin):
    resource_class = ProgramacionResource
    list_display = ('codigo','bus','origen','destino','precio','programacion','estado','fecha_creado','fecha_actualizado',)

    def autor(self, obj):
        return 'Administración de la Programación'

    search_fields = ('estado','codigo',)