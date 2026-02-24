from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Paciente(models.Model):
    COR_CHOICES = [
        ('branca', 'Branca'),
        ('preta', 'Preta'),
        ('amarela', 'Amarela'),
        ('parda', 'Parda'),
        ('indigena', 'Indígena'),
        ('outro','Outro'),
        ('nao_declarado', 'Não Declarado'),
    ]
    
    SEXUALIDADE_CHOICES = [
        ('heterosexual', 'Heterossexual'),
        ('homossexual', 'Homossexual'),
        ('bissexual', 'Bissexual'),
        ('asexual', 'Assexual'),
        ('transsexual', 'Transsexual'),
        ('prefiro_nao_responder', 'Prefiro não responder'),
    ]
    
    ESCOLARIDADE_CHOICES = [
        ('sem_escolaridade', 'Sem Escolaridade'),
        ('ensino_fundamental', 'Ensino Fundamental'),
        ('ensino_medio', 'Ensino Médio'),
        ('ensino_superior', 'Ensino Superior'),
        ('pos_graduacao', 'Pós-Graduação'),
        ('nao_declarado', 'Não Declarado'),
    ]
    
    ESTADO_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]
    
    nome = models.CharField(max_length=200)
    data_nascimento = models.DateField()
    cartao_sus = models.CharField(max_length=18, unique=True)
    cor = models.CharField(max_length=20, choices=COR_CHOICES, verbose_name='Grupo étnico')
    sexualidade = models.CharField(max_length=30, choices=SEXUALIDADE_CHOICES)
    escolaridade = models.CharField(max_length=30, choices=ESCOLARIDADE_CHOICES)
    
    # Endereço
    rua = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES)
    cep = models.CharField(max_length=9)
    
    # Fatores de vulnerabilidade social (opcional)
    area_rural = models.BooleanField(default=False, verbose_name='Reside em área rural/difícil acesso')
    perda_seguimento = models.BooleanField(default=False, verbose_name='Histórico de perda de seguimento')
    primeira_vez_rastreamento = models.BooleanField(default=False, verbose_name='Primeira vez no rastreamento')
    observacoes_vulnerabilidade = models.TextField(
        null=True, 
        blank=True,
        help_text='Observações sobre vulnerabilidade social, dificuldades de acesso, etc.'
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nome} - {self.cartao_sus}"
    
    class Meta:
        ordering = ['-criado_em']


class HistoricoSexual(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='historico_sexual')
    idade_inicio_atividade_sexual = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    numero_parceiros = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        null=True,
        blank=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Histórico Sexual - {self.paciente.nome}"
    
    class Meta:
        verbose_name_plural = "Históricos Sexuais"


class HistoricoReprodutivo(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='historico_reprodutivo')
    numero_gestacoes = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    historico_ists = models.TextField(
        null=True,
        blank=True,
        help_text="Descreva o histórico de Infecções Sexualmente Transmissíveis (ISTs) anteriores"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Histórico Reprodutivo - {self.paciente.nome}"
    
    class Meta:
        verbose_name_plural = "Históricos Reprodutivos"


class Vacinacao(models.Model):
    STATUS_CHOICES = [
        ('nao_vacinado', 'Não Vacinado'),
        ('parcialmente_vacinado', 'Parcialmente Vacinado'),
        ('totalmente_vacinado', 'Totalmente Vacinado'),
    ]
    
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='vacinacao')
    status_vacinacao = models.CharField(max_length=30, choices=STATUS_CHOICES)
    data_primeira_dose = models.DateField(null=True, blank=True)
    data_segunda_dose = models.DateField(null=True, blank=True)
    data_terceira_dose = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Vacinação - {self.paciente.nome}"


