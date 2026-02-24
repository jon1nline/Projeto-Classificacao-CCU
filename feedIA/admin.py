from django.contrib import admin
from .models import FeedbackIA, ClassificacaoHistorico


@admin.register(FeedbackIA)
class FeedbackIAAdmin(admin.ModelAdmin):
    list_display = ('classificacao', 'texto_preview', 'criado_em')
    list_filter = ('classificacao', 'criado_em')
    search_fields = ('texto',)
    readonly_fields = ('criado_em',)
    ordering = ('-criado_em',)
    
    def texto_preview(self, obj):
        return obj.texto[:100] + '...' if len(obj.texto) > 100 else obj.texto
    texto_preview.short_description = 'Texto'


@admin.register(ClassificacaoHistorico)
class ClassificacaoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'risco_final', 'risco_ia', 'modificador_ner', 'total_entidades', 'data_classificacao')
    list_filter = ('risco_final', 'risco_ia', 'modificador_ner', 'data_classificacao')
    search_fields = ('paciente__nome', 'paciente__cartao_sus')
    readonly_fields = ('data_classificacao', 'paciente', 'risco_ia', 'risco_final', 'modificador_ner',
                       'hpv_types', 'lesions', 'exams', 'procedures', 'viral_loads',
                       'texto_original', 'texto_enriquecido')
    ordering = ('-data_classificacao',)
    
    fieldsets = (
        ('Paciente', {
            'fields': ('paciente', 'data_classificacao')
        }),
        ('Classificação', {
            'fields': ('risco_ia', 'risco_final', 'modificador_ner')
        }),
        ('Entidades NER', {
            'fields': ('hpv_types', 'lesions', 'exams', 'procedures', 'viral_loads'),
            'classes': ('collapse',)
        }),
        ('Textos', {
            'fields': ('texto_original', 'texto_enriquecido'),
            'classes': ('collapse',)
        }),
    )
