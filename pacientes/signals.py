from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    Paciente, HistoricoSexual, HistoricoReprodutivo, Vacinacao,
    ExameDnaHpv, CitopatologicoHistorico, ProcedimentoRealizado, StatusSeguimento
)
from .utils import build_patient_text
from feedIA.ner import classify_patient_text


def _salvar_historico_classificacao(paciente, texto_original, entidades, risco_final, score, justificativas):
    """Salva o histórico de classificação no banco de dados"""
    try:
        from feedIA.models import ClassificacaoHistorico
        
        # Converter justificativas em texto
        texto_justificativa = '\n'.join(justificativas) if justificativas else 'Sem fatores de risco identificados'
        
        ClassificacaoHistorico.objects.create(
            paciente=paciente,
            risco_ia=risco_final,  # Agora é só NER, não há IA separada
            risco_final=risco_final,
            modificador_ner=0,  # Não há mais modificador, classificação é direta
            hpv_types=entidades.get('hpv_types', []),
            lesions=entidades.get('lesions', []),
            exams=entidades.get('exams', []),
            procedures=entidades.get('procedures', []),
            viral_loads=entidades.get('viral_loads', []),
            texto_original=texto_original,
            texto_enriquecido=texto_justificativa
        )
        print(f"[HISTÓRICO] Classificação registrada no banco de dados")
    except Exception as e:
        print(f"[HISTÓRICO] Erro ao salvar: {e}")


def _classificar_paciente(paciente):
    print(f"\n{'#'*80}")
    print(f"### SIGNAL DISPARADO: classificar_paciente chamada para {paciente.nome} ###")
    print(f"{'#'*80}")
    
    texto = build_patient_text(paciente)
    if not texto:
        print(f"[ERRO] Nenhum texto gerado para o paciente")
        return
    
    print(f"\n{'='*80}")
    print(f"[INICIO] Classificacao automatica do paciente {paciente.id} - {paciente.nome}")
    print(f"{'='*80}")
    
    # Mostrar texto analisado
    print(f"\n[INPUT-NER] Texto do paciente que sera analisado:")
    print(f"{'-'*80}")
    print(texto)
    print(f"{'-'*80}")
    
    # Classificar usando apenas NER
    print(f"\n[NER] Extraindo entidades medicas e classificando...")
    resultado = classify_patient_text(texto)
    
    risco_final = resultado['risco']
    justificativas = resultado['justificativas']
    score = resultado['score']
    entidades = resultado['entidades']
    
    # Log das entidades encontradas
    if entidades.get('all_entities'):
        print(f"\n[NER] Entidades extraídas ({len(entidades['all_entities'])} total):")
        print(f"\n  === ENTIDADES CLÍNICAS ===")
        if entidades.get('hpv_types'):
            print(f"  - HPV: {', '.join(entidades['hpv_types'])}")
        if entidades.get('lesions'):
            print(f"  - Lesões: {', '.join(entidades['lesions'])}")
        if entidades.get('viral_loads'):
            print(f"  - Carga Viral: {', '.join(entidades['viral_loads'])}")
        if entidades.get('procedures'):
            print(f"  - Procedimentos: {', '.join(entidades['procedures'])}")
        if entidades.get('exams'):
            print(f"  - Exames: {', '.join(entidades['exams'])}")
        
        # Novas entidades sociais
        print(f"\n  === FATORES DE VULNERABILIDADE SOCIAL ===")
        if entidades.get('social_factors'):
            print(f"  - 📚 Fatores Sociais: {', '.join(entidades['social_factors'])}")
        if entidades.get('geographic'):
            print(f"  - 📍 Localização: {', '.join(entidades['geographic'])}")
        if entidades.get('behavioral'):
            print(f"  - 👥 Comportamentais: {', '.join(entidades['behavioral'])}")
        if entidades.get('follow_up'):
            print(f"  - ⏰ Seguimento: {', '.join(entidades['follow_up'])}")
    else:
        print(f"\n[NER] Nenhuma entidade medica especifica identificada")
        print(f"[NER] Dica: Treine o modelo NER para melhor deteccao de HPV, lesoes, etc.")
    
    # Log da classificação
    print(f"\n[CLASSIFICACAO] Score calculado: {score}")
    if justificativas:
        print(f"[CLASSIFICACAO] Justificativas:")
        for just in justificativas:
            print(f"  - {just}")
    else:
        print(f"[CLASSIFICACAO] Sem fatores de risco identificados")
    
    # Salvar classificação
    justificativas_texto = '\n'.join(justificativas) if justificativas else 'Sem fatores de risco identificados'
    
    StatusSeguimento.objects.update_or_create(
        paciente=paciente,
        defaults={
            'classificacao_risco': risco_final,
            'score_total': score,
            'justificativas': justificativas_texto,
            # Entidades clínicas
            'hpv_types': ', '.join(entidades.get('hpv_types', [])),
            'lesions': ', '.join(entidades.get('lesions', [])),
            'exams': ', '.join(entidades.get('exams', [])),
            'procedures': ', '.join(entidades.get('procedures', [])),
            'viral_loads': ', '.join(entidades.get('viral_loads', [])),
            # Entidades de vulnerabilidade social (NOVO)
            'social_factors': ', '.join(entidades.get('social_factors', [])),
            'geographic_factors': ', '.join(entidades.get('geographic', [])),
            'behavioral_factors': ', '.join(entidades.get('behavioral', [])),
            'follow_up_issues': ', '.join(entidades.get('follow_up', [])),
        }
    )
    
    print(f"\n{'='*80}")
    print(f"[FINAL] Paciente {paciente.nome} classificado como: {risco_final.upper()}")
    print(f"[FINAL] Score: {score} | Risco: {risco_final}")
    print(f"{'='*80}\n")
    
    # Salvar histórico
    _salvar_historico_classificacao(
        paciente=paciente,
        texto_original=texto,
        entidades=entidades,
        risco_final=risco_final,
        score=score,
        justificativas=justificativas
    )
    
    print(f"{'='*80}\n")


