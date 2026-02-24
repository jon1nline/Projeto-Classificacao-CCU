from django.contrib import admin
from .models import (
    Paciente, HistoricoSexual, HistoricoReprodutivo, Vacinacao,
    ExameDnaHpv, CitopatologicoHistorico, ProcedimentoRealizado, StatusSeguimento
)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cartao_sus', 'data_nascimento', 'cidade', 'estado', 'area_rural', 'criado_em')
    list_filter = ('estado', 'escolaridade', 'sexualidade', 'area_rural', 'perda_seguimento', 'criado_em')
    search_fields = ('nome', 'cartao_sus', 'cidade')
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'data_nascimento', 'cartao_sus', 'cor', 'sexualidade', 'escolaridade')
        }),
        ('Endereço', {
            'fields': ('rua', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Vulnerabilidade Social', {
            'fields': ('area_rural', 'perda_seguimento', 'primeira_vez_rastreamento', 'observacoes_vulnerabilidade'),
            'description': 'Fatores socioeconômicos e geográficos que podem elevar o risco'
        }),
        ('Metadata', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HistoricoSexual)
class HistoricoSexualAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'idade_inicio_atividade_sexual', 'numero_parceiros', 'atualizado_em')
    search_fields = ('paciente__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(HistoricoReprodutivo)
class HistoricoReprodutivouAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'numero_gestacoes', 'atualizado_em')
    search_fields = ('paciente__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(Vacinacao)
class VacinacaoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'status_vacinacao', 'data_primeira_dose', 'atualizado_em')
    list_filter = ('status_vacinacao', 'data_primeira_dose')
    search_fields = ('paciente__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(ExameDnaHpv)
class ExameDnaHpvAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'data_exame', 'tipo_hpv', 'resultado')
    list_filter = ('data_exame', 'tipo_hpv')
    search_fields = ('paciente__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(CitopatologicoHistorico)
class CitopatologicoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'data_exame', 'resultado')
    list_filter = ('data_exame', 'resultado')
    search_fields = ('paciente__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(ProcedimentoRealizado)
class ProcedimentoRealizadoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo_procedimento', 'data_procedimento')
    list_filter = ('tipo_procedimento', 'data_procedimento')
    search_fields = ('paciente__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(StatusSeguimento)
class StatusSeguimentoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'classificacao_risco', 'score_total', 'atualizado_em')
    list_filter = ('classificacao_risco', 'atualizado_em')
    search_fields = ('paciente__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        ('Classificação', {
            'fields': ('paciente', 'classificacao_risco', 'score_total', 'justificativas')
        }),
        ('Entidades Clínicas Extraídas', {
            'fields': ('hpv_types', 'lesions', 'exams', 'procedures', 'viral_loads'),
            'classes': ('collapse',)
        }),
        ('Vulnerabilidade Social Extraída', {
            'fields': ('social_factors', 'geographic_factors', 'behavioral_factors', 'follow_up_issues'),
            'classes': ('collapse',),
            'description': 'Fatores de vulnerabilidade identificados pelo NER'
        }),
        ('Metadata', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
