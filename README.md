# Neila - Sistema de Classificação de Risco CCU

Sistema de classificação de risco para rastreamento de câncer do colo do útero baseado em **Named Entity Recognition (NER)** com integração de fatores de vulnerabilidade social.

## 🏥 Características

- **NER com 9 Entidades**: Identifica automaticamente tipos de HPV, lesões, exames, procedimentos, carga viral e fatores de vulnerabilidade social
- **Classificação Dual**: Combina risco clínico + vulnerabilidade social para classificação mais precisa
- **Upload de PDFs**: Extração automática de texto de exames em PDF
- **Interface Intuitiva**: Formulários amigáveis para profissionais de saúde
- **Equity-Focused**: Integração com pesquisa sobre desigualdades (Neila Pierote)

## 🛠️ Instalação

### Pré-requisitos
- Python 3.9+
- pip
- virtualenv

### Setup do Projeto

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd Neila
```

2. **Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Baixe o modelo spaCy em português**
```bash
python -m spacy download pt_core_news_sm
```

5. **Execute as migrações do Django**
```bash
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Inicie o servidor**
```bash
python manage.py runserver
```

Acesse em `http://localhost:8000`

## 📊 Estrutura do Projeto

```
Neila/
├── ccu/                  # Configurações Django
├── feedIA/              # Sistema NER para classificação
│   ├── ner.py          # Core do NER com 9 entidades
│   ├── views.py        # Interface de treinamento
│   └── models.py       # Modelos de feedback
├── pacientes/          # Gestão de pacientes
│   ├── models.py       # Modelos (Paciente, StatusSeguimento)
│   ├── views.py        # Views de pacientes
│   └── signals.py      # Auto-classificação com NER
├── users/              # Autenticação
├── models/             # Modelos treinados
│   └── ner_model/      # Modelo NER spaCy
└── requirements.txt    # Dependências Python
```

## 🚀 Uso

### 1. Adicionar um Novo Paciente
- Acesse: `/pacientes/novo/`
- Preencha dados básicos (nome, nascimento, endereço)
- Marque fatores de vulnerabilidade social se aplicável
- Ao salvar, o paciente será **automaticamente classificado** pelo NER

### 2. Treinar o Modelo NER
- Acesse: `/alimentar/`
- **Passo 1**: Adicionar exemplos de treinamento (clínicos + sociais)
- **Passo 2**: Treinar o modelo com dados anotados
- **Passo 3**: Testar com novo texto ou PDF

### 3. Visualizar Classificação
- Acesse detalhes do paciente
- Veja: Entidades identificadas, Score, Risco classificado
- Seção "Vulnerabilidade Social" mostra fatores extraídos

## 📋 Entidades NER Suportadas

### Clínicas
- **HPV_TYPE**: Tipos de HPV (16, 18, 31, 33, 45, 52, 58)
- **LESION**: Lesões precursoras (NIC, HSIL, LSIL)
- **EXAM**: Exames (DNA-HPV, Citopatológico, Colposcopia)
- **PROCEDURE**: Procedimentos (CAF, Conização, LEEP)
- **VIRAL_LOAD**: Carga viral

### Vulnerabilidade Social
- **SOCIAL_FACTOR**: Fatores socioeconômicos (escolaridade, pobreza)
- **GEOGRAPHIC**: Fatores geográficos (região Norte/Nordeste, rural)
- **BEHAVIORAL**: Comportamentais (início precoce, múltiplos parceiros)
- **FOLLOW_UP**: Problemas de seguimento (perda de atendimento)

## 🤖 Sistema de Classificação

### Scoring
```
Score Clínico:
- HPV alto risco: +3
- Lesão grave: +3
- Procedimento: +2
- Carga viral alta: +2

Score Vulnerabilidade:
- Fatores sociais: +3
- Fatores geográficos: +1
- Comportamentais: +1
- Perda de seguimento: +1

Regra Especial:
Score Clínico ≥1 AND Vulnerabilidade ≥3 → ALTO RISCO
```

### Interpretação
- 🟢 **Baixo Risco**: Score < 1
- 🟡 **Médio Risco**: Score 1-2
- 🔴 **Alto Risco**: Score ≥ 3 ou Clínico ≥1 + Social ≥3

## 🔄 Reclassificar Pacientes Existentes

```bash
# Simular reclassificação (dry-run)
python manage.py reclassificar_pacientes --dry-run

# Reclassificar todos os pacientes
python manage.py reclassificar_pacientes

# Reclassificar um paciente específico
python manage.py reclassificar_pacientes --paciente-id 1
```

## 📦 Dependências Principais

- **Django 5.2**: Framework web
- **spaCy 3.7+**: NER (único engine de classificação)
- **PyPDF2 3.0+**: Extração de texto de PDFs

## 🔐 Segurança

- Use variáveis de ambiente para dados sensíveis
- Configure `DEBUG = False` em produção
- Use `ALLOWED_HOSTS` corretamente
- Configure HTTPS em produção

## 📚 Bases para o Modelo

Baseado em pesquisa sobre desigualdades no rastreamento de câncer do colo do útero:
- Respeita desigualdades sociais e territoriais no Brasil
- Integra fatores de vulnerabilidade social na classificação
- Prioriza Região Norte/Nordeste e populações vulneráveis

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## 📧 Contato

Para dúvidas ou sugestões sobre o projeto, entre em contato através do email de suporte.

---

**Última atualização**: Fevereiro de 2026
