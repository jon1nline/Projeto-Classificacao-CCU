from datetime import date


def calcular_idade(data_nascimento):
    if not data_nascimento:
        return None
    hoje = date.today()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))


def build_patient_text(paciente):
    """Gera um texto consolidado do paciente para classificação pela IA."""
    partes = []

    idade = calcular_idade(paciente.data_nascimento)
    if idade is not None:
        partes.append(f"Idade: {idade} anos.")

    partes.append(f"Grupo étnico: {paciente.get_cor_display()}.")
    partes.append(f"Sexualidade: {paciente.get_sexualidade_display()}. Escolaridade: {paciente.get_escolaridade_display()}.")
    partes.append(f"Cidade: {paciente.cidade}, {paciente.get_estado_display()}. Bairro: {paciente.bairro}.")
    
    # === FATORES DE VULNERABILIDADE SOCIAL ===
    
    # Região geográfica prioritária (Norte/Nordeste)
    regioes_norte_nordeste = ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO', 'AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE']
    if paciente.estado in regioes_norte_nordeste:
        partes.append(f"Região {paciente.get_estado_display()} (Norte/Nordeste).")
    
    # Área rural/difícil acesso
    if paciente.area_rural:
        partes.append("Residente em área rural ou de difícil acesso.")
    
    # Perda de seguimento
    if paciente.perda_seguimento:
        partes.append("Histórico de perda de seguimento no rastreamento.")
    
    # Primeira vez no rastreamento
    if paciente.primeira_vez_rastreamento:
        partes.append("Primeira vez no programa de rastreamento de câncer de colo de útero.")
    
    # Escolaridade baixa (vulnerabilidade)
    if paciente.escolaridade in ['sem_escolaridade', 'ensino_fundamental']:
        partes.append(f"Baixa escolaridade: {paciente.get_escolaridade_display()}.")
    
    # Observações de vulnerabilidade
    if paciente.observacoes_vulnerabilidade:
        partes.append(f"Vulnerabilidade: {paciente.observacoes_vulnerabilidade}")
    
    # === HISTÓRICO SEXUAL ===

    historico_sexual = getattr(paciente, 'historico_sexual', None)
    if historico_sexual:
        if historico_sexual.idade_inicio_atividade_sexual is not None:
            partes.append(f"Início atividade sexual: {historico_sexual.idade_inicio_atividade_sexual} anos.")
            # Início precoce (<16 anos) é fator de risco comportamental
            if historico_sexual.idade_inicio_atividade_sexual < 16:
                partes.append("Início precoce da atividade sexual (antes dos 16 anos).")
        if historico_sexual.numero_parceiros is not None:
            partes.append(f"Número de parceiros: {historico_sexual.numero_parceiros}.")
            # Múltiplos parceiros (>3) é fator de risco
            if historico_sexual.numero_parceiros > 3:
                partes.append("Múltiplos parceiros sexuais ao longo da vida.")

    historico_reprodutivo = getattr(paciente, 'historico_reprodutivo', None)
    if historico_reprodutivo:
        if historico_reprodutivo.numero_gestacoes is not None:
            partes.append(f"Gestações: {historico_reprodutivo.numero_gestacoes}.")
        if historico_reprodutivo.historico_ists:
            partes.append(f"Histórico ISTs: {historico_reprodutivo.historico_ists}.")

    vacinacao = getattr(paciente, 'vacinacao', None)
    if vacinacao:
        partes.append(f"Vacinação HPV: {vacinacao.get_status_vacinacao_display()}.")

    ultimo_dna = paciente.exames_dna_hpv.order_by('-data_exame').first()
    if ultimo_dna:
        # Gerar texto claro para NER detectar HPV
        tipo_hpv_display = ultimo_dna.get_tipo_hpv_display()
        
        # Resultado positivo com tipo de HPV específico
        if ultimo_dna.resultado.upper() in ['POSITIVO', 'POSITIVA', 'REAGENTE']:
            partes.append(f"Teste de DNA-HPV positivo para {tipo_hpv_display}.")
        else:
            partes.append(f"DNA-HPV: {tipo_hpv_display}, resultado {ultimo_dna.resultado}.")
        
        # Carga viral com classificação
        if ultimo_dna.carga_viral:
            try:
                valor = float(str(ultimo_dna.carga_viral).replace(',', '.').replace(' ', ''))
                if valor >= 1000:
                    partes.append(f"Carga viral alta detectada: {ultimo_dna.carga_viral} cópias.")
                elif valor >= 100:
                    partes.append(f"Carga viral moderada: {ultimo_dna.carga_viral} cópias.")
                else:
                    partes.append(f"Baixa carga viral: {ultimo_dna.carga_viral} cópias.")
            except (ValueError, TypeError):
                partes.append(f"Carga viral: {ultimo_dna.carga_viral}.")

    ultimo_cito = paciente.citopatologicos.order_by('-data_exame').first()
    if ultimo_cito:
        partes.append(
            f"Citopatológico {ultimo_cito.data_exame}: {ultimo_cito.get_resultado_display()}."
        )

    ultimo_proc = paciente.procedimentos.order_by('-data_procedimento').first()
    if ultimo_proc:
        partes.append(
            f"Procedimento {ultimo_proc.get_tipo_procedimento_display()} em {ultimo_proc.data_procedimento}."
        )
        if ultimo_proc.complicacoes:
            partes.append(f"Complicações: {ultimo_proc.complicacoes}.")

    return " ".join(partes).strip()


