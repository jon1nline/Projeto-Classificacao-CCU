"""
Data Augmentation - Exemplos aprimorados de treinamento para o modelo NER.

Inclui:
1. Exemplos com negação
2. Exemplos com persistência temporal
3. Exemplos com entidades aninhadas
4. Exemplos com ruído real de documentos médicos
5. Exemplos regionalizados (Bahia, Salvador)
"""

TRAINING_DATA_AUGMENTED = [
    # ====== EXEMPLOS COM NEGAÇÃO ======
    ("DNA-HPV negativo para HPV 16 de alto risco", {
        "entities": [(0, 7, "EXAM"), (31, 41, "HPV_TYPE")]
    }),
    ("Teste de DNA-HPV negativo, sem detecção de HPV oncogênico", {
        "entities": [(8, 15, "EXAM"), (45, 60, "HPV_TYPE")]
    }),
    ("Resultado negativo: ausência de HPV detectado", {
        "entities": [(18, 29, "HPV_TYPE")]
    }),
    ("Não há evidência de HPV 16 ou HPV 18 no exame", {
        "entities": [(25, 31, "HPV_TYPE"), (35, 41, "HPV_TYPE"), (54, 58, "EXAM")]
    }),
    ("HSIL negativa, sem achados de lesão pré-maligna", {
        "entities": [(0, 4, "LESION")]
    }),
    ("Carga viral indetectável, sem sinais de HPV", {
        "entities": [(0, 5, "VIRAL_LOAD")]
    }),
    
    # ====== EXEMPLOS COM PERSISTÊNCIA TEMPORAL ======
    ("Paciente com HPV 16 persistente há 3 anos, múltiplos testes positivos", {
        "entities": [(13, 19, "HPV_TYPE"), (46, 50, "EXAM")]
    }),
    ("DNA-HPV positivo em janeiro 2022, positivo novamente em março 2024 - persistência confirmada", {
        "entities": [(0, 7, "EXAM"), (40, 47, "EXAM")]
    }),
    ("HPV 31 detectado em 2021 ainda presente em 2024, infecção persistente", {
        "entities": [(0, 6, "HPV_TYPE")]
    }),
    ("Histórico de HPV positivo há mais de 2 anos com exame atual positivo", {
        "entities": [(11, 14, "HPV_TYPE")]
    }),
    ("Lesão recorrente NIC 2 após conização em 2022, re-epitealização com HPV 18 persistente", {
        "entities": [(20, 25, "LESION"), (34, 44, "PROCEDURE"), (68, 74, "HPV_TYPE")]
    }),
    
    # ====== EXEMPLOS COM ENTIDADES ANINHADAS ======
    ("HPV 16 (alto risco) com HSIL confirmado em biópsia", {
        "entities": [(0, 6, "HPV_TYPE"), (9, 19, "HPV_TYPE"), (25, 29, "LESION"), (45, 51, "EXAM")]
    }),
    ("DNA-HPV detectou HPV 18 (tipo oncogênico) compatível com lesão de alto grau HSIL", {
        "entities": [(0, 7, "EXAM"), (17, 23, "HPV_TYPE"), (29, 43, "HPV_TYPE"), (66, 70, "LESION")]
    }),
    ("Paciente com idade 35 anos, HPV 52 (alto risco) e LSIL - encaminhada para colposcopia", {
        "entities": [(15, 22, "BEHAVIORAL"), (24, 30, "HPV_TYPE"), (35, 45, "HPV_TYPE"), (50, 54, "LESION"), (75, 86, "EXAM")]
    }),
    
    # ====== EXEMPLOS REGIONALIZADOS (BAHIA/SALVADOR) ======
    ("Mulher moradora de Tororó, bairro de Salvador, com HPV 16 e vulnerabilidade social", {
        "entities": [(19, 25, "GEOGRAPHIC"), (50, 56, "HPV_TYPE"), (63, 85, "SOCIAL_FACTOR")]
    }),
    ("Paciente da Região Norte, escolaridade baixa, apresenta HPV 18 com HSIL", {
        "entities": [(15, 29, "GEOGRAPHIC"), (31, 49, "SOCIAL_FACTOR"), (61, 67, "HPV_TYPE"), (73, 77, "LESION")]
    }),
    ("Área de difícil acesso no Nordeste, seguimento comprometido, HPV persistente desde 2022", {
        "entities": [(0, 20, "GEOGRAPHIC"), (24, 34, "GEOGRAPHIC"), (51, 53, "FOLLOW_UP"), (63, 66, "HPV_TYPE")]
    }),
    ("Residente em zona rural do Nordeste, baixa escolaridade, HSIL + HPV 31", {
        "entities": [(13, 22, "GEOGRAPHIC"), (25, 37, "GEOGRAPHIC"), (40, 58, "SOCIAL_FACTOR"), (61, 65, "LESION"), (68, 74, "HPV_TYPE")]
    }),
    
    # ====== EXEMPLOS COM RUÍDO REAL (DOCUMENTOS VARIADOS) ======
    ("Resultado de DNA-HPV: positivo para HPV 16. Carga viral: alta. Colposcopia indicada.",
     {"entities": [(12, 19, "EXAM"), (38, 44, "HPV_TYPE"), (47, 58, "VIRAL_LOAD"), (62, 73, "EXAM")]}),
    
    ("Paciente: Não comparecimento às convocações x 2. Último exame DNA-HPV em jan/2023 positivo para HPV de alto risco.",
     {"entities": [(11, 28, "FOLLOW_UP"), (56, 63, "EXAM"), (80, 99, "HPV_TYPE")]}),
    
    ("LAUDO CITOPAT: CERVICITE. Sem achados de SIL. DNA-HPV não realizado.",
     {"entities": [(5, 15, "EXAM"), (37, 44, "LESION"), (47, 54, "EXAM")]}),
    
    ("PAC: 35a, múltiplos parceiros, HPV 45 persistente, NIC 1 em última biópsia, conv. para CAF",
     {"entities": [(4, 8, "BEHAVIORAL"), (10, 29, "BEHAVIORAL"), (31, 37, "HPV_TYPE"), (50, 55, "LESION"), (67, 70, "PROCEDURE")]}),
    
    # ====== EXEMPLOS COM DENSIDADE VARIÁVEL DE ENTIDADES ======
    ("Exame simples positivo", {
        "entities": [(0, 5, "EXAM")]
    }),
    
    ("Colposcopia com múltiplas biópsias revelou NIC 2 e carga viral elevada de HPV 16 oncogênico",
     {"entities": [(0, 11, "EXAM"), (43, 48, "LESION"), (53, 70, "VIRAL_LOAD"), (74, 80, "HPV_TYPE")]}),
    
    # ====== EXEMPLOS COM IDADE E FATORES COMPORTAMENTAIS ======
    ("Candidata à vacinação HPV, 14 anos, virgem, sem atividade sexual",
     {"entities": [(15, 18, "HPV_TYPE"), (20, 22, "BEHAVIORAL")]}),
    
    ("Mulher de 45 anos com HPV 16, 15 parceiros sexuais, perda de seguimento há 5 anos",
     {"entities": [(10, 12, "BEHAVIORAL"), (17, 23, "HPV_TYPE"), (26, 48, "BEHAVIORAL"), (51, 70, "FOLLOW_UP")]}),
    
    # ====== EXEMPLOS COM COMBINAÇÕES CRÍTICAS ======
    ("HPV 16 + HPV 18 + HSIL + Paciente residente em região rural do Nordeste com baixa escolaridade",
     {"entities": [(0, 6, "HPV_TYPE"), (9, 15, "HPV_TYPE"), (18, 22, "LESION"), (47, 56, "GEOGRAPHIC"), (60, 72, "GEOGRAPHIC"), (76, 94, "SOCIAL_FACTOR")]}),
    
    ("Capacidade de seguimento comprometida: endereço não atualizado, sem telefone, HPV 31 persistente documentado desde 2020",
     {"entities": [(0, 30, "FOLLOW_UP"), (32, 64, "FOLLOW_UP"), (67, 73, "HPV_TYPE")]}),
    
    # ====== EXEMPLOS DE PROCEDIMENTOS E LESÕES COMBINADAS ======
    ("CAF realizada para excisão de tecido com HSIL, anatomopatológico confirma NIC 3",
     {"entities": [(0, 3, "PROCEDURE"), (35, 39, "LESION"), (65, 70, "LESION")]}),
    
    ("Conização por HSIL há 18 meses, HPV persistente à retest, re-epitealização incompleta",
     {"entities": [(0, 8, "PROCEDURE"), (12, 16, "LESION"), (28, 31, "HPV_TYPE"), (44, 49, "EXAM")]}),
    
    # ====== EXEMPLOS COM NEGAÇÃO COMPLEXA ======
    ("HPV não detectado em teste de DNA-HPV repetido 3 vezes",
     {"entities": [(4, 7, "HPV_TYPE"), (21, 28, "EXAM")]}),
    
    ("Ausência de lesão pré-maligna em colposcopia com biópsias negativas",
     {"entities": [(10, 25, "LESION"), (29, 40, "EXAM")]}),
    
    ("Sem evidências de HPV de alto risco, sem HSIL, sem necessidade de intervenção",
     {"entities": [(24, 39, "HPV_TYPE"), (46, 50, "LESION")]}),
]

