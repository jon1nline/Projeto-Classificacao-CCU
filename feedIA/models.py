from django.db import models
from datetime import datetime

# Create your models here.

class FeedbackIA(models.Model):
    RISK_LEVELS = [
        ('low', 'Baixo Risco'),
        ('medium', 'Médio Risco'),
        ('high', 'Alto Risco'),
    ]
    
    texto = models.TextField()
    classificacao = models.CharField(max_length=10, choices=RISK_LEVELS)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.classificacao} - {self.texto[:50]}"
    
    class Meta:
        ordering = ['-criado_em']


class ClassificacaoHistorico(models.Model):
    """Histórico de classificações de risco com informações de NER"""
    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.CASCADE, related_name='historico_classificacoes')
    data_classificacao = models.DateTimeField(auto_now_add=True)
    
    # Classificação
    risco_ia = models.CharField(max_length=10, help_text="Classificação original da IA")
    risco_final = models.CharField(max_length=10, help_text="Classificação final após NER")
    modificador_ner = models.IntegerField(default=0, help_text="Modificador aplicado pelo NER (-1, 0, +1)")
    
    # Entidades identificadas
    hpv_types = models.JSONField(default=list, blank=True)
    lesions = models.JSONField(default=list, blank=True)
    exams = models.JSONField(default=list, blank=True)
    procedures = models.JSONField(default=list, blank=True)
    viral_loads = models.JSONField(default=list, blank=True)
    
    # Texto analisado
    texto_original = models.TextField(blank=True)
    texto_enriquecido = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-data_classificacao']
        verbose_name = "Histórico de Classificação"
        verbose_name_plural = "Históricos de Classificação"
    
    def __str__(self):
        return f"{self.paciente.nome} - {self.risco_final} em {self.data_classificacao.strftime('%d/%m/%Y %H:%M')}"
    
    def tem_modificacao_ner(self):
        """Verifica se houve modificação pela análise NER"""
        return self.modificador_ner != 0
    
    def total_entidades(self):
        """Retorna o total de entidades identificadas"""
        return (
            len(self.hpv_types) + 
            len(self.lesions) + 
            len(self.exams) + 
            len(self.procedures) + 
            len(self.viral_loads)
        )
