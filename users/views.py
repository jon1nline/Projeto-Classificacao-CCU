from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegistroForm, LoginForm
from pacientes.models import Paciente


def registro(request):
    """View para registro de novos usuários"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = RegistroForm()
    
    return render(request, 'users/registro.html', {'form': form})


def login_view(request):
    """View para login de usuários"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """View para logout de usuários"""
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """View do dashboard (página principal após login)"""
    # Obter estatísticas de pacientes
    total_pacientes = Paciente.objects.count()
    pacientes_recentes = Paciente.objects.all()[:5]
    
    context = {
        'total_pacientes': total_pacientes,
        'pacientes_recentes': pacientes_recentes,
    }
    
    return render(request, 'users/dashboard.html', context)
