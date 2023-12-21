from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Conductor(models.Model): #
    conductor = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100)
    cedula = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=(('1', 'Activo'), ('2', 'Inactivo')), default=1)

    def __str__(self):
        return str(self.conductor + ' - ' + self.codigo)

    class Meta:
        verbose_name_plural = 'Conductores'


class Propietario(models.Model):
    propietario = models.CharField(max_length=100)
    documento = models.CharField(max_length=12)
    estado = models.CharField(max_length=2, choices=(('1', 'Activo'), ('2', 'Inactivo')), default=1)

    def __str__(self):
        return str(self.propietario)

    class Meta:
        verbose_name_plural = 'Propietarios'


class Sede(models.Model):
    sede = models.CharField(max_length=250)
    tipo = models.CharField(max_length=2, choices=(('1','Terminal'),('2','Oficina'),('3','Paradero')), default='1')
    fecha_creado = models.DateTimeField(default=timezone.now)
    fecha_actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sede


class Bus(models.Model):
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, blank=True, null=True)
    numero_bus = models.CharField(max_length=5)
    placa_bus = models.CharField(max_length=8)
    asientos = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(50)])
    estado = models.CharField(max_length=2, choices=(('1', 'Activo'), ('2', 'Inactivo'), ), default=1)
    fecha_creado = models.DateTimeField(default=timezone.now)
    fecha_actualizado = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = 'Buses'

    def __str__(self):
        return self.numero_bus


class Programacion(models.Model):
    codigo = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    origen = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='origen')
    destino = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='destino')
    programacion = models.DateTimeField()
    precio = models.IntegerField(default=0, validators=[MinValueValidator(5000), MaxValueValidator(75000)])
    estado = models.CharField(max_length=2, choices=(('0','Cancelado'),('1','Despachado')), default=1)
    fecha_creado = models.DateTimeField(default=timezone.now)
    fecha_actualizado = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.codigo + ' - ' + self.bus.numero_bus)

    class Meta:
        verbose_name_plural = 'Programación'


class Encomienda(models.Model):
    programacion = models.ForeignKey(Programacion, on_delete=models.CASCADE)
    nombre_envio = models.CharField(max_length=100)
    cedula_envio = models.CharField(max_length=12)
    telefono_envio = models.CharField(max_length=12)
    nombre_recibido = models.CharField(max_length=100)
    cedula_recibido = models.CharField(max_length=12)
    telefono_recibido = models.CharField(max_length=12)
    codigo_encomienda = models.CharField(max_length=5)
    #costo_envio
    caracteristicas = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1000), MaxValueValidator(100000)])
    estado = models.CharField(max_length=2, choices=(('1', 'Programada'), ('2', 'Entregada')), default=1)
    fecha_creado = models.DateTimeField(default=timezone.now)
    fecha_actualizado = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.nombre_envio
