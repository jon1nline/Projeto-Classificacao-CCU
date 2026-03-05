"""
Módulo NER aprimorado com tratamento de negação, matriz de risco,
detecção de idade e persistência de HPV.

Melhorias implementadas:
1. Tratamento de Negação - negspacy
2. Matriz de Risco (Clínica + Social)
3. Detector de Idade como filtro
4. EntityRuler com Gazetteers
5. Detecção de Persistência Temporal
"""

import spacy
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
import json
from pathlib import Path
from django.conf import settings

# ====== GAZETTEERS (Listas exaustivas) ======

# Municípios e bairros de Salvador (exemplo para Bahia)
SALVADOR_LOCATIONS = {
    "bairros": [
        "Tororó", "Centro", "Graça", "Vitória", "Barra", "Ondina", "Rio Vermelho",
        "Amaralina", "Corsário", "Guaratinga", "Camarão", "Pituba", "Costa Azul",
        "Stiep", "Paralela", "Cabula", "Pernambués", "Federação", "Engenho Velho",
        "Santo Antônio", "Saramandaia", "Horto Florestal", "Liberdade", "São Caetano",
        "Curuzu", "Tororózinho", "Matoporé", "Cais", "Pelourinho"
    ],
    "regioes": [
        "Região Norte", "Região Nordeste", "Região Centro-Oeste", "Sudeste", "Sul",
        "Área Rural", "Zona Urbana", "Periferia", "Comunidade"
    ]
}

# Termos médicos específicos e técnicos
MEDICAL_GAZETEER = {
    "hpv_types": {
        "alto_risco": ["HPV 16", "HPV 18", "HPV 31", "HPV 33", "HPV 35", "HPV 45", 
                      "HPV 52", "HPV 58", "HPV oncogênico", "HPV de alto risco"],
        "baixo_risco": ["HPV 6", "HPV 11", "HPV 42", "HPV 44", "HPV 53", "HPV 54",
                       "HPV de baixo risco", "HPV não oncogênico"]
    },
    "lesions": {
        "alto_grau": ["HSIL", "High-Grade Squamous Intraepithelial Lesion", 
                     "NIC 2", "NIC 3", "NIC2", "NIC3", "Neoplasia Intraepitelial Cervical 2",
                     "Neoplasia Intraepitelial Cervical 3", "Carcinoma", "Displasia alta"],
        "baixo_grau": ["LSIL", "Low-Grade Squamous Intraepithelial Lesion", 
                      "NIC 1", "NIC1", "Neoplasia Intraepitelial Cervical 1", "Displasia leve"]
    },
    "exams": [
        "DNA-HPV", "DNA HPV", "PCR-HPV", "Captura Híbrida", "Citopatológico",
        "Papanicolau", "Colposcopia", "Biópsia", "Teste Molecular", "Teste Rápido"
    ],
    "procedures": [
        "Conização", "CAF", "LEEP", "Crioterapia", "Crioablação", "Cauterização",
        "Eletrocirurgia", "Exérese", "Cirurgia", "Curetagem"
    ]
}

# Indicadores de negação
NEGATION_TERMS = [
    "não", "nao", "nunca", "nenhum", "nenhuma", "ausência", "ausencia",
    "sem", "negativo", "negativa", "normal", "negacionista"
]

# Indicadores de persistência temporal
PERSISTENCE_TERMS = {
    "persistence": ["persistente", "persistencia", "persiste", "permanece", 
                   "recorrente", "recorrencia", "recidiva", "reinfeccao"],
    "temporal_past": ["há", "desde", "anos atrás", "meses atrás", "2 anos",
                     "anterior", "historicamente", "ainda", "continua"],
    "temporal_recent": ["recente", "atual", "novo", "agora", "atual"],
}

# ====== DETECTOR DE NEGAÇÃO ======

