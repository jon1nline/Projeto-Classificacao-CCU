"""
Script de testes para validar as melhorias implementadas no NER.

Testa:
1. Tratamento de negação
2. Detector de idade
3. Detector de persistência
4. Matriz de risco aprimorada
5. Classificação com dados reais
"""

import sys
import os

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ccu.settings')

import django
django.setup()

from feedIA.ner import (
    classify_patient_text, extract_entities, classify_risk_by_entities
)
from feedIA.ner_enhanced import (
    detect_negation, extract_age, detect_persistence
)


def test_negation_handling():
    """Testa o tratamento de negação"""
    print("\n" + "="*60)
    print("TESTE 1: TRATAMENTO DE NEGAÇÃO")
    print("="*60)
    
    test_cases = [
        ("DNA-HPV negativo para HPV 16", "Deve indicar BAIXO risco"),
        ("HPV 16 detectado no exame", "Deve indicar ALTO risco"),
        ("Resultado negativo: ausência de HPV detectado", "Deve indicar BAIXO risco"),
        ("Não há evidência de lesão grave HSIL", "Deve indicar BAIXO risco"),
    ]
    
    for text, expected in test_cases:
        print(f"\nTexto: '{text}'")
        print(f"Esperado: {expected}")
        
        result = classify_patient_text(text)
        print(f"Resultado: Risco = {result['risco'].upper()}")
        print(f"Score: {result['score']}")
        for just in result['justificativas'][:3]:
            print(f"  - {just}")


def test_age_detection():
    """Testa o detector de idade"""
    print("\n" + "="*60)
    print("TESTE 2: DETECÇÃO DE IDADE")
    print("="*60)
    
    test_cases = [
        "Paciente de 18 anos com HPV 16",
        "Mulher de 45 anos com HPV 31",
        "Idade: 65 anos. HPV positivo",
    ]
    
    for text in test_cases:
        print(f"\nTexto: '{text}'")
        try:
            age, age_type = extract_age(text)
            if age:
                print(f"✅ Idade detectada: {age} anos (tipo: {age_type})")
                print(f"   Risco elevado (>30 anos)? {age > 30}")
            else:
                print("❌ Idade não detectada")
        except Exception as e:
            print(f"❌ Erro: {e}")


def test_persistence_detection():
    """Testa a detecção de persistência"""
    print("\n" + "="*60)
    print("TESTE 3: DETECÇÃO DE PERSISTÊNCIA")
    print("="*60)
    
    test_cases = [
        "HPV 16 persistente há 3 anos",
        "DNA-HPV positivo em janeiro 2022, ainda positivo em 2024",
        "HPV detectado em exame atual",
    ]
    
    for text in test_cases:
        print(f"\nTexto: '{text}'")
        try:
            entities = extract_entities(text)
            persistence = detect_persistence(text, entities)
            print(f"Persistência detectada? {persistence['has_persistence']}")
            if persistence['evidence']:
                for evidence in persistence['evidence']:
                    print(f"  - {evidence}")
            print(f"Elevação de risco: +{persistence['risk_elevation']}")
        except Exception as e:
            print(f"❌ Erro: {e}")


def test_risk_matrix():
    """Testa a matriz de risco aprimorada"""
    print("\n" + "="*60)
    print("TESTE 4: MATRIZ DE RISCO APRIMORADA")
    print("="*60)
    
    test_cases = [
        ("HPV 16 com HSIL em residente do Nordeste com escolaridade baixa", 
         "Deve indicar RISCO VERMELHO"),
        ("HPV 31 detectado, paciente jovem, sem lesão", 
         "Deve indicar RISCO VERDE/MÉDIO"),
        ("HPV 18 com carga viral alta + vulnerabilidade social", 
         "Deve indicar RISCO AMARELO/ALTO"),
    ]
    
    for text, expected in test_cases:
        print(f"\nTexto: '{text}'")
        print(f"Esperado: {expected}")
        
        try:
            result = classify_patient_text(text)
            print(f"\n✅ Classificação: RISCO {result['risco'].upper()}")
            print(f"   Score total: {result['score']}")
            print(f"   Entidades encontradas:")
            for key, values in result['entidades'].items():
                if values and 'all_entities' not in key:
                    print(f"      {key}: {values}")
            print(f"   Justificativas principais:")
            for just in result['justificativas'][:5]:
                print(f"      {just}")
        except Exception as e:
            print(f"❌ Erro na classifi cação: {e}")
            import traceback
            traceback.print_exc()


def test_comparison_before_after():
    """Compara classificações antes e depois de tratamento de negação"""
    print("\n" + "="*60)
    print("TESTE 5: COMPARAÇÃO COM/SEM NEGAÇÃO")
    print("="*60)
    
    text_positivo = "DNA-HPV positivo para HPV 16, HSIL, carga viral alta"
    text_negativo = "DNA-HPV NEGATIVO, sem HPV 16 detectado, ausência de HSIL"
    
    print(f"\nContexto POSITIVO: '{text_positivo}'")
    result_pos = classify_patient_text(text_positivo)
    print(f"Resultado: {result_pos['risco'].upper()} (score: {result_pos['score']})")
    
    print(f"\nContexto NEGATIVO: '{text_negativo}'")
    result_neg = classify_patient_text(text_negativo)
    print(f"Resultado: {result_neg['risco'].upper()} (score: {result_neg['score']})")
    
    print(f"\n✅ Diferença de classificação: {result_pos['risco']} vs {result_neg['risco']}")


def test_real_document():
    """Testa com documento médico realista"""
    print("\n" + "="*60)
    print("TESTE 6: DOCUMENTO MÉDICO REALISTA")
    print("="*60)
    
    documento = """
    LAUDO CITOPAT:
    Paciente: Maria Silva, 32 anos
    Local: Tororó, Salvador - Bahia
    Escolaridade: Ensino fundamental incompleto
    
    Resultado: DNA-HPV POSITIVO para HPV 16 e HPV 18 (alto risco)
    Carga viral: ALTA (5 log cópias)
    Citopatológico: HSIL compatível
    
    Histórico: Exame anterior positivo em 2022, persistência confirmada.
    Nota clínica: Paciente em situação de vulnerabilidade social.
    Recomendação: Colposcopia urgente com CAF se confirmado.
    """
    
    print(f"Analisando documento médico...")
    try:
        result = classify_patient_text(documento)
        
        print(f"\n📋 RESULTADO DA ANÁLISE:")
        print(f"   Classificação: RISCO {result['risco'].upper()}")
        print(f"   Score total: {result['score']}")
        
        print(f"\n🔍 Entidades identificadas:")
        entidades = result['entidades']
        for key in ['hpv_types', 'lesions', 'exams', 'viral_loads', 'social_factors', 'geographic', 'behavioral']:
            if entidades.get(key):
                print(f"   {key}: {entidades[key]}")
        
        print(f"\n📊 Justificativas detalhadas:")
        for i, just in enumerate(result['justificativas'], 1):
            if just.strip():
                print(f"   {just}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Executa todos os testes"""
    print("\n" + "🔬 "*20)
    print("SUITE DE TESTES - MELHORIAS NER v2")
    print("🔬 "*20)
    
    try:
        test_negation_handling()
        test_age_detection()
        test_persistence_detection()
        test_risk_matrix()
        test_comparison_before_after()
        test_real_document()
        
        print("\n" + "="*60)
        print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Erro geral nos testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
