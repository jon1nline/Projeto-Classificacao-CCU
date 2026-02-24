from django import forms
from .models import (
    Paciente, HistoricoSexual, HistoricoReprodutivo, Vacinacao,
    ExameDnaHpv, CitopatologicoHistorico, ProcedimentoRealizado, StatusSeguimento
)


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nome', 'data_nascimento', 'cartao_sus', 'cor', 
                  'sexualidade', 'escolaridade', 'rua', 'bairro', 'cidade', 'estado', 'cep',
                  'area_rural', 'perda_seguimento', 'primeira_vez_rastreamento', 'observacoes_vulnerabilidade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cartao_sus': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cartão SUS'}),
            'cor': forms.Select(attrs={'class': 'form-control'}),
            'sexualidade': forms.Select(attrs={'class': 'form-control'}),
            'escolaridade': forms.Select(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'area_rural': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'perda_seguimento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'primeira_vez_rastreamento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes_vulnerabilidade': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva fatores de vulnerabilidade social, barreiras de acesso, etc.'}),
        }
        labels = {
            'cor': 'Grupo étnico',
            'area_rural': 'Reside em área rural ou difícil acesso?',
            'perda_seguimento': 'Histórico de perda de seguimento?',
            'primeira_vez_rastreamento': 'Primeira vez no rastreamento?',
            'observacoes_vulnerabilidade': 'Observações sobre vulnerabilidade social',
        }


class HistoricoSexualForm(forms.ModelForm):
    class Meta:
        model = HistoricoSexual
        fields = ['idade_inicio_atividade_sexual', 'numero_parceiros']
        widgets = {
            'idade_inicio_atividade_sexual': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Idade (anos)',
                'min': '1',
                'max': '100'
            }),
            'numero_parceiros': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de parceiros',
                'min': '0'
            }),
        }


class HistoricoReprodutivouForm(forms.ModelForm):
    class Meta:
        model = HistoricoReprodutivo
        fields = ['numero_gestacoes', 'historico_ists']
        widgets = {
            'numero_gestacoes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de gestações',
                'min': '0'
            }),
            'historico_ists': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva o histórico de ISTs',
                'rows': 4
            }),
        }


class VacinacaoForm(forms.ModelForm):
    class Meta:
        model = Vacinacao
        fields = ['status_vacinacao', 'data_primeira_dose', 'data_segunda_dose', 'data_terceira_dose', 'observacoes']
        widgets = {
            'status_vacinacao': forms.Select(attrs={'class': 'form-control'}),
            'data_primeira_dose': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_segunda_dose': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_terceira_dose': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ExameDnaHpvForm(forms.ModelForm):
    class Meta:
        model = ExameDnaHpv
        fields = ['data_exame', 'tipo_hpv', 'carga_viral', 'resultado', 'observacoes']
        widgets = {
            'data_exame': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_hpv': forms.Select(attrs={'class': 'form-control'}),
            'carga_viral': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1000 cópias/mL'}),
            'resultado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resultado do exame'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CitopatologicoHistoricoForm(forms.ModelForm):
    class Meta:
        model = CitopatologicoHistorico
        fields = ['data_exame', 'resultado', 'observacoes']
        widgets = {
            'data_exame': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resultado': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProcedimentoRealizadoForm(forms.ModelForm):
    class Meta:
        model = ProcedimentoRealizado
        fields = ['tipo_procedimento', 'data_procedimento', 'resultado', 'complicacoes']
        widgets = {
            'tipo_procedimento': forms.Select(attrs={'class': 'form-control'}),
            'data_procedimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resultado': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'complicacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StatusSeguimentoForm(forms.ModelForm):
    class Meta:
        model = StatusSeguimento
        fields = ['classificacao_risco']
        widgets = {
            'classificacao_risco': forms.Select(attrs={'class': 'form-control'}),
        }
