"""
Módulo de Named Entity Recognition (NER) para extração de entidades médicas.
Identifica: tipos de HPV, lesões, procedimentos e outros termos clínicos.
"""

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
from pathlib import Path
from django.conf import settings
import json
import random

# Diretório para salvar o modelo NER
NER_MODEL_DIR = Path(settings.BASE_DIR) / "models" / "ner_model"

# Definição das entidades que queremos identificar
ENTITY_LABELS = [
    "HPV_TYPE",      # HPV 16, HPV 18, HPV 11, HPV alto risco, etc.
    "LESION",        # lesão precursora, LSIL, HSIL, NIC, etc.
    "EXAM",          # DNA-HPV, citopatológico, colposcopia, biópsia
    "PROCEDURE",     # CAF, conização, crioterapia
    "VIRAL_LOAD",    # carga viral alta, baixa carga viral
    "SOCIAL_FACTOR", # escolaridade baixa, vulnerabilidade social
    "GEOGRAPHIC",    # região Norte/Nordeste, área de difícil acesso
    "BEHAVIORAL",    # início precoce atividade sexual, múltiplos parceiros
    "FOLLOW_UP",     # perda de seguimento, ausência de rastreamento
]

# Dados de treinamento anotados
TRAINING_DATA = [
    ("Paciente com HPV 16 detectado no exame DNA-HPV", {
        "entities": [(14, 20, "HPV_TYPE"), (36, 43, "EXAM")]
    }),
    ("HPV 18 confirmado em DNA-HPV com lesão precursora", {
        "entities": [(0, 6, "HPV_TYPE"), (20, 27, "EXAM"), (32, 48, "LESION")]
    }),
    ("Resultado negativo para HPV de alto risco", {
        "entities": [(24, 41, "HPV_TYPE")]
    }),
    ("Citopatológico mostra LSIL compatível com HPV", {
        "entities": [(0, 14, "EXAM"), (22, 26, "LESION"), (43, 46, "HPV_TYPE")]
    }),
    ("Detectado HPV 11 em exame de DNA-HPV", {
        "entities": [(10, 16, "HPV_TYPE"), (29, 36, "EXAM")]
    }),
    ("HSIL confirmado com necessidade de CAF", {
        "entities": [(0, 4, "LESION"), (36, 39, "PROCEDURE")]
    }),
    ("Biópsia revelou NIC 3 associado a HPV 16", {
        "entities": [(0, 7, "EXAM"), (16, 21, "LESION"), (34, 40, "HPV_TYPE")]
    }),
    ("Carga viral alta detectada no DNA-HPV", {
        "entities": [(0, 16, "VIRAL_LOAD"), (30, 37, "EXAM")]
    }),
    ("Realizada conização por lesão de alto grau", {
        "entities": [(10, 19, "PROCEDURE"), (24, 42, "LESION")]
    }),
    ("HPV alto risco positivo com LSIL", {
        "entities": [(0, 14, "HPV_TYPE"), (28, 32, "LESION")]
    }),
    ("Colposcopia evidenciou lesão precursora NIC 2", {
        "entities": [(0, 11, "EXAM"), (23, 39, "LESION"), (40, 45, "LESION")]
    }),
    ("DNA-HPV negativo sem sinais de lesão", {
        "entities": [(0, 7, "EXAM"), (31, 36, "LESION")]
    }),
    ("Tratamento com crioterapia para HPV persistente", {
        "entities": [(15, 26, "PROCEDURE"), (32, 47, "HPV_TYPE")]
    }),
    ("HPV 31 e HPV 33 detectados em análise molecular", {
        "entities": [(0, 6, "HPV_TYPE"), (9, 15, "HPV_TYPE")]
    }),
    ("Baixa carga viral de HPV de baixo risco", {
        "entities": [(0, 17, "VIRAL_LOAD"), (21, 39, "HPV_TYPE")]
    }),
    ("NIC 1 observado no exame citopatológico", {
        "entities": [(0, 5, "LESION"), (23, 39, "EXAM")]
    }),
    ("Procedimento CAF realizado com sucesso", {
        "entities": [(13, 16, "PROCEDURE")]
    }),
    ("HPV 45 positivo requer acompanhamento", {
        "entities": [(0, 6, "HPV_TYPE")]
    }),
    ("Lesão de alto grau HSIL identificada", {
        "entities": [(0, 18, "LESION"), (19, 23, "LESION")]
    }),
    ("Exame DNA-HPV detectou HPV 52 com alta carga viral", {
        "entities": [(6, 13, "EXAM"), (23, 29, "HPV_TYPE"), (34, 51, "VIRAL_LOAD")]
    }),
    ("Paciente com HPV 58 detectado no DNA-HPV", {"entities": [(13, 19, "HPV_TYPE"), (33, 40, "EXAM")]}),
    ("Biópsia confirmou NIC 2 em paciente vulnerável", {"entities": [(0, 7, "EXAM"), (18, 23, "LESION")]}),
    ("Encaminhamento para colposcopia por lesão precursora", {"entities": [(20, 31, "EXAM"), (36, 52, "LESION")]}),
    ("Tratamento com CAF indicado para lesão de alto grau", {"entities": [(15, 18, "PROCEDURE"), (33, 51, "LESION")]}),
    ("Monitoramento longitudinal de HPV 18 positivo", {"entities": [(30, 36, "HPV_TYPE")]}),

    ("Teste de DNA-HPV positivo para HPV 16", {
        "entities": [(9, 16, "EXAM"), (31, 37, "HPV_TYPE")]
    }),
    ("Resultado positivo para HPV 18 com carga viral alta", {
        "entities": [(24, 30, "HPV_TYPE"), (35, 51, "VIRAL_LOAD")]
    }),
    ("Paciente com teste molecular positivo para HPV de alto risco", {
        "entities": [(13, 28, "EXAM"), (43, 60, "HPV_TYPE")]
    }),
    ("Teste de DNA-HPV reagente para tipos oncogênicos", {
        "entities": [(9, 16, "EXAM"), (31, 48, "HPV_TYPE")]
    }),
    ("Diagnóstico positivo de HPV 31 no rastreamento", {
        "entities": [(0, 11, "EXAM"), (24, 30, "HPV_TYPE")]
    }),
    ("Resultado positivo indica necessidade de colposcopia", {
        "entities": [(41, 52, "EXAM")]
    }),
    ("HPV 16 positivo associado a lesão de alto grau", {
        "entities": [(0, 6, "HPV_TYPE"), (28, 46, "LESION")]
    }),
    ("Presença de HPV 52 confirmada em teste positivo", {
        "entities": [(12, 18, "HPV_TYPE")]
    }),
    ("Teste de DNA-HPV positivo requer seguimento longitudinal", {
        "entities": [(9, 16, "EXAM")]
    }),
    ("Mulher com resultado positivo no rastreamento organizado", {
        "entities": [(33, 56, "EXAM")]
    }),
    
    # Fatores socioeconômicos e vulnerabilidade
    ("Paciente com baixa escolaridade e HPV 16", {
        "entities": [(14, 32, "SOCIAL_FACTOR"), (35, 41, "HPV_TYPE")]
    }),
    ("Mulher em situação de vulnerabilidade social", {
        "entities": [(18, 44, "SOCIAL_FACTOR")]
    }),
    ("Ensino fundamental incompleto, dificuldade de acesso aos serviços", {
        "entities": [(0, 29, "SOCIAL_FACTOR"), (31, 65, "GEOGRAPHIC")]
    }),
    ("Residente na Região Norte com HSIL", {
        "entities": [(13, 25, "GEOGRAPHIC"), (30, 34, "LESION")]
    }),
    ("Mora em área de difícil acesso no Nordeste", {
        "entities": [(8, 30, "GEOGRAPHIC"), (34, 42, "GEOGRAPHIC")]
    }),
    ("Início da atividade sexual aos 14 anos", {
        "entities": [(0, 38, "BEHAVIORAL")]
    }),
    ("Múltiplos parceiros sexuais e HPV persistente", {
        "entities": [(0, 23, "BEHAVIORAL"), (26, 45, "HPV_TYPE")]
    }),
    ("Perda de seguimento após primeiro exame alterado", {
        "entities": [(0, 19, "FOLLOW_UP")]
    }),
    ("Ausência de rastreamento há mais de 5 anos", {
        "entities": [(0, 42, "FOLLOW_UP")]
    }),
    ("Não compareceu às convocações para colposcopia", {
        "entities": [(0, 16, "FOLLOW_UP"), (39, 50, "EXAM")]
    }),
    ("Paciente sem rastreamento prévio e escolaridade baixa", {
        "entities": [(13, 32, "FOLLOW_UP"), (39, 57, "SOCIAL_FACTOR")]
    }),
    ("Condições socioeconômicas desfavoráveis na Região Norte", {
        "entities": [(0, 39, "SOCIAL_FACTOR"), (43, 55, "GEOGRAPHIC")]
    }),
    ("Início precoce da vida sexual com múltiplos parceiros", {
        "entities": [(0, 29, "BEHAVIORAL"), (34, 53, "BEHAVIORAL")]
    }),
    ("Falha no seguimento longitudinal, residente em área rural", {
        "entities": [(0, 32, "FOLLOW_UP"), (34, 57, "GEOGRAPHIC")]
    }),
    ("Mulher negra com baixo nível de escolaridade", {
        "entities": [(13, 44, "SOCIAL_FACTOR")]
    }),
]