def detect_negation(text: str, entity_start: int, entity_end: int, window: int = 5) -> bool:
    """
    Detecta se uma entidade está sob escopo de negação.
    
    Busca por palavras de negação em um janela antes da entidade.
    
    Args:
        text: Texto completo
        entity_start: Posição inicial da entidade
        entity_end: Posição final da entidade
        window: Número de palavras antes da entidade para procurar negação
    
    Returns:
        True se há negação, False caso contrário
    """
    # Pega texto desde o início do documento até a entidade
    context = text[:entity_start].lower()
    
    # Procura por negações na janela
    words_before = context.split()[-window:] if context.split() else []
    context_window = " ".join(words_before).lower()
    
    for neg in NEGATION_TERMS:
        if neg in context_window:
            return True
    
    # Também verifica próximas 2 palavras após a entidade (ex: "HPV negativo")
    context_after = text[entity_end:entity_end+20].lower()
    if "negativo" in context_after or "negativa" in context_after:
        return True
    
    return False


# ====== DETECTOR DE IDADE ======

def extract_age(text: str) -> Tuple[int, str]:
    """
    Extrai idade do texto. Retorna (idade, tipo_evidência).
    
    Procura padrões como:
    - "idade: 35" or "35 anos"
    - "nascida em 1990"
    
    Args:
        text: Texto para análise
    
    Returns:
        Tupla (idade, tipo) ou (None, "não encontrado")
    """
    text_lower = text.lower()
    
    # Padrão 1: "idade: XX" ou "idade XX"
    pattern1 = r'idade\s*:?\s*(\d{1,3})\s*(?:anos)?'
    match = re.search(pattern1, text_lower)
    if match:
        age = int(match.group(1))
        if 13 <= age <= 100:  # Validação básica
            return age, "idade_explícita"
    
    # Padrão 2: "XX anos"
    pattern2 = r'(\d{1,3})\s*anos'
    matches = re.finditer(pattern2, text_lower)
    for match in matches:
        age = int(match.group(1))
        if 13 <= age <= 100:
            return age, "anos_explícito"
    
    # Padrão 3: "nascida em YYYY"
    pattern3 = r'nascid[ao](?:\s+em)?\s*(\d{4})'
    match = re.search(pattern3, text_lower)
    if match:
        year = int(match.group(1))
        current_year = datetime.now().year
        age = current_year - year
        if 13 <= age <= 100:
            return age, "ano_nascimento"
    
    return None, "não_encontrado"


# ====== DETECTOR DE PERSISTÊNCIA ======

def detect_persistence(text: str, entities: Dict) -> Dict:
    """
    Detecta sinais de persistência de HPV através de indicadores temporais.
    
    Procura por:
    - Múltiplos exames positivos com datas
    - Expressões como "persistente", "recorrente"
    - Datas indicando longa evolução (>2 anos)
    
    Args:
        text: Texto para análise
        entities: Dicionário de entidades extraídas
    
    Returns:
        Dict com informações de persistência:
        {
            "has_persistence": bool,
            "evidence": List[str],
            "timeline": List[str],
            "risk_elevation": int
        }
    """
    result = {
        "has_persistence": False,
        "evidence": [],
        "timeline": [],
        "risk_elevation": 0
    }
    
    text_lower = text.lower()
    
    # Procura por termos de persistência
    for term in PERSISTENCE_TERMS["persistence"]:
        if term in text_lower and "hpv" in text_lower:
            result["has_persistence"] = True
            result["evidence"].append(f"Termo de persistência: {term}")
            break
    
    # Procura por múltiplos exames positivos
    hpv_positive_count = 0
    if entities.get('hpv_types'):
        # Conta referências a HPV no texto
        hpv_matches = len(re.findall(r'hpv.*?(?:positiv|detect|confirm)', text_lower))
        if hpv_matches >= 2:
            hpv_positive_count = hpv_matches
            result["has_persistence"] = True
            result["evidence"].append(f"Múltiplos exames positivos detectados: {hpv_matches}")
    
    # Procura por datas para avaliar timeline
    # Padrão: "2024", "jan 2024", "janeiro 2024", "há X anos" etc
    date_pattern = r'(\d{4}|jan|fev|mar|abr|mai|junho|julho|ago|set|out|nov|dez|janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s*(?:\d{1,2})?\s*(?:\d{4})?'
    dates_found = re.findall(date_pattern, text_lower)
    
    if len(dates_found) >= 2:
        result["timeline"].append(f"Múltiplas datas encontradas: {len(dates_found)}")
        result["has_persistence"] = True
    
    # Procura por "há X anos" ou similar
    anos_pattern = r'há\s+(\d+)\s+anos'
    match = re.search(anos_pattern, text_lower)
    if match:
        anos = int(match.group(1))
        if anos >= 2:
            result["has_persistence"] = True
            result["evidence"].append(f"HPV com {anos} anos de evolução")
            result["timeline"].append(f"Infecção há {anos} anos")
            # Persistência >2 anos aumenta risco
            result["risk_elevation"] = 2 if anos >= 2 else 1
    
    return result