@receiver(post_save, sender=Paciente, dispatch_uid='classificar_paciente_paciente')
def classificar_paciente_sender(sender, instance, created, **kwargs):
    print(f"[SIGNAL] post_save Paciente disparado - created={created}, paciente={instance.nome}")
    if created:
        print(f"[SIGNAL] Ignorando - paciente recém-criado")
        return
    print(f"[SIGNAL] Processando edição do paciente...")
    _classificar_paciente(instance)


@receiver(post_save, sender=HistoricoSexual, dispatch_uid='classificar_paciente_historico_sexual')
def classificar_paciente_historico_sexual(sender, instance, created, **kwargs):
    print(f"[SIGNAL] post_save HistoricoSexual disparado - created={created}")
    _classificar_paciente(instance.paciente)


@receiver(post_save, sender=HistoricoReprodutivo, dispatch_uid='classificar_paciente_historico_reprodutivo')
def classificar_paciente_historico_reprodutivo(sender, instance, created, **kwargs):
    print(f"[SIGNAL] post_save HistoricoReprodutivo disparado - created={created}")
    _classificar_paciente(instance.paciente)


@receiver(post_save, sender=Vacinacao, dispatch_uid='classificar_paciente_vacinacao')
def classificar_paciente_vacinacao(sender, instance, created, **kwargs):
    print(f"[SIGNAL] post_save Vacinacao disparado - created={created}")
    _classificar_paciente(instance.paciente)


@receiver(post_save, sender=ExameDnaHpv, dispatch_uid='classificar_paciente_exame_dna')
def classificar_paciente_exame_dna(sender, instance, created, **kwargs):
    print(f"[SIGNAL] post_save ExameDnaHpv disparado - created={created}")
    _classificar_paciente(instance.paciente)


@receiver(post_save, sender=CitopatologicoHistorico, dispatch_uid='classificar_paciente_citopatologico')
def classificar_paciente_citopatologico(sender, instance, created, **kwargs):
    print(f"[SIGNAL] post_save CitopatologicoHistorico disparado - created={created}")
    _classificar_paciente(instance.paciente)


@receiver(post_save, sender=ProcedimentoRealizado, dispatch_uid='classificar_paciente_procedimento')
def classificar_paciente_procedimento(sender, instance, created, **kwargs):
    print(f"[SIGNAL] post_save ProcedimentoRealizado disparado - created={created}")
    _classificar_paciente(instance.paciente)