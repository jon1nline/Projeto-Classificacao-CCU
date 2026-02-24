from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from datetime import date
import json
from .models import (
    Paciente, HistoricoSexual, HistoricoReprodutivo, Vacinacao,
    ExameDnaHpv, CitopatologicoHistorico, ProcedimentoRealizado, StatusSeguimento
)
from .forms import (
    PacienteForm, HistoricoSexualForm, HistoricoReprodutivouForm, VacinacaoForm,
    ExameDnaHpvForm, CitopatologicoHistoricoForm, ProcedimentoRealizadoForm, StatusSeguimentoForm
)
from .utils import build_patient_text
from feedIA.ner import extract_entities


@login_required(login_url='login')
def lista_pacientes(request):
    """Lista todos os pacientes cadastrados"""
    pacientes = Paciente.objects.all()
    return render(request, 'pacientes/lista_pacientes.html', {'pacientes': pacientes})


@login_required(login_url='login')
def novo_paciente(request):
    """Criar um novo paciente"""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            # Criar registros associados vazios (evitar duplicidade com sinais)
            StatusSeguimento.objects.get_or_create(paciente=paciente)
            messages.success(request, f'Paciente {paciente.nome} cadastrado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PacienteForm()
    
    return render(request, 'pacientes/novo_paciente.html', {'form': form})


@login_required(login_url='login')
def detalhes_paciente(request, pk):
    """Exibir detalhes de um paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Tentar obter os dados relacionados ou None
    historico_sexual = getattr(paciente, 'historico_sexual', None)
    historico_reprodutivo = getattr(paciente, 'historico_reprodutivo', None)
    vacinacao = getattr(paciente, 'vacinacao', None)
    status_seguimento = getattr(paciente, 'status_seguimento', None)
    
    exames_dna = paciente.exames_dna_hpv.all()
    citopatologicos = paciente.citopatologicos.all()
    procedimentos = paciente.procedimentos.all()
    
    # Extrair entidades médicas do texto do paciente
    patient_text = build_patient_text(paciente)
    entities = extract_entities(patient_text)
    
    context = {
        'paciente': paciente,
        'historico_sexual': historico_sexual,
        'historico_reprodutivo': historico_reprodutivo,
        'vacinacao': vacinacao,
        'status_seguimento': status_seguimento,
        'exames_dna': exames_dna,
        'citopatologicos': citopatologicos,
        'procedimentos': procedimentos,
        'entities': entities,
        'patient_text': patient_text,
    }
    
    return render(request, 'pacientes/detalhes_paciente.html', context)


@login_required(login_url='login')
def editar_paciente(request, pk):
    """Editar dados básicos do paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente atualizado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'pacientes/editar_paciente.html', {'form': form, 'paciente': paciente})


@login_required(login_url='login')
def adicionar_historico_sexual(request, pk):
    """Adicionar/editar histórico sexual"""
    paciente = get_object_or_404(Paciente, pk=pk)
    historico, created = HistoricoSexual.objects.get_or_create(paciente=paciente)
    
    if request.method == 'POST':
        form = HistoricoSexualForm(request.POST, instance=historico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Histórico sexual atualizado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
    else:
        form = HistoricoSexualForm(instance=historico)
    
    return render(request, 'pacientes/formulario_historico.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Histórico Sexual',
        'descricao': 'Informações sobre o início da atividade sexual e parceiros'
    })


@login_required(login_url='login')
def adicionar_historico_reprodutivo(request, pk):
    """Adicionar/editar histórico reprodutivo"""
    paciente = get_object_or_404(Paciente, pk=pk)
    historico, created = HistoricoReprodutivo.objects.get_or_create(paciente=paciente)
    
    if request.method == 'POST':
        form = HistoricoReprodutivouForm(request.POST, instance=historico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Histórico reprodutivo atualizado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
    else:
        form = HistoricoReprodutivouForm(instance=historico)
    
    return render(request, 'pacientes/formulario_historico.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Histórico Reprodutivo',
        'descricao': 'Informações sobre gestações e histórico de ISTs'
    })


@login_required(login_url='login')
def adicionar_vacinacao(request, pk):
    """Adicionar/editar vacinação"""
    paciente = get_object_or_404(Paciente, pk=pk)
    vacinacao, created = Vacinacao.objects.get_or_create(paciente=paciente)
    
    if request.method == 'POST':
        form = VacinacaoForm(request.POST, instance=vacinacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de vacinação atualizado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
    else:
        form = VacinacaoForm(instance=vacinacao)
    
    return render(request, 'pacientes/formulario_historico.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Vacinação HPV',
        'descricao': 'Registro de vacinação contra o HPV'
    })


@login_required(login_url='login')
def adicionar_exame_dna_hpv(request, pk):
    """Adicionar novo exame DNA-HPV"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = ExameDnaHpvForm(request.POST)
        if form.is_valid():
            exame = form.save(commit=False)
            exame.paciente = paciente
            exame.save()
            messages.success(request, 'Exame DNA-HPV registrado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
    else:
        form = ExameDnaHpvForm()
    
    return render(request, 'pacientes/formulario_historico.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Novo Exame DNA-HPV',
        'descricao': 'Registre os resultados de um novo exame de DNA-HPV'
    })


@login_required(login_url='login')
def adicionar_citopatologico(request, pk):
    """Adicionar novo exame citopatológico"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = CitopatologicoHistoricoForm(request.POST)
        if form.is_valid():
            exame = form.save(commit=False)
            exame.paciente = paciente
            exame.save()
            messages.success(request, 'Exame citopatológico registrado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
    else:
        form = CitopatologicoHistoricoForm()
    
    return render(request, 'pacientes/formulario_historico.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Novo Exame Citopatológico',
        'descricao': 'Registre os resultados de um novo Papanicolau'
    })