# Dicionário de variações de termos para aumentar dados de treinamento
ENTITY_VARIATIONS = {
    "HPV_TYPE": {
        "alto_risco": [
            "HPV 16", "HPV-16", "HPV16", "tipo 16",
            "HPV 18", "HPV-18", "HPV18", "tipo 18",
            "HPV 31", "HPV 33", "HPV 45", "HPV 52", "HPV 58",
            "HPV de alto risco", "HPV alto risco", "HPV oncogênico",
            "tipos oncogênicos"
        ],
        "baixo_risco": [
            "HPV 6", "HPV 11", "HPV 42",
            "HPV de baixo risco", "HPV baixo risco", "HPV não oncogênico",
        ]
    },
    "LESION": {
        "alto_grau": [
            "HSIL", "high-grade", "NIC 2", "NIC2", "NIC 3", "NIC3",
            "neoplasia cervical", "displasia alta", "lesão de alto grau"
        ],
        "baixo_grau": [
            "LSIL", "low-grade", "NIC 1", "NIC1",
            "displasia leve", "lesão de baixo grau"
        ]
    },
    "SOCIAL_FACTOR": [
        "escolaridade baixa", "analfabetismo", "vulnerabilidade social",
        "renda insuficiente", "pobreza", "carência",
        "dificuldade de acesso", "migrante", "refugiada"
    ],
    "GEOGRAPHIC": [
        "Região Norte", "Nordeste", "zona rural", "periferia",
        "favela", "comunidade", "área de difícil acesso", "remota",
        "Salvador", "Tororó", "Bahia"
    ]
}


def generate_augmented_data(base_examples: list, augmentation_factor: int = 2) -> list:
    """
    Gera dados aumentados através de paráfrases e variações de termos.
    
    Args:
        base_examples: Lista de exemplos originais
        augmentation_factor: Multiplicador de aumento (2 = dobra o dataset)
    
    Returns:
        Lista expandida de exemplos
    """
    augmented = []
    
    import random
    
    for text, annotations in base_examples:
        augmented.append((text, annotations))  # Mantém original
        
        # Variação 1: Paráfrase simples se é exemplo de negação
        if "negativo" in text.lower() or "não" in text.lower():
            paraphrased = text.replace("negativo", "negativa").replace("não há", "ausência de")
            augmented.append((paraphrased, annotations))
    
    return augmented


__all__ = ['TRAINING_DATA_AUGMENTED', 'ENTITY_VARIATIONS', 'generate_augmented_data']