def create_ner_model():
    """Cria um novo modelo NER em português."""
    nlp = spacy.blank("pt")
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    # Adicionar os labels das entidades
    for label in ENTITY_LABELS:
        ner.add_label(label)
    
    return nlp


def train_ner_model(training_data=None, n_iter=30):
    """
    Treina o modelo NER com dados anotados.
    
    Args:
        training_data: Lista de tuplas (text, {"entities": [(start, end, label)]})
        n_iter: Número de iterações de treinamento
    
    Returns:
        Tuple (success: bool, message: str)
    """
    if training_data is None:
        training_data = TRAINING_DATA
    
    if len(training_data) < 10:
        return False, "Conjunto de treinamento muito pequeno. Adicione mais exemplos anotados."
    
    try:
        # Criar modelo
        nlp = create_ner_model()
        ner = nlp.get_pipe("ner")
        
        # Preparar dados de treinamento
        train_examples = []
        for text, annots in training_data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annots)
            train_examples.append(example)
        
        # Configurar otimizador
        optimizer = nlp.begin_training()
        
        # Treinar
        losses = {}
        for epoch in range(n_iter):
            random.shuffle(train_examples)
            
            batches = minibatch(train_examples, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                nlp.update(batch, drop=0.3, sgd=optimizer, losses=losses)
            
            if epoch % 5 == 0:
                print(f"Época {epoch}: Loss = {losses.get('ner', 0):.4f}")
        
        # Salvar modelo
        NER_MODEL_DIR.mkdir(parents=True, exist_ok=True)
        nlp.to_disk(NER_MODEL_DIR)
        
        # Salvar metadados (converter float32/numpy para Python nativo)
        final_loss = losses.get('ner', 0)
        if hasattr(final_loss, 'item'):  # numpy/torch tensor
            final_loss = float(final_loss.item())
        else:
            final_loss = float(final_loss)
        
        metadata = {
            "labels": ENTITY_LABELS,
            "n_examples": len(training_data),
            "n_iterations": n_iter,
            "final_loss": final_loss
        }
        
        with open(NER_MODEL_DIR / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return True, f"Modelo NER treinado com sucesso! {len(training_data)} exemplos, Loss final: {final_loss:.4f}"
    
    except Exception as e:
        return False, f"Erro ao treinar modelo NER: {str(e)}"


def load_ner_model():
    """Carrega o modelo NER treinado."""
    if not NER_MODEL_DIR.exists():
        return None
    
    try:
        nlp = spacy.load(NER_MODEL_DIR)
        return nlp
    except Exception as e:
        print(f"Erro ao carregar modelo NER: {e}")
        return None


def extract_entities(text):
    """
    Extrai entidades médicas de um texto.
    
    Args:
        text: Texto para análise
    
    Returns:
        Dict com entidades extraídas por categoria
    """
    nlp = load_ner_model()
    
    # Se não há modelo treinado, retornar vazio
    if nlp is None:
        print("[NER] Modelo não treinado. Execute o treinamento primeiro.")
        return {
            "hpv_types": [],
            "lesions": [],
            "exams": [],
            "procedures": [],
            "viral_loads": [],
            "social_factors": [],
            "geographic": [],
            "behavioral": [],
            "follow_up": [],
            "all_entities": []
        }
    
    try:
        doc = nlp(text)
        
        entities = {
            "hpv_types": [],
            "lesions": [],
            "exams": [],
            "procedures": [],
            "viral_loads": [],
            "social_factors": [],
            "geographic": [],
            "behavioral": [],
            "follow_up": [],
            "all_entities": []
        }
        
        # Palavras comuns a serem filtradas
        common_words = [
            'idade', 'anos', 'grupo', 'etnico', 'sexualidade', 'escolaridade',
            'cidade', 'bairro', 'inicio', 'numero', 'gestacoes', 'atividade',
            'parceiros', 'totalmente', 'vacinado', 'resultado', 'positivo',
            'negativo', 'exame', 'superior', 'indigena', 'branca', 'preta',
            'parda', 'amarela', 'salvador', 'tororo', 'endereco', 'rua',
            'avenida', 'telefone', 'celular', 'email'
        ]
        
        # Filtrar entidades válidas
        for ent in doc.ents:
            entity_text = ent.text.strip()
            
            # Remover pontuação inicial/final
            entity_text = entity_text.strip(':.,;!?()-[]{}"\' ')
            
            # Validações básicas
            if len(entity_text) < 3:
                continue
            
            if not any(c.isalpha() for c in entity_text):
                continue
            
            # Filtrar palavras comuns
            if entity_text.lower() in common_words:
                continue
            
            # Validar por tipo de entidade
            if ent.label_ == "HPV_TYPE":
                # HPV deve conter número ou palavras chave específicas
                if not any(termo in entity_text.upper() for termo in ['HPV', '16', '18', '31', '33', '45', '52', '58']):
                    continue
                # Filtrar "HPV:" sem número
                if entity_text.strip() in ['HPV', 'HPV:']:
                    continue
            
            elif ent.label_ == "LESION":
                # Lesão deve conter termos médicos específicos
                termos_lesao = ['NIC', 'HSIL', 'LSIL', 'LESAO', 'DISPLASIA', 'CARCINOMA', 
                               'NEOPLASIA', 'GRAU', 'ALTO', 'BAIXO', 'PRECURSORA']
                if not any(termo in entity_text.upper() for termo in termos_lesao):
                    continue
            
            elif ent.label_ == "VIRAL_LOAD":
                # Carga viral deve conter termos específicos
                termos_carga = ['CARGA', 'VIRAL', 'ALTA', 'BAIXA', 'ELEVADA', 'COPIAS']
                if not any(termo in entity_text.upper() for termo in termos_carga):
                    continue
            
            elif ent.label_ == "EXAM":
                # Exames devem ser termos médicos conhecidos
                exames_validos = ['DNA-HPV', 'DNA HPV', 'CITOPATOLOGICO', 'COLPOSCOPIA', 
                                 'BIOPSIA', 'PAPANICOLAU', 'PCR', 'CAPTURA', 'HIBRIDA']
                if not any(exame in entity_text.upper() for exame in exames_validos):
                    continue
            
            elif ent.label_ == "PROCEDURE":
                # Procedimentos devem ser termos médicos válidos
                proc_validos = ['CONIZACAO', 'CAF', 'LEEP', 'CRIOCAUTERIZACAO', 
                               'CAUTERIZACAO', 'EXERESE', 'CIRURGIA']
                if not any(proc in entity_text.upper() for proc in proc_validos):
                    continue
            
            elif ent.label_ == "SOCIAL_FACTOR":
                # Fatores sociais (não precisa validação rígida)
                pass
            
            elif ent.label_ == "GEOGRAPHIC":
                # Fatores geográficos (não precisa validação rígida)
                pass
            
            elif ent.label_ == "BEHAVIORAL":
                # Fatores comportamentais (não precisa validação rígida)
                pass
            
            elif ent.label_ == "FOLLOW_UP":
                # Acompanhamento (não precisa validação rígida)
                pass
            
            # Se passou em todas as validações, adicionar
            entity_info = {
                "text": entity_text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            
            entities["all_entities"].append(entity_info)
            
            if ent.label_ == "HPV_TYPE":
                entities["hpv_types"].append(entity_text)
            elif ent.label_ == "LESION":
                entities["lesions"].append(entity_text)
            elif ent.label_ == "EXAM":
                entities["exams"].append(entity_text)
            elif ent.label_ == "PROCEDURE":
                entities["procedures"].append(entity_text)
            elif ent.label_ == "VIRAL_LOAD":
                entities["viral_loads"].append(entity_text)
            elif ent.label_ == "SOCIAL_FACTOR":
                entities["social_factors"].append(entity_text)
            elif ent.label_ == "GEOGRAPHIC":
                entities["geographic"].append(entity_text)
            elif ent.label_ == "BEHAVIORAL":
                entities["behavioral"].append(entity_text)
            elif ent.label_ == "FOLLOW_UP":
                entities["follow_up"].append(entity_text)
        
        return entities
    
    except Exception as e:
        print(f"[NER] Erro ao extrair entidades: {e}")
        return {
            "hpv_types": [],
            "lesions": [],
            "exams": [],
            "procedures": [],
            "viral_loads": [],
            "social_factors": [],
            "geographic": [],
            "behavioral": [],
            "follow_up": [],
            "all_entities": []
        }


def add_training_example(text, entities):
    """
    Adiciona um novo exemplo de treinamento.
    
    Args:
        text: Texto do exemplo
        entities: Lista de tuplas (start, end, label)
    
    Returns:
        Bool indicando sucesso
    """
    training_file = Path(settings.BASE_DIR) / "data" / "ner_training.json"
    training_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Carregar exemplos existentes
    if training_file.exists():
        with open(training_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    
    # Adicionar novo exemplo
    data.append((text, {"entities": entities}))
    
    # Salvar
    with open(training_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return True


def get_training_examples():
    """Retorna todos os exemplos de treinamento (padrão + personalizados)."""
    training_file = Path(settings.BASE_DIR) / "data" / "ner_training.json"
    
    all_examples = list(TRAINING_DATA)
    
    if training_file.exists():
        with open(training_file, "r", encoding="utf-8") as f:
            custom_examples = json.load(f)
            all_examples.extend(custom_examples)
    
    return all_examples


def classify_risk_by_entities(entities):
    """
    Classifica risco do paciente baseado nas entidades médicas E socioeconômicas extraídas.
    
    Regras de classificação baseadas no projeto de pesquisa sobre desigualdades no CCU:
    
    RISCO CLÍNICO:
    - ALTO: HPV alto risco (16,18,31,33,45,52,58) OU lesões graves (HSIL, NIC 2/3) 
            OU carga viral alta OU procedimentos realizados
    - MÉDIO: HPV outros tipos OU lesões leves (LSIL, NIC 1) OU exames positivos
    - BAIXO: Sem entidades de risco ou apenas exames negativos
    
    VULNERABILIDADE SOCIAL (pode elevar o risco):
    - Fatores socioeconômicos (+3): escolaridade baixa, vulnerabilidade social
    - Fatores geográficos (+1): Região Norte/Nordeste, área de difícil acesso
    - Fatores comportamentais (+1): início precoce atividade sexual, múltiplos parceiros
    - Perda de seguimento (+1): ausência de rastreamento, falha em convocações
    
    Args:
        entities: Dict com entidades extraídas (retorno de extract_entities)
    
    Returns:
        Tuple (risco: str, justificativa: list, score_total: int)
    """
    score_clinico = 0
    score_vulnerabilidade = 0
    justificativas = []
    
    # === RISCO CLÍNICO ===
    
    # HPV de alto risco
    hpv_alto_risco = ['16', '18', '31', '33', '45', '52', '58', 'ALTO RISCO', 'ONCOGENICO']
    for hpv in entities.get('hpv_types', []):
        if any(tipo in hpv.upper() for tipo in hpv_alto_risco):
            score_clinico += 3
            justificativas.append(f"🦠 HPV alto risco: {hpv}")
            break
    
    # Lesões graves
    lesoes_graves = ['HSIL', 'NIC 3', 'NIC 2', 'NIC3', 'NIC2', 'ALTO GRAU', 'HIGH-GRADE', 
                     'CARCINOMA', 'NEOPLASIA']
    lesoes_leves = ['LSIL', 'NIC 1', 'NIC1', 'BAIXO GRAU', 'LOW-GRADE', 'DISPLASIA LEVE']
    
    for lesion in entities.get('lesions', []):
        if any(grave in lesion.upper() for grave in lesoes_graves):
            score_clinico += 3
            justificativas.append(f"⚠️ Lesão grave: {lesion}")
            break
        elif any(leve in lesion.upper() for leve in lesoes_leves):
            score_clinico += 1
            justificativas.append(f"⚠️ Lesão leve: {lesion}")
    
    # Carga viral
    for viral in entities.get('viral_loads', []):
        if any(termo in viral.upper() for termo in ['ALTA', 'HIGH', 'ELEVADA']):
            score_clinico += 2
            justificativas.append(f"📊 Carga viral alta: {viral}")
        elif any(termo in viral.upper() for termo in ['BAIXA', 'LOW']):
            score_clinico -= 1
            justificativas.append(f"📊 Carga viral baixa: {viral}")
    
    # Procedimentos realizados indicam necessidade de tratamento
    if entities.get('procedures') and len(entities['procedures']) > 0:
        score_clinico += 2
        justificativas.append(f"⚕️ Procedimento realizado: {', '.join(entities['procedures'])}")
    
    # HPV outros tipos (não alto risco) = risco médio
    if entities.get('hpv_types') and not any(any(tipo in hpv.upper() for tipo in hpv_alto_risco) for hpv in entities.get('hpv_types', [])):
        score_clinico += 1
        justificativas.append(f"🦠 HPV detectado: {', '.join(entities['hpv_types'])}")
    
    # === VULNERABILIDADE SOCIAL ===
    
    # Fatores socioeconômicos (+3 pontos) - Desigualdades estruturais
    if entities.get('social_factors'):
        score_vulnerabilidade += 3
        justificativas.append(f"📚 Vulnerabilidade social: {', '.join(entities['social_factors'][:2])}")
    
    # Fatores geográficos (+1 ponto) - Desigualdades regionais
    if entities.get('geographic'):
        score_vulnerabilidade += 1
        regioes_prioritarias = ['NORTE', 'NORDESTE', 'RURAL', 'DIFICIL ACESSO', 'REMOTA']
        for geo in entities['geographic']:
            if any(reg in geo.upper() for reg in regioes_prioritarias):
                justificativas.append(f"📍 Região prioritária: {geo}")
                break
    
    # Fatores comportamentais (+1 ponto) - Risco epidemiológico
    if entities.get('behavioral'):
        score_vulnerabilidade += 1
        justificativas.append(f"👥 Fator comportamental: {', '.join(entities['behavioral'][:2])}")
    
    # Perda de seguimento (+1 ponto) - Gargalo do sistema
    if entities.get('follow_up'):
        score_vulnerabilidade += 1
        justificativas.append(f"⏰ Alerta de seguimento: {', '.join(entities['follow_up'][:2])}")
    
    # === CLASSIFICAÇÃO FINAL ===
    # Score total combina risco clínico + vulnerabilidade social
    score_total = score_clinico + score_vulnerabilidade
    
    # Vulnerabilidade social pode elevar um médio risco para alto
    if score_clinico >= 3:
        risco = 'alto'
    elif score_clinico >= 1 and score_vulnerabilidade >= 3:
        risco = 'alto'
        justificativas.insert(0, "⚠️ ALERTA: Risco elevado por vulnerabilidade social")
    elif score_total >= 3:
        risco = 'medio'
    elif score_total >= 1:
        risco = 'medio'
    else:
        risco = 'baixo'
    
    # Adicionar resumo de scores
    if score_vulnerabilidade > 0:
        justificativas.append(f"📊 Score Clínico: {score_clinico} | Vulnerabilidade: {score_vulnerabilidade}")
    
    return risco, justificativas, score_total


def classify_patient_text(text):
    """
    Classifica o risco de um paciente baseado no texto completo.
    Extrai entidades médicas E sociais, aplica regras de classificação considerando
    desigualdades sociais e territoriais (projeto Neila Pierote).
    
    Args:
        text: Texto com informações do paciente
    
    Returns:
        Dict com classificação completa:
        {
            'risco': 'alto|medio|baixo',
            'justificativas': ['motivo 1', 'motivo 2'],
            'score': int,
            'entidades': {...}
        }
    """
    # Extrair entidades (clínicas + sociais)
    entidades = extract_entities(text)
    
    # Classificar baseado nas entidades (risco clínico + vulnerabilidade social)
    risco, justificativas, score = classify_risk_by_entities(entidades)
    
    return {
        'risco': risco,
        'justificativas': justificativas,
        'score': score,
        'entidades': entidades
    }