class ExameDnaHpv(models.Model):
    TIPO_HPV_CHOICES = [
        ('16', 'HPV 16 (Alto Risco)'),
        ('18', 'HPV 18 (Alto Risco)'),
        ('31', 'HPV 31 (Alto Risco)'),
        ('33', 'HPV 33 (Alto Risco)'),
        ('45', 'HPV 45 (Alto Risco)'),
        ('6', 'HPV 6 (Baixo Risco)'),
        ('11', 'HPV 11 (Baixo Risco)'),
        ('outro', 'Outro Tipo'),
        ('negativo', 'Negativo para HPV'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='exames_dna_hpv')
    data_exame = models.DateField()
    tipo_hpv = models.CharField(max_length=50, choices=TIPO_HPV_CHOICES)
    carga_viral = models.CharField(max_length=100, null=True, blank=True)
    resultado = models.CharField(max_length=50)
    observacoes = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"DNA-HPV {self.data_exame} - {self.paciente.nome}"
    
    class Meta:
        verbose_name = "Exame DNA-HPV"
        verbose_name_plural = "Exames DNA-HPV"
        ordering = ['-data_exame']


class CitopatologicoHistorico(models.Model):
    RESULTADO_CHOICES = [
        ('normal', 'Normal'),
        ('mudancas_reativas', 'Mudanças Reativas'),
        ('nic1', 'NIC I'),
        ('nic2', 'NIC II'),
        ('nic3', 'NIC III'),
        ('cancer', 'Câncer'),
        ('nao_conclusivo', 'Não Conclusivo'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citopatologicos')
    data_exame = models.DateField()
    resultado = models.CharField(max_length=50, choices=RESULTADO_CHOICES)
    observacoes = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Citopatológico {self.data_exame} - {self.paciente.nome}"
    
    class Meta:
        verbose_name_plural = "Citopatológicos"
        ordering = ['-data_exame']


class ProcedimentoRealizado(models.Model):
    TIPO_PROCEDIMENTO_CHOICES = [
        ('colposcopia', 'Colposcopia'),
        ('biopsia', 'Biópsia'),
        ('conizacao', 'Conização'),
        ('laser', 'Laser'),
        ('crioterapia', 'Crioterapia'),
        ('leep', 'LEEP'),
        ('outro', 'Outro'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='procedimentos')
    tipo_procedimento = models.CharField(max_length=50, choices=TIPO_PROCEDIMENTO_CHOICES)
    data_procedimento = models.DateField()
    resultado = models.TextField()
    complicacoes = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.tipo_procedimento} - {self.data_procedimento}"
    
    class Meta:
        ordering = ['-data_procedimento']


class StatusSeguimento(models.Model):
    RISCO_CHOICES = [
        ('baixo', 'Baixo Risco'),
        ('medio', 'Médio Risco'),
        ('alto', 'Alto Risco'),
    ]
    
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='status_seguimento')
    classificacao_risco = models.CharField(max_length=10, choices=RISCO_CHOICES, null=True, blank=True)
    
    # Detalhes da classificação NER (clínico + social)
    score_total = models.IntegerField(null=True, blank=True, help_text="Score total (clínico + vulnerabilidade)")
    justificativas = models.TextField(null=True, blank=True, help_text="Justificativas da classificação")
    
    # Entidades clínicas extraídas
    hpv_types = models.TextField(null=True, blank=True, help_text="Tipos de HPV detectados")
    lesions = models.TextField(null=True, blank=True, help_text="Lesões identificadas")
    exams = models.TextField(null=True, blank=True, help_text="Exames realizados")
    procedures = models.TextField(null=True, blank=True, help_text="Procedimentos realizados")
    viral_loads = models.TextField(null=True, blank=True, help_text="Informações de carga viral")
    
    # Fatores de vulnerabilidade social (NOVO)
    social_factors = models.TextField(null=True, blank=True, help_text="Fatores socioeconômicos identificados")
    geographic_factors = models.TextField(null=True, blank=True, help_text="Fatores geográficos de vulnerabilidade")
    behavioral_factors = models.TextField(null=True, blank=True, help_text="Fatores comportamentais de risco")
    follow_up_issues = models.TextField(null=True, blank=True, help_text="Problemas de seguimento identificados")
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Classificação de Risco - {self.paciente.nome}"
    
    class Meta:
        verbose_name_plural = "Classificação de Risco"
