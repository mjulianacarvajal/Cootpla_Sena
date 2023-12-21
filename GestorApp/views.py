
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.management import call_command

from django.shortcuts import render,redirect
import json
from django.contrib import messages
from django.http import HttpResponse,HttpRequest
from .forms import RegistrarUsuario, ActualizarPerfil,ActualizarContrasena,GuardarSede, GuardarBus,GuardarProgramacion, GuardarEncomienda
from .models import Sede, Bus, Programacion, Encomienda,Propietario, Conductor

from datetime import datetime

from django.db.models import Q, QuerySet

from django.utils import timezone

context = {
    'page_title' : 'Visor de Viajes Intermunicipales',
}


def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Usuario o Contraseña: Incorrecta"
        else:
            resp['msg'] = "Usuario o Contraseña: Incorrecta"
    return HttpResponse(json.dumps(resp),content_type='application/json')

@login_required
def inicio(request: HttpRequest):
    context = {}
    context['page_title'] = 'Inicio'
    context['buses'] = Bus.objects.count()
    context['encomiendas'] = Encomienda.objects.count()
    context['programaciones'] = Programacion.objects.filter(estado= 1, programacion__gt = datetime.today()).count()
    context['username'] = User.objects.count()

    labels = []
    data = []
  
    queryset = Bus.objects.order_by('estado')
    for buses_c in queryset:
        if buses_c.estado == '1':
            labels.append(buses_c.numero_bus)
            data.append(buses_c.asientos)       

    context = {
        'labels': labels,
        'data': data,
    }


    return render(request,'inicio.html',context)



def logoutuser(request: HttpRequest):
    logout(request)
    return redirect('/')


