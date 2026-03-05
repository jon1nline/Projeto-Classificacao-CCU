"""
Management command para testar as melhorias do NER v2.

Uso: python manage.py test_ner_improvements [--quick]
"""

from django.core.management.base import BaseCommand
from feedIA.ner import classify_patient_text, extract_entities, classify_risk_by_entities

try:
    from feedIA.ner_enhanced import (
        detect_negation, extract_age, detect_persistence
    )
    NER_ENHANCED = True
except ImportError:
    NER_ENHANCED = False


class Command(BaseCommand):
    help = "Testa as melhorias implementadas no NER (negação, idade, persistência, matriz de risco)"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Executa apenas testes rápidos',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Saída detalhada',
        )
    
    def handle(self, *args, **options):
        quick_mode = options.get('quick', False)
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('\n' + '🔬 '*20))
        self.stdout.write(self.style.SUCCESS('SUITE DE TESTES - MELHORIAS NER v2'))
        self.stdout.write(self.style.SUCCESS('🔬 '*20 + '\n'))
        
        if not NER_ENHANCED:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Módulo ner_enhanced não disponível. '
                    'Alguns testes serão pulados.'
                )
            )
        
        try:
            if not quick_mode:
                self.test_negation_handling()
                self.test_comparison_before_after()
            
            if NER_ENHANCED:
                self.test_age_detection()
                self.test_persistence_detection()
            
            self.test_risk_classification()
            self.test_real_document()
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('✅ TESTES CONCLUÍDOS COM SUCESSO!'))
            self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Erro durante testes: {e}\n')
            )
            import traceback
            traceback.print_exc()
    
    def test_negation_handling(self):
        """Testa tratamento de negação"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('TESTE 1: TRATAMENTO DE NEGAÇÃO'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        test_cases = [
            ("DNA-HPV negativo para HPV 16", "✅ BAIXO risco esperado"),
            ("HPV 16 detectado no exame", "❌ ALTO risco esperado"),
            ("Resultado negativo: ausência de HPV detectado", "✅ BAIXO risco esperado"),
        ]
        
        for text, expected in test_cases:
            self.stdout.write(f"\n📝 Texto: '{text}'")
            self.stdout.write(f"   Esperado: {expected}")
            
            try:
                result = classify_patient_text(text)
                COLOR = self.style.SUCCESS if result['risco'] == 'baixo' else self.style.WARNING
                self.stdout.write(COLOR(f"   ✓ Resultado: {result['risco'].upper()}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
    
    def test_age_detection(self):
        """Testa detecção de idade"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('TESTE 2: DETECÇÃO DE IDADE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        test_cases = [
            "Paciente de 18 anos com HPV 16",
            "Mulher de 45 anos com HPV 31",
        ]
        
        for text in test_cases:
            self.stdout.write(f"\n📝 Texto: '{text}'")
            try:
                age, age_type = extract_age(text)
                if age:
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✓ Idade: {age} anos (tipo: {age_type})")
                    )
                else:
                    self.stdout.write(self.style.WARNING("   ⚠️  Idade não detectada"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
    
    def test_persistence_detection(self):
        """Testa detecção de persistência"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('TESTE 3: DETECÇÃO DE PERSISTÊNCIA'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        test_cases = [
            ("HPV 16 persistente há 3 anos", True),
            ("DNA-HPV positivo em 2022... ainda positivo em 2024", True),
            ("HPV detectado em exame atual", False),
        ]
        
        for text, should_detect in test_cases:
            self.stdout.write(f"\n📝 Texto: '{text}'")
            try:
                entities = extract_entities(text)
                persistence = detect_persistence(text, entities)
                
                if persistence['has_persistence'] == should_detect:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   ✓ Persistência: {persistence['has_persistence']}"
                        )
                    )
                    if persistence['evidence']:
                        for evidence in persistence['evidence']:
                            self.stdout.write(f"      - {evidence}")
                else:
                    self.stdout.write(self.style.WARNING(
                        f"   ⚠️  Persistência: {persistence['has_persistence']} "
                        f"(esperado: {should_detect})"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
    
    def test_risk_classification(self):
        """Testa classificação de risco aprimorada"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('TESTE 4: CLASSIFICAÇÃO DE RISCO'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        test_cases = [
            ("HPV 16 com HSIL", "alto"),
            ("HPV detectado sem lesão", "medio"),
            ("DNA-HPV negativo", "baixo"),
        ]
        
        for text, expected_risk in test_cases:
            self.stdout.write(f"\n📝 Texto: '{text}'")
            try:
                result = classify_patient_text(text)
                
                if result['risco'] == expected_risk:
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✓ Risco: {result['risco'].upper()}")
                    )
                else:
                    self.stdout.write(self.style.WARNING(
                        f"   ⚠️  Risco: {result['risco'].upper()} "
                        f"(esperado: {expected_risk.upper()})"
                    ))
                
                self.stdout.write(f"   Score: {result['score']}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
    
    def test_comparison_before_after(self):
        """Compara com/sem negação"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('TESTE 5: COMPARAÇÃO COM/SEM NEGAÇÃO'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        text_pos = "DNA-HPV positivo para HPV 16, HSIL"
        text_neg = "DNA-HPV NEGATIVO, sem HPV 16, sem HSIL"
        
        self.stdout.write(f"\n📝 Positivo: '{text_pos}'")
        try:
            result_pos = classify_patient_text(text_pos)
            self.stdout.write(f"   ✓ Resultado: {result_pos['risco'].upper()}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
        
        self.stdout.write(f"\n📝 Negativo: '{text_neg}'")
        try:
            result_neg = classify_patient_text(text_neg)
            self.stdout.write(f"   ✓ Resultado: {result_neg['risco'].upper()}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
    
    def test_real_document(self):
        """Testa com documento médico realista"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('TESTE 6: DOCUMENTO MÉDICO REALISTA'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        documento = """
        LAUDO CITOPAT:
        Paciente: Maria Silva, 35 anos
        Local: Salvador - Bahia
        
        Resultado: DNA-HPV POSITIVO para HPV 16 (alto risco)
        Carga viral: ALTA
        Citopatológico: HSIL
        
        Histórico: Exame anterior positivo em 2021, persistência.
        Nota: Vulnerabilidade social identificada.
        """
        
        self.stdout.write("\n📋 Analisando documento médico realista...")
        try:
            result = classify_patient_text(documento)
            
            COLOR = {
                'alto': self.style.ERROR,
                'medio': self.style.WARNING,
                'baixo': self.style.SUCCESS
            }.get(result['risco'], self.style.WARNING)
            
            self.stdout.write(COLOR(f"\n✓ Classificação: RISCO {result['risco'].upper()}"))
            self.stdout.write(f"  Score: {result['score']}")
            
            self.stdout.write("\n  Entidades encontradas:")
            for key, values in result['entidades'].items():
                if values and key != 'all_entities':
                    self.stdout.write(f"    {key}: {', '.join(str(v) for v in values[:3])}")
            
            self.stdout.write("\n  Primeiras justificativas:")
            for j in result['justificativas'][:5]:
                if j.strip():
                    self.stdout.write(f"    {j}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
            import traceback
            traceback.print_exc()