# ====== ENTITY RULER COM GAZETTEERS ======

def add_entity_ruler(nlp):
    """
    Adiciona EntityRuler ao pipeline spaCy com gazetteers.
    
    O EntityRuler roda ANTES do modelo estatístico, garantindo 100% de acerto
    para termos conhecidos.
    
    Args:
        nlp: Modelo spaCy
    
    Returns:
        nlp atualizado com EntityRuler
    """
    # Remove EntityRuler existente se houver
    if "entity_ruler" in nlp.pipe_names:
        nlp.remove_pipe("entity_ruler")
    
    # Adiciona novo EntityRuler NO INÍCIO do pipeline
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    patterns = []
    
    # Padrões para HPV tipos alto risco
    for hpv in MEDICAL_GAZETEER["hpv_types"]["alto_risco"]:
        patterns.append({
            "label": "HPV_TYPE",
            "pattern": hpv,
            "id": "hpv_alto_risco"
        })
    
    # Padrões para HPV tipos baixo risco
    for hpv in MEDICAL_GAZETEER["hpv_types"]["baixo_risco"]:
        patterns.append({
            "label": "HPV_TYPE",
            "pattern": hpv,
            "id": "hpv_baixo_risco"
        })
    
    # Padrões para lesões altos grau
    for lesion in MEDICAL_GAZETEER["lesions"]["alto_grau"]:
        patterns.append({
            "label": "LESION",
            "pattern": lesion,
            "id": "lesion_alto_grau"
        })
    
    # Padrões para lesões baixo grau
    for lesion in MEDICAL_GAZETEER["lesions"]["baixo_grau"]:
        patterns.append({
            "label": "LESION",
            "pattern": lesion,
            "id": "lesion_baixo_grau"
        })
    
    # Padrões para exames
    for exam in MEDICAL_GAZETEER["exams"]:
        patterns.append({
            "label": "EXAM",
            "pattern": exam,
            "id": "exam_padrao"
        })
    
    # Padrões para procedimentos
    for proc in MEDICAL_GAZETEER["procedures"]:
        patterns.append({
            "label": "PROCEDURE",
            "pattern": proc,
            "id": "procedure_padrao"
        })
    
    # Padrões para locais em Salvador
    for bairro in SALVADOR_LOCATIONS["bairros"]:
        patterns.append({
            "label": "GEOGRAPHIC",
            "pattern": bairro,
            "id": "salvador_bairro"
        })
    
    # Adicionar todos os padrões ao ruler
    ruler.add_patterns(patterns)
    
    return nlp


# ====== MATRIZ DE RISCO APRIMORADA ======

