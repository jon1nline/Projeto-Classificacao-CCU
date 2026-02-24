"""
Comando para reclassificar todos os pacientes existentes usando o sistema NER atualizado.
Este comando reconstrói a classificação de risco de todos os pacientes baseado nas 9 entidades
(clínicas + vulnerabilidade social).

Uso: python manage.py reclassificar_pacientes
"""

from django.core.management.base import BaseCommand
from pacientes.models import Paciente, StatusSeguimento
from pacientes.utils import build_patient_text
from feedIA.ner import classify_patient_text


class Command(BaseCommand):
    help = 'Reclassifica todos os pacientes usando o sistema NER atualizado (clínico + vulnerabilidade social)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--paciente-id',
            type=int,
            help='Reclassificar apenas um paciente específico pelo ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular classificação sem salvar no banco de dados',
        )

    def handle(self, *args, **options):
        paciente_id = options.get('paciente_id')
        dry_run = options.get('dry_run')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DRY-RUN: Nenhuma alteração será salva no banco de dados'))
        
        # Selecionar pacientes
        if paciente_id:
            pacientes = Paciente.objects.filter(id=paciente_id)
            if not pacientes.exists():
                self.stdout.write(self.style.ERROR(f'❌ Paciente com ID {paciente_id} não encontrado'))
                return
        else:
            pacientes = Paciente.objects.all()
        
        total = pacientes.count()
        self.stdout.write(self.style.SUCCESS(f'\n🏥 Iniciando reclassificação de {total} paciente(s)...\n'))
        
        classificados = 0
        erros = 0
        
        for i, paciente in enumerate(pacientes, 1):
            try:
                self.stdout.write(f'[{i}/{total}] Processando: {paciente.nome} (ID: {paciente.id})')
                
                # Construir texto do paciente
                texto = build_patient_text(paciente)
                if not texto:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  Sem dados para classificar'))
                    continue
                
                # Classificar usando NER (9 entidades)
                resultado = classify_patient_text(texto)
                
                risco = resultado['risco']
                score = resultado['score']
                justificativas = resultado['justificativas']
                entidades = resultado['entidades']
                
                # Mostrar resultado
                emoji_risco = {'alto': '🔴', 'medio': '🟡', 'baixo': '🟢'}
                self.stdout.write(f'  {emoji_risco.get(risco, "⚪")} Risco: {risco.upper()} (Score: {score})')
                
                # Mostrar entidades clínicas
                if entidades.get('hpv_types') or entidades.get('lesions') or entidades.get('procedures'):
                    self.stdout.write(f'  🧠 Clínico: ', ending='')
                    clinico_parts = []
                    if entidades.get('hpv_types'):
                        clinico_parts.append(f"HPV: {', '.join(entidades['hpv_types'][:2])}")
                    if entidades.get('lesions'):
                        clinico_parts.append(f"Lesões: {', '.join(entidades['lesions'][:2])}")
                    if entidades.get('procedures'):
                        clinico_parts.append(f"Proc: {', '.join(entidades['procedures'][:1])}")
                    self.stdout.write(', '.join(clinico_parts))
                
                # Mostrar entidades de vulnerabilidade
                vulnerabilidade_parts = []
                if entidades.get('social_factors'):
                    vulnerabilidade_parts.append(f"📚 Social: {', '.join(entidades['social_factors'][:2])}")
                if entidades.get('geographic'):
                    vulnerabilidade_parts.append(f"📍 Geo: {', '.join(entidades['geographic'][:2])}")
                if entidades.get('behavioral'):
                    vulnerabilidade_parts.append(f"👥 Comp: {', '.join(entidades['behavioral'][:1])}")
                if entidades.get('follow_up'):
                    vulnerabilidade_parts.append(f"⏰ Seguimento: {', '.join(entidades['follow_up'][:1])}")
                
                if vulnerabilidade_parts:
                    for part in vulnerabilidade_parts:
                        self.stdout.write(f'  {part}')
                
                # Salvar no banco (se não for dry-run)
                if not dry_run:
                    justificativas_texto = '\n'.join(justificativas) if justificativas else 'Sem fatores de risco identificados'
                    
                    StatusSeguimento.objects.update_or_create(
                        paciente=paciente,
                        defaults={
                            'classificacao_risco': risco,
                            'score_total': score,
                            'justificativas': justificativas_texto,
                            # Entidades clínicas
                            'hpv_types': ', '.join(entidades.get('hpv_types', [])),
                            'lesions': ', '.join(entidades.get('lesions', [])),
                            'exams': ', '.join(entidades.get('exams', [])),
                            'procedures': ', '.join(entidades.get('procedures', [])),
                            'viral_loads': ', '.join(entidades.get('viral_loads', [])),
                            # Entidades de vulnerabilidade social
                            'social_factors': ', '.join(entidades.get('social_factors', [])),
                            'geographic_factors': ', '.join(entidades.get('geographic', [])),
                            'behavioral_factors': ', '.join(entidades.get('behavioral', [])),
                            'follow_up_issues': ', '.join(entidades.get('follow_up', [])),
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Salvo no banco de dados\n'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ⏭️  Pulado (dry-run)\n'))
                
                classificados += 1
                
            except Exception as e:
                erros += 1
                self.stdout.write(self.style.ERROR(f'  ❌ Erro: {str(e)}\n'))
        
        # Resumo final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ Concluído!'))
        self.stdout.write(f'  Total processado: {total}')
        self.stdout.write(f'  Classificados: {classificados}')
        if erros > 0:
            self.stdout.write(self.style.ERROR(f'  Erros: {erros}'))
        self.stdout.write('='*60 + '\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  ATENÇÃO: Este foi um DRY-RUN. Execute sem --dry-run para salvar as alterações.'))