@login_required
def registrarUsuario(request: HttpRequest):
    user = request.user
    context['page_title'] = "Registrar Usuario"
    if request.method == 'POST':
        data = request.POST.copy()
        form = RegistrarUsuario(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('inicio')
        else:
            context['reg_form'] = form
    return render(request,'registro.html',context)


@login_required
def perfil(request: HttpRequest):
    context['page_title'] = 'Pelfil del Usuario'
    return render(request, 'perfil.html',context)


@login_required
def actualizarPerfil(request: HttpRequest):
    context['page_title'] = 'Actualizar Perfil'
    user = User.objects.get(id=request.user.id)
    if not request.method == 'POST':
        form = ActualizarPerfil(instance=user)
        context['form'] = form
        print(form)
    else:
        form = ActualizarPerfil(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect("perfil")
        else:
            context['form'] = form

    return render(request, 'gestion_perfil.html', context)


@login_required
def actualizarContrasena(request: HttpRequest):
    context['page_title'] = "Actualizar Contraseña"
    if request.method == 'POST':
        form = ActualizarContrasena(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Contraseña actualizada correctamente")
            update_session_auth_hash(request, form.user)
            return redirect("perfil")
        else:
            context['form'] = form
    else:
        form = ActualizarContrasena(request.POST)
        context['form'] = form
    return render(request,'actualizar_contrasena.html',context)


@login_required
def sede(request: HttpRequest):
    semaforo = {
        '1': 'bg-primary',
        '2': 'bg-secondary',
        '3': 'bg-success',
    }
    context['page_title'] = "Sedes"
    sedes = Sede.objects.all()
    context['sedes'] = sedes
    context['semaforo'] = semaforo
    return render(request, 'sede.html', context)


@login_required
def guardar_sede(request: HttpRequest):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        id_value = request.POST.get('id')
        if id_value and id_value.isnumeric():
            sede = Sede.objects.get(pk=id_value)
        else:
            sede = None
        if sede is None:
            form = GuardarSede(request.POST)
        else:
            form = GuardarSede(request.POST, instance=sede)
        if form.is_valid():
            form.save()
            messages.success(request, 'La Sede se ha guardado exitosamente.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No se han guardado datos.'
    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def adm_sede(request: HttpRequest, pk: str | None = None):
    context['page_title'] = "Gestion de Sedes"
    if pk != None:
        sede = Sede.objects.get(id=pk)
        context['sede'] = sede
    else:
        context['sede'] = {}

    return render(request, 'adm_sede.html', context)


@login_required
def eliminar_sede(request: HttpRequest):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        try:
            sede = Sede.objects.get(id=request.POST['id'])
            sede.delete()
            messages.success(request, 'La Sede se ha eliminado exitosamente')
            resp['status'] = 'success'
        except Sede.DoesNotExist as err:
            resp['msg'] = 'La Sede no se pudo eliminar'
            print(err)

    else:
        resp['msg'] = 'La Sede no se pudo eliminar'

    return HttpResponse(json.dumps(resp), content_type="application/json")


# bus
@login_required
def bus(request: HttpRequest):
    context['page_title'] = "Buses"
    buses = Bus.objects.all()
    context['buses'] = buses
    return render(request, 'bus.html', context)

@login_required
def guardar_bus(request:HttpRequest):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        id_value = request.POST.get('id')
        if id_value and id_value.isnumeric():
            bus = Bus.objects.get(pk=id_value)
        else:
            bus = None
        if bus is None:
            form = GuardarBus(request.POST)
        else:
            form = GuardarBus(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'El Bus se ha guardado exitosamente')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No se han guardado datos.'
    return HttpResponse(json.dumps(resp), content_type='application/json')




# @login_required
# def guardar_bus(request: HttpRequest):
#     resp = {'status': 'failed', 'msg': ''}
#     if request.method == 'POST':
#         form = GuardarBus(data=request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'El Bus se ha guardado exitosamente')
#             resp['status'] = 'success'
#         else:
#             for fields in form:
#                 for error in fields.errors:
#                     resp['msg'] += str(error + "<br>")
#     else:
#         resp['msg'] = 'No se han guardado datos.'
#     return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def adm_bus(request: HttpRequest, pk: str | None = None):
    context['page_title'] = "Gestión de Buses"
    propietarios = Propietario.objects.all()
    context['propietarios'] = propietarios
    
    if pk != None:
        bus = Bus.objects.get(id=pk)
        context['bus'] = bus
    else:
        context['bus'] = {}

    return render(request, 'adm_bus.html', context)


@login_required
def eliminar_bus(request: HttpRequest):
    resp = {'status': 'failed', 'msg': ''}
    print(f"datos: {request}")
    if request.method == 'POST':
        
        try:
            bus = Bus.objects.get(id=request.POST['id'])
            bus.delete()
            messages.success(request, 'El Bus se ha guardado exitosamente.')
            resp['status'] = 'success'
        except Bus.DoesNotExist as err:
            resp['msg'] = 'El Bus no se pudo eliminar'
            print(err)
    else:
        resp['msg'] = 'El Bus no se pudo eliminar'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def programacion(request: HttpRequest):
    context['page_title'] = "Progamación"
    programaciones = Programacion.objects.all()
    context['programaciones'] = programaciones
    return render(request, 'programacion.html', context)


@login_required
def guardar_programacion(request: HttpRequest):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        form = GuardarProgramacion(request.POST)
        if form.is_valid():
            programacion = form.save(commit=False)
            # convierte la hora a la zona horaria por defecto
            programacion.programacion = timezone.make_aware(programacion.programacion, timezone.get_default_timezone())
            programacion.save()
            messages.success(request, 'La Programación se ha guardado exitosamente.')
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No se han guardado datos.'
    return HttpResponse(json.dumps(resp), content_type='application/json')



#
#
# @login_required
# def adm_programacion(request: HttpRequest, pk: str | None = None):
#     context['page_title'] = "Gestión Programación"
#     buses = Bus.objects.filter(estado=1).all()
#     sedes = Sede.objects.filter(tipo=1).all()
#     conductores = Conductor.objects.filter(estado=1)
#     context['buses'] = buses
#     context['sedes'] = sedes
#     context['conductores'] = conductores
#
#     if pk != None:
#         programacion = Programacion.objects.get(id=pk)
#         context['programacion'] = programacion
#     else:
#         context['programacion'] = {}
#
#     return render(request, 'adm_programacion.html', context)

@login_required
def adm_programacion(request, pk=None):
    context['page_title'] = "Manage Schedule"
    buses = Bus.objects.all()
    sedes = Sede.objects.all()
    conductores = Conductor.objects.all()

    context['buses'] = buses
    context['sedes'] = sedes
    context['conductores'] = conductores

    if not pk is None:
        programacion = Programacion.objects.get(id = pk)
        context['programacion'] = programacion
    else:
        context['programacion'] = {}

    return render(request, 'adm_programacion.html', context)



@login_required
def eliminar_programacion(request: HttpRequest):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        try:
            programacion = Programacion.objects.get(id=request.POST['id'])
            programacion.delete()
            messages.success(request, 'La Programación ha eliminado exitosamente')
            resp['status'] = 'success'
        except Programacion.DoesNotExist as err:
            resp['msg'] = 'La Programación no se pudo eliminar'
            print(err)

    else:
        resp['msg'] = 'La Programación no se pudo eliminar'

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def encomienda(request: HttpRequest):
    context['page_title'] = "Encomienda"
    encomiendas = Encomienda.objects.all()
    context['encomiendas'] = encomiendas

    return render(request, 'encomienda.html', context)


@login_required
def guardar_encomienda(request: HttpRequest):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        form = GuardarEncomienda(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La encomienda ha guardado exitosamente')
            resp['status'] = 'success'
    else:
        for fields in form:
            for error in fields.errors:
                resp['msg'] += str(error + "<br>")
        else:
            resp['msg'] = 'No se han guardado datos.'
    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def adm_encomienda(request: HttpRequest, pk: str | None = None):
    context['page_title'] = "Gestión de Encomiendas"

    encomiendas = Encomienda.objects.all()
    context['encomiendas'] = encomiendas
    if not pk is None:
        programacion = Bus.objects.get(id=pk)
        context['programacion'] = programacion
    else:
        context['programacion'] = {}

    return render(request, 'adm_encomienda.html', context)


@login_required
def eliminar_encomienda(request: HttpRequest):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        try:
            encomienda = Encomienda.objects.get(id=request.POST['id'])
            encomienda.delete()
            messages.success(request, 'La Encomienda se ha guardado exitosamente.')
            resp['status'] = 'success'
        except Encomienda.DoesNotExist as err:
            resp['msg'] = 'El Bus no se pudo eliminar'
            print(err)

    else:
        resp['msg'] = 'La Encomienda no se pudo eliminar'

    return HttpResponse(json.dumps(resp), content_type="application/json")


def buscar_programado(request: HttpRequest):
    context['page_title'] = 'Buscar Viajes Programacions'
    context['sedes'] = Sede.objects.filter(tipo__gt = 0).all
    today = datetime.today().strftime("%Y-%m-%d")
    context['today'] = today
    return render(request, 'buscar_viaje.html', context)


def viajes_programados(request: HttpRequest):
    if not request.method == 'POST':
        context['page_title'] = "Viajes Programacions"
        programaciones = Programacion.objects.filter(estado=1, programacion__gt=datetime.now()).all()
        context['programaciones'] = programaciones
        context['is_searched'] = False
        context['data'] = {}
    else:
        context['page_title'] = "Resultados | Viajes Programacions"
        context['is_searched'] = True
        date = datetime.strptime(request.POST['date'],"%Y-%m-%d").date()
        year= date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        origen = Sede.objects.get(id=request.POST['origen'])
        destino = Sede.objects.get(id=request.POST['destino'])
        programaciones = Programacion.objects.filter(Q(estado=1) & Q(programacion__year=year) & Q(programacion__month=month) & Q(programacion__day=day) & Q(Q(origen=origen) | Q(destino=destino))).all()
        context['programaciones'] = programaciones
        context['data'] = {'date':date,'origen': origen, 'destino': destino}

    return render(request, 'viajes_programados.html', context)


def base(request: HttpRequest):
    call_command('dbbackup')
    return HttpResponse('db creada')


def contacto(request: HttpRequest):
    context={}
    return render(request,'contacto.html',context)