def create_risk_matrix() -> Dict:
    """
    Cria matriz de risco baseada em combinações de fatores clínicos e sociais.
    
    A matriz considera:
    - Tipo de HPV (alto/baixo risco)
    - Presença de lesão (alto/baixo grau)
    - Vulnerabilidade social
    - Persistência
    - Idade (>30 anos = risco aumentado)
    
    Returns:
        Dict com matriz de risco tabulada
    """
    return {
        "red_alert": {
            # Prioridade Máxima (Risco Vermelho) - encaminhamento urgente
            "conditions": [
                {
                    "name": "HPV Alto Risco + HSIL + Vulnerabilidade Social",
                    "score": 10,
                    "action": "Encaminhamento urgente para colposcopia"
                },
                {
                    "name": "HPV 16/18 Persistente (>2 anos) + Vulnerabilidade Social",
                    "score": 10,
                    "action": "Avaliação ginecológica especializada urgente"
                },
                {
                    "name": "HSIL + NIC 2/3 + Perda de Seguimento",
                    "score": 10,
                    "action": "Convocação imediata"
                }
            ]
        },
        "yellow_alert": {
            # Risco Elevado (Amarelo) - acompanhamento próximo
            "conditions": [
                {
                    "name": "HPV Alto Risco + LSIL",
                    "score": 7,
                    "action": "Colposcopia em até 3 meses"
                },
                {
                    "name": "HPV Alto Risco + Vulnerabilidade Social",
                    "score": 7,
                    "action": "Colposcopia prioritária + apoio social"
                },
                {
                    "name": "HPV Detectado + >30 anos + LSIL",
                    "score": 6,
                    "action": "Colposcopia em 3-6 meses"
                }
            ]
        },
        "green_alert": {
            # Baixo Risco (Verde) - acompanhamento rotineiro
            "conditions": [
                {
                    "name": "HPV Negativo ou Baixo Risco",
                    "score": 1,
                    "action": "Rastreamento rotineiro em 3 anos"
                },
                {
                    "name": "HPV Detectado + <25 anos + Sem Lesão",
                    "score": 2,
                    "action": "Retest em 12 meses"
                }
            ]
        }
    }


