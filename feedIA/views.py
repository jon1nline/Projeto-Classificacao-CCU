from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import csv
from pathlib import Path
from django.conf import settings
from datetime import datetime
from .models import FeedbackIA
from .ner import train_ner_model, extract_entities, get_training_examples, classify_patient_text, add_training_example
import json
import PyPDF2
import io


def feedback_form(request):
    """Exibe o formulário para gerenciar o NER e adicionar exemplos de treinamento"""
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'add_example':
            # Adicionar novo exemplo de treinamento ao NER
            texto = request.POST.get('texto', '').strip()
            hpv_types = request.POST.get('hpv_types', '').strip()
            lesions = request.POST.get('lesions', '').strip()
            exams = request.POST.get('exams', '').strip()
            procedures = request.POST.get('procedures', '').strip()
            viral_loads = request.POST.get('viral_loads', '').strip()
            social_factors = request.POST.get('social_factors', '').strip()
            geographic = request.POST.get('geographic', '').strip()
            behavioral = request.POST.get('behavioral', '').strip()
            follow_up = request.POST.get('follow_up', '').strip()
            
            if not texto:
                messages.error(request, 'Por favor, insira um texto de exemplo.')
                return redirect('feedback_form')
            
            # Criar anotações para o exemplo (simplificado - apenas marca presença)
            entities = []
            annotations_text = []
            
            if hpv_types:
                annotations_text.append(f"HPV: {hpv_types}")
            if lesions:
                annotations_text.append(f"Lesões: {lesions}")
            if exams:
                annotations_text.append(f"Exames: {exams}")
            if procedures:
                annotations_text.append(f"Procedimentos: {procedures}")
            if viral_loads:
                annotations_text.append(f"Carga Viral: {viral_loads}")
            if social_factors:
                annotations_text.append(f"Fatores Sociais: {social_factors}")
            if geographic:
                annotations_text.append(f"Localização: {geographic}")
            if behavioral:
                annotations_text.append(f"Comportamentais: {behavioral}")
            if follow_up:
                annotations_text.append(f"Seguimento: {follow_up}")
            
            # Salvar exemplo (será usado no próximo treinamento)
            example_with_annotations = f"{texto} [{', '.join(annotations_text)}]"
            FeedbackIA.objects.create(
                texto=example_with_annotations,
                classificacao='treinamento_ner'
            )
            
            messages.success(request, 'Exemplo adicionado! Treine o modelo NER para aplicar as mudanças.')
            return redirect('feedback_form')
        
        elif action == 'classify_text':
            # Classificar texto usando NER (com suporte a PDF)
            texto = request.POST.get('texto', '').strip()
            pdf_file = request.FILES.get('pdf_file')
            
            # Extrair texto do PDF se fornecido
            if pdf_file:
                try:
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
                    texto_pdf = ''
                    for page in pdf_reader.pages:
                        texto_pdf += page.extract_text() + ' '
                    texto = texto_pdf.strip()
                    
                    if not texto:
                        messages.error(request, 'Não foi possível extrair texto do PDF. Verifique se o arquivo não está protegido ou corrompido.')
                        return redirect('feedback_form')
                    
                    messages.info(request, f'✅ Texto extraído do PDF: {len(texto)} caracteres')
                except Exception as e:
                    messages.error(request, f'Erro ao processar PDF: {str(e)}')
                    return redirect('feedback_form')
            
            if not texto:
                messages.error(request, 'Por favor, insira um texto ou carregue um PDF para classificar.')
                return redirect('feedback_form')
            
            try:
                resultado = classify_patient_text(texto)
                risco = resultado['risco']
                justificativas = resultado['justificativas']
                entidades = resultado['entidades']
                
                # Salvar a classificação
                FeedbackIA.objects.create(
                    texto=texto[:1000],  # Limitar tamanho para evitar textos muito longos
                    classificacao=risco
                )
                
                messages.success(
                    request, 
                    f'Texto classificado como: {risco.upper()}. '
                    f'Justificativas: {"; ".join(justificativas) if justificativas else "Sem fatores de risco identificados"}'
                )
            except Exception as e:
                messages.error(request, f'Erro ao classificar: {str(e)}')
            
            return redirect('feedback_form')
    
    # Buscar exemplos de treinamento e classificações
    feedbacks = FeedbackIA.objects.all().order_by('-criado_em')[:50]
    training_examples = get_training_examples()
    
    return render(request, 'feedIA/feedback_form.html', {
        'feedbacks': feedbacks,
        'n_training_examples': len(training_examples)
    })


def treinar_ner(request):
    """Treina o modelo NER para extração de entidades médicas"""
    if request.method != 'POST':
        return redirect('feedback_form')
    
    try:
        training_data = get_training_examples()
        
        # Adicionar validação de quantidade mínima
        if len(training_data) < 20:
            messages.warning(
                request, 
                f'Apenas {len(training_data)} exemplos disponíveis. '
                'Recomenda-se pelo menos 30 exemplos para melhor precisão.'
            )
        
        ok, msg = train_ner_model(training_data, n_iter=30)
        
        if ok:
            messages.success(request, f'{msg} O modelo está pronto para classificar pacientes!')
        else:
            messages.error(request, msg)
    except Exception as exc:
        messages.error(request, f'Erro ao treinar modelo NER: {exc}')
    
    return redirect('feedback_form')


def extrair_entidades(request):
    """Extrai entidades de um texto via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    import json as json_lib
    try:
        data = json_lib.loads(request.body)
        texto = data.get('texto', '').strip()
    except:
        texto = request.POST.get('texto', '').strip()
    
    if not texto:
        return JsonResponse({'error': 'Texto vazio'}, status=400)
    
    try:
        entities = extract_entities(texto)
        return JsonResponse({
            'success': True,
            'entities': entities
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Erro ao extrair entidades: {str(e)}'
        }, status=500)


def classificar_texto(request):
    """Classifica um texto usando NER e retorna JSON"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    import json as json_lib
    try:
        data = json_lib.loads(request.body)
        texto = data.get('texto', '').strip()
    except:
        texto = request.POST.get('texto', '').strip()
    
    if not texto:
        return JsonResponse({'error': 'Texto vazio'}, status=400)
    
    try:
        resultado = classify_patient_text(texto)
        return JsonResponse({
            'success': True,
            'risco': resultado['risco'],
            'justificativas': resultado['justificativas'],
            'score': resultado['score'],
            'entidades': resultado['entidades']
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Erro ao classificar: {str(e)}'
        }, status=500)


def estatisticas_ner(request):
    """Retorna estatísticas sobre o modelo NER"""
    training_examples = get_training_examples()
    
    # Contar por tipo de entidade
    entity_counts = {
        'HPV_TYPE': 0,
        'LESION': 0,
        'EXAM': 0,
        'PROCEDURE': 0,
        'VIRAL_LOAD': 0
    }
    
    for text, annots in training_examples:
        for start, end, label in annots.get('entities', []):
            if label in entity_counts:
                entity_counts[label] += 1
    
    # Verificar se modelo está treinado
    from pathlib import Path
    from django.conf import settings
    model_dir = Path(settings.BASE_DIR) / "models" / "ner_model"
    modelo_treinado = model_dir.exists()
    
    return JsonResponse({
        'success': True,
        'total_exemplos': len(training_examples),
        'modelo_treinado': modelo_treinado,
        'entidades_por_tipo': entity_counts
    })