@login_required(login_url='login')
def adicionar_procedimento(request, pk):
    """Adicionar novo procedimento"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = ProcedimentoRealizadoForm(request.POST)
        if form.is_valid():
            procedimento = form.save(commit=False)
            procedimento.paciente = paciente
            procedimento.save()
            messages.success(request, 'Procedimento registrado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
    else:
        form = ProcedimentoRealizadoForm()
    
    return render(request, 'pacientes/formulario_historico.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Novo Procedimento',
        'descricao': 'Registre um novo procedimento realizado'
    })


@login_required(login_url='login')
def adicionar_status_seguimento(request, pk):
    """Adicionar/editar status de seguimento"""
    paciente = get_object_or_404(Paciente, pk=pk)
    status, created = StatusSeguimento.objects.get_or_create(paciente=paciente)
    
    if request.method == 'POST':
        form = StatusSeguimentoForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status de seguimento atualizado com sucesso!')
            return redirect('detalhes_paciente', pk=paciente.pk)
    else:
        form = StatusSeguimentoForm(instance=status)
    
    return render(request, 'pacientes/formulario_historico.html', {
        'form': form,
        'paciente': paciente,
        'titulo': 'Classificação de Risco',
        'descricao': 'Risco calculado pela IA com base nos dados da paciente'
    })


@login_required(login_url='login')
def dados_coletados(request):
    """Dashboard de dados coletados para análise de risco"""
    pacientes = Paciente.objects.select_related('status_seguimento').all()

    risco_display = {
        'baixo': 'Baixo Risco',
        'medio': 'Médio Risco',
        'alto': 'Alto Risco'
    }
    risco_keys = ['baixo', 'medio', 'alto']

    def calcular_idade(data_nascimento):
        if not data_nascimento:
            return None
        hoje = date.today()
        return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

    # Estatísticas por risco (idade)
    idade_stats = {k: {'min': None, 'max': None, 'sum': 0, 'count': 0} for k in risco_keys}
    classificados_count = 0

    # Aggregações por categoria
    bairro_counts = {}
    cidade_counts = {}
    escolaridade_counts = {label: {k: 0 for k in risco_keys} for _, label in Paciente.ESCOLARIDADE_CHOICES}
    sexualidade_counts = {label: {k: 0 for k in risco_keys} for _, label in Paciente.SEXUALIDADE_CHOICES}

    escolaridade_map = dict(Paciente.ESCOLARIDADE_CHOICES)
    sexualidade_map = dict(Paciente.SEXUALIDADE_CHOICES)

    for paciente in pacientes:
        status = getattr(paciente, 'status_seguimento', None)
        risco = status.classificacao_risco if status else None
        if risco not in risco_keys:
            continue

        classificados_count += 1

        # Idade
        idade = calcular_idade(paciente.data_nascimento)
        if idade is not None:
            stats = idade_stats[risco]
            stats['min'] = idade if stats['min'] is None else min(stats['min'], idade)
            stats['max'] = idade if stats['max'] is None else max(stats['max'], idade)
            stats['sum'] += idade
            stats['count'] += 1

        # Bairro
        if paciente.bairro:
            bairro_counts.setdefault(paciente.bairro, {k: 0 for k in risco_keys})
            bairro_counts[paciente.bairro][risco] += 1

        # Cidade
        if paciente.cidade:
            cidade_counts.setdefault(paciente.cidade, {k: 0 for k in risco_keys})
            cidade_counts[paciente.cidade][risco] += 1

        # Escolaridade
        escolaridade_label = escolaridade_map.get(paciente.escolaridade)
        if escolaridade_label:
            escolaridade_counts[escolaridade_label][risco] += 1

        # Sexualidade
        sexualidade_label = sexualidade_map.get(paciente.sexualidade)
        if sexualidade_label:
            sexualidade_counts[sexualidade_label][risco] += 1

    # Preparar dados para gráficos
    idade_labels = [risco_display[k] for k in risco_keys]
    idade_min = [idade_stats[k]['min'] or 0 for k in risco_keys]
    idade_max = [idade_stats[k]['max'] or 0 for k in risco_keys]
    idade_avg = [
        round(idade_stats[k]['sum'] / idade_stats[k]['count'], 1) if idade_stats[k]['count'] > 0 else 0
        for k in risco_keys
    ]

    def top_categorias(counts_dict, limit=10):
        items = [
            (categoria, sum(contagens.values()), contagens)
            for categoria, contagens in counts_dict.items()
        ]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:limit]

    bairro_top = top_categorias(bairro_counts)
    cidade_top = top_categorias(cidade_counts)

    def split_counts(items):
        labels = [i[0] for i in items]
        baixo = [i[2]['baixo'] for i in items]
        medio = [i[2]['medio'] for i in items]
        alto = [i[2]['alto'] for i in items]
        return labels, baixo, medio, alto

    bairro_labels, bairro_baixo, bairro_medio, bairro_alto = split_counts(bairro_top)
    cidade_labels, cidade_baixo, cidade_medio, cidade_alto = split_counts(cidade_top)

    escolaridade_labels = list(escolaridade_counts.keys())
    escolaridade_baixo = [escolaridade_counts[l]['baixo'] for l in escolaridade_labels]
    escolaridade_medio = [escolaridade_counts[l]['medio'] for l in escolaridade_labels]
    escolaridade_alto = [escolaridade_counts[l]['alto'] for l in escolaridade_labels]

    sexualidade_labels = list(sexualidade_counts.keys())
    sexualidade_baixo = [sexualidade_counts[l]['baixo'] for l in sexualidade_labels]
    sexualidade_medio = [sexualidade_counts[l]['medio'] for l in sexualidade_labels]
    sexualidade_alto = [sexualidade_counts[l]['alto'] for l in sexualidade_labels]

    context = {
        'idade_labels': json.dumps(idade_labels),
        'idade_min': json.dumps(idade_min),
        'idade_max': json.dumps(idade_max),
        'idade_avg': json.dumps(idade_avg),
        'bairro_labels': json.dumps(bairro_labels),
        'bairro_baixo': json.dumps(bairro_baixo),
        'bairro_medio': json.dumps(bairro_medio),
        'bairro_alto': json.dumps(bairro_alto),
        'cidade_labels': json.dumps(cidade_labels),
        'cidade_baixo': json.dumps(cidade_baixo),
        'cidade_medio': json.dumps(cidade_medio),
        'cidade_alto': json.dumps(cidade_alto),
        'escolaridade_labels': json.dumps(escolaridade_labels),
        'escolaridade_baixo': json.dumps(escolaridade_baixo),
        'escolaridade_medio': json.dumps(escolaridade_medio),
        'escolaridade_alto': json.dumps(escolaridade_alto),
        'sexualidade_labels': json.dumps(sexualidade_labels),
        'sexualidade_baixo': json.dumps(sexualidade_baixo),
        'sexualidade_medio': json.dumps(sexualidade_medio),
        'sexualidade_alto': json.dumps(sexualidade_alto),
        'total_classificados': classificados_count
    }

    return render(request, 'pacientes/dados_coletados.html', context)