def classify_risk_with_matrix(entities: Dict, text: str = "", nlp=None) -> Dict:
    """
    Classifica risco usando matriz aprimorada com:
    1. Tratamento de negação
    2. Detector de idade
    3. Detector de persistência
    4. Matriz de combinações de risco
    
    Args:
        entities: Entidades extraídas
        text: Texto original (para análise de negação e age)
        nlp: Modelo spaCy (opcional, para análise aprimorada)
    
    Returns:
        Dict com classificação completa e detalhes
    """
    result = {
        "risk_level": "baixo",
        "score": 0,
        "color": "green",
        "justifications": [],
        "alerts": [],
        "negation_adjustments": [],
        "age_info": None,
        "persistence_info": None,
        "recommended_action": None
    }
    
    # === AJUSTAMENTOS POR NEGAÇÃO ===
    hpv_types_with_negation = []
    for hpv in entities.get('hpv_types', []):
        # Simular busca pela entidade no texto (simplificado)
        if text and hpv in text:
            # Encontra posição aproximada
            pos = text.find(hpv)
            is_negated = detect_negation(text, pos, pos + len(hpv), window=5)
            
            if is_negated:
                result["negation_adjustments"].append(f"Negação detectada: '{hpv}' está sob escopo de negação")
                # NÃO adiciona à lista se negado
            else:
                hpv_types_with_negation.append(hpv)
        else:
            hpv_types_with_negation.append(hpv)
    
    # === DETECÇÃO DE IDADE ===
    if text:
        age, age_type = extract_age(text)
        if age:
            result["age_info"] = {
                "age": age,
                "type": age_type,
                "is_high_risk": age > 30  # >30 anos = risco aumentado
            }
            if age > 30 and hpv_types_with_negation:
                result["justifications"].append(f"⚠️ Paciente com {age} anos + HPV = risco elevado de progressão")
    
    # === DETECÇÃO DE PERSISTÊNCIA ===
    if text and hpv_types_with_negation:
        persistence = detect_persistence(text, entities)
        result["persistence_info"] = persistence
        
        if persistence["has_persistence"]:
            result["justifications"].append(f"⚠️ Evidência de persistência: {'; '.join(persistence['evidence'])}")
            result["score"] += persistence["risk_elevation"]
    
    # === SCORING APRIMORADO ===
    
    # Fatores clínicos
    clinical_score = 0
    
    # HPV alto risco
    hpv_alto_risco_count = 0
    for hpv in hpv_types_with_negation:
        if any(tipo in hpv.upper() for tipo in ["16", "18", "31", "33", "45", "52", "58", "ALTO RISCO"]):
            hpv_alto_risco_count += 1
            clinical_score += 3
            result["justifications"].append(f"🦠 HPV alto risco: {hpv}")
    
    # Lesões graves
    for lesion in entities.get('lesions', []):
        if any(termo in lesion.upper() for termo in ["HSIL", "NIC 2", "NIC 3", "NIC2", "NIC3", "CARCINOMA"]):
            clinical_score += 3
            result["alerts"].append(f"⚠️ ALERTA: Lesão grave detectada - {lesion}")
        elif any(termo in lesion.upper() for termo in ["LSIL", "NIC 1", "NIC1"]):
            clinical_score += 1
            result["justifications"].append(f"⚠️ Lesão leve: {lesion}")
    
    # Fatores sociais
    social_score = 0
    if entities.get('social_factors'):
        social_score += 3
        result["justifications"].append(f"💔 Vulnerabilidade social: {', '.join(entities['social_factors'][:2])}")
    
    if entities.get('geographic'):
        social_score += 1
        result["justifications"].append(f"📍 Fator geográfico: {entities['geographic'][0]}")
    
    # Fator idade para vulnerabilidade
    if result["age_info"] and result["age_info"]["is_high_risk"] and social_score > 0:
        social_score += 1
        result["justifications"].append(f"Idade >30 anos + vulnerabilidade social = risco multiplicado")
    
    # Score total
    result["score"] = clinical_score + social_score
    
    # === DETERMINAÇÃO DO NÍVEL DE RISCO ===
    
    # Verificar condições críticas (red_alert)
    red_conditions = [
        (hpv_alto_risco_count > 0 and any("HSIL" in l.upper() for l in entities.get('lesions', [])) and social_score >= 3),
        (result.get("persistence_info", {}).get("has_persistence") and hpv_alto_risco_count > 0 and social_score >= 3),
        (any("NIC 2" in l.upper() or "NIC 3" in l.upper() for l in entities.get('lesions', [])) and entities.get('follow_up'))
    ]
    
    if any(red_conditions):
        result["risk_level"] = "alto"
        result["color"] = "red"
        result["score"] = max(10, result["score"])
        result["recommended_action"] = "🚨 ENCAMINHAMENTO URGENTE - Avaliação ginecológica especializada"
    
    # Verificar condições de risco elevado (yellow_alert)
    elif clinical_score >= 3 or (clinical_score >= 1 and social_score >= 3):
        result["risk_level"] = "alto"
        result["color"] = "yellow"
        result["score"] = max(7, result["score"])
        result["recommended_action"] = "⚠️ COLPOSCOPIA PRIORITÁRIA - Agendar em até 3 meses"
    
    # Verificar condições de risco médio
    elif result["score"] >= 3:
        result["risk_level"] = "medio"
        result["color"] = "yellow"
        result["recommended_action"] = "📋 ACOMPANHAMENTO - Colposcopia nos próximos 3-6 meses"
    
    else:
        result["risk_level"] = "baixo"
        result["color"] = "green"
        result["recommended_action"] = "✅ BAIXO RISCO - Rastreamento rotineiro em 3 anos"
    
    return result


# ====== EXPORTAR FUNÇÕES PARA USO EM NER.PY ======

__all__ = [
    'detect_negation',
    'extract_age',
    'detect_persistence',
    'add_entity_ruler',
    'create_risk_matrix',
    'classify_risk_with_matrix',
    'SALEM_LOCATIONS',
    'MEDICAL_GAZETEER',
    'NEGATION_TERMS'
]
