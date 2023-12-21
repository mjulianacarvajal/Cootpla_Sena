from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm

from django.contrib.auth.models import User

from .models import Encomienda, Sede, Bus, Programacion
from datetime import datetime

import random

class RegistrarUsuario(UserCreationForm):
    email = forms.EmailField(max_length=250, help_text="El sistema requiere un correo electrónico para asignar un nuevo usuario.")
    first_name = forms.CharField(max_length=250, help_text="El sistema requiere un nombre para completar los datos.")
    last_name = forms.CharField(max_length=250, help_text="El sistema requiere un apellido para completar los datos.")

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"{user.email} es un correo ya existente en el sistema")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"{user.username} es un usuario ya existente en el sistema")


class ActualizarContrasena(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm rounded-0'}),
        label="Contraseña Anterior")
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm rounded-0'}),
        label="Nueva Constraseña")
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm rounded-0'}),
        label="Confirmar Nueva Contraseña")

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class ActualizarPerfil(UserChangeForm):
    username = forms.CharField(max_length=250, help_text="Asignar un usuario es requerido.")
    email = forms.EmailField(max_length=250, help_text="Asignar un correo electronico es requerido.")
    first_name = forms.CharField(max_length=250, help_text="Asignar un nombre para este usuario es requerido.")
    last_name = forms.CharField(max_length=250, help_text="Asignar  un apellido para este usuario es requerido.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Contraseña Incorrecta")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email=email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"{user.email} es un correo ya existente en el sistema")

    def clean_username(self):

        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username=username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"{user.username} es un nick ya existente en el sistema")


"""

No son necesarios en forms verdad??
Se llaman cuando se necesita o si toca crear forms asi se herenden


class GuardarConductor(forms.ModelForm):
    conductor = forms.CharField(max_length=100)
    codigo = forms.IntegerField(max_length=5)
    cedula = forms.IntegerField(max_length=12)
    estado = forms.ChoiceField(choices=[('1', 'Activo'), ('2', 'Inactivo')])

    class Meta:
        model = Conductor
        fields = ('conductor', 'caracteristicas', 'estado')

class GuardarPropietario(forms.ModelForm):
    propietario = forms.CharField(max_length=100)
    documentoo = forms.IntegerField(max_length=5)


    class Meta:
        model = Propietario
        fields = (' propietario', 'documento', )      

"""


class GuardarSede(forms.ModelForm):
    sede = forms.CharField(max_length="25")
    tipo = forms.ChoiceField(choices=[('1', 'Terminal'), ('2', 'Oficina'), ('3', 'Paradero')])

    class Meta:
        model = Sede
        fields = ('sede', 'tipo',)

    def clean_sede(self):
        id = self.instance.id if self.instance.id else 0
        sede = self.cleaned_data['sede']

        try:
            if int(id) > 0:
                loc = Sede.objects.exclude(id=id).get(sede=sede)
            else:
                loc = Sede.objects.get(sede=sede)
        except:
            return sede

        raise forms.ValidationError(f"{sede} Sede ya existente en el sistema.")


####
class GuardarBus(forms.ModelForm):

    class Meta:
        model = Bus
        fields = ('propietario', 'numero_bus', 'placa_bus', 'asientos', 'estado')

    def clean_numero_bus(self):
        id = self.instance.id if self.instance.id else 0
        numero_bus = self.cleaned_data['numero_bus']
        # print(int(id) > 0)
        try:
            if int(id) > 0:
                bus = Bus.objects.exclude(id=id).get(numero_bus=numero_bus)
            else:
                bus = Bus.objects.get(numero_bus=numero_bus)
        except:
            return numero_bus
            # raise forms.ValidationError(f"{bus_number} Category Already Exists.")
        raise forms.ValidationError(f"{numero_bus}: Este bus ya existe en sistema")

    def clean_placa_bus(self):
        id = self.instance.id if self.instance.id else 0
        placa_bus = self.cleaned_data['placa_bus']
        # print(int(id) > 0)
        try:
            if int(id) > 0:

                bus = Bus.objects.exclude(id=id).get(placa_bus=placa_bus)
            else:
                bus = Bus.objects.get(placa_bus=placa_bus)
        except:
            return placa_bus.upper()
            # raise forms.ValidationError(f"{bus_number} Category Already Exists.")
        raise forms.ValidationError(f"{placa_bus}: Esta placa ya existe en sistema")
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     origen = cleaned_data.get('origen')
    #     destino = cleaned_data.get('destino')

    #     # Verificar si ya existe una Programacion con la misma ruta y destino
    #     if Programacion.objects.filter(origen=origen, destino=destino).exclude(id=self.instance.id).exists():
    #         raise forms.ValidationError('Ya existe una Programacion con la misma ruta y destino.')

    #     return cleaned_data


from .models import Conductor

class GuardarProgramacion(forms.ModelForm):
    codigo = forms.CharField(max_length="250")
    programacion = forms.CharField()
    conductor = forms.ModelChoiceField(queryset=Conductor.objects.all(), required=True)

    class Meta:
        model = Programacion
        fields = ('codigo', 'bus', 'origen', 'destino', 'precio', 'programacion', 'estado', 'conductor')

    def clean_codigo(self):
        id = self.instance.id if self.instance.id else 0
        if id > 0:
            try:
                programacion = Programacion.objects.get(id=id)
                return programacion.codigo
            except:
                codigo = ''
        else:
            codigo = ''
        pref = datetime.today().strftime('%Y%m%d')
        codigo = str(1).zfill(4)
        while True:
            prog = Programacion.objects.filter(codigo=str(pref + codigo)).count()
            if prog > 0:
                codigo = str(int(codigo) + 1).zfill(4)
            else:
                codigo = str(pref + codigo)
                break
        return codigo





class GuardarEncomienda(forms.ModelForm):
    programacion = forms.CharField()
    codigo = forms.CharField()
    nombre_envio = forms.CharField(max_length="100")
    cedula_envio = forms.CharField(max_length="12")
    telefono_envio = forms.CharField(max_length="12")
    nombre_recibido = forms.CharField(max_length="100")
    cedula_recibido = forms.CharField(max_length="12")
    telefono_recibido = forms.CharField(max_length="12")
    codigo_encomienda = forms.CharField(max_length="5")
    estado = forms.ChoiceField(choices=[('1', 'Programada'), ('2', 'Entregada')])

    # 0 Aplazada, 1 Programada, 2 Entregada 3 Devuelta

    class Meta:
        model = Encomienda
        fields = ('programacion', 'codigo', 'nombre_envio', 'cedula_envio', 'telefono_envio', 'nombre_recibido',
                  'cedula_recibido', 'telefono_recibido', 'codigo_encomienda', 'estado',)

    """
    #asignar un código aleatorio
    def clean_codigo(self):
        id = self.instance.id if self.instance.id else 0
        if id > 0:
            try:
                encomienda = Encomienda.objects.get(id=id)
                return encomienda.codigo_encomienda
            except:
                codigo = ''
            else:
                codigo = ''
            pref = random.randint(1000,99999)

            while True:
                enc = Encomienda.objects.filter(codigo=str(pref))
                if prog > 0:
                    codigo_encomienda = str(int(pref))
                else:
                    codigo_encomienda = str(pref)
                    break
            return codigo_encomienda
    """




