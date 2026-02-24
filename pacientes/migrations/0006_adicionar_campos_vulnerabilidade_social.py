# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0005_alter_paciente_cor'),
    ]

    operations = [
        # Adicionar campos de vulnerabilidade social ao Paciente
        migrations.AddField(
            model_name='paciente',
            name='area_rural',
            field=models.BooleanField(default=False, verbose_name='Reside em área rural/difícil acesso'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='perda_seguimento',
            field=models.BooleanField(default=False, verbose_name='Histórico de perda de seguimento'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='primeira_vez_rastreamento',
            field=models.BooleanField(default=False, verbose_name='Primeira vez no rastreamento'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='observacoes_vulnerabilidade',
            field=models.TextField(blank=True, help_text='Observações sobre vulnerabilidade social, dificuldades de acesso, etc.', null=True),
        ),
        # Adicionar campos detalhados ao StatusSeguimento
        migrations.AddField(
            model_name='statusseguimento',
            name='score_total',
            field=models.IntegerField(blank=True, help_text='Score total (clínico + vulnerabilidade)', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='justificativas',
            field=models.TextField(blank=True, help_text='Justificativas da classificação', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='hpv_types',
            field=models.TextField(blank=True, help_text='Tipos de HPV detectados', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='lesions',
            field=models.TextField(blank=True, help_text='Lesões identificadas', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='exams',
            field=models.TextField(blank=True, help_text='Exames realizados', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='procedures',
            field=models.TextField(blank=True, help_text='Procedimentos realizados', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='viral_loads',
            field=models.TextField(blank=True, help_text='Informações de carga viral', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='social_factors',
            field=models.TextField(blank=True, help_text='Fatores socioeconômicos identificados', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='geographic_factors',
            field=models.TextField(blank=True, help_text='Fatores geográficos de vulnerabilidade', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='behavioral_factors',
            field=models.TextField(blank=True, help_text='Fatores comportamentais de risco', null=True),
        ),
        migrations.AddField(
            model_name='statusseguimento',
            name='follow_up_issues',
            field=models.TextField(blank=True, help_text='Problemas de seguimento identificados', null=True),
        ),
    ]
