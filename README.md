---
title: Projeto Neila
emoji: 🏥
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
---

# Projeto Neila - Análise de Risco de Câncer Cervical
Este é um projeto Django rodando em Docker no Hugging Face Spaces.


# Neila - Sistema de Classificação de Risco CCU

Sistema de classificação de risco para rastreamento de câncer do colo do útero baseado em **Named Entity Recognition (NER)** com integração de fatores de vulnerabilidade social.

## 🏥 Características

- **NER com 9 Entidades**: Identifica automaticamente tipos de HPV, lesões, exames, procedimentos, carga viral e fatores de vulnerabilidade social
- **Classificação Dual**: Combina risco clínico + vulnerabilidade social para classificação mais precisa
- **Upload de PDFs**: Extração automática de texto de exames em PDF
- **Interface Intuitiva**: Formulários amigáveis para profissionais de saúde
- **Equity-Focused**: Integração com pesquisa sobre desigualdades (Neila Pierote)

## � Autenticação JWT

Sistema completo de autenticação baseado em JWT tokens com segurança robusta.

### Endpoints da API

#### Autenticação (Públicos)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/users/api/register/` | Registrar novo usuário |
| POST | `/users/api/token/` | Login (obter access + refresh tokens) |
| POST | `/users/api/token/refresh/` | Refrescar access token |

#### Conta (Autenticados - Bearer Token)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/users/api/profile/` | Obter dados do perfil |
| PUT | `/users/api/profile/update/` | Atualizar perfil |
| POST | `/users/api/change-password/` | Trocar senha |
| GET | `/users/api/login-history/` | Histórico de login (IP, timestamp) |
| POST | `/users/api/logout/` | Fazer logout (revoga token) |
| POST | `/users/api/logout-all-devices/` | Logout em todos os dispositivos |

### Teste Rápido (cURL)

```bash
# 1. Registrar
curl -X POST http://localhost:8000/users/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username":"testuser",
    "email":"test@example.com",
    "password":"securepass123",
    "password_confirm":"securepass123"
  }'

# 2. Login
curl -X POST http://localhost:8000/users/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"securepass123"}'

# 3. Usar Token
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/users/api/profile/
```

### Segurança JWT

- ✅ **Access Token**: Válido por 1 hora
- ✅ **Refresh Token**: Válido por 7 dias com rotação automática
- ✅ **Blacklist de Tokens**: Revogação imediata ao logout
- ✅ **Rate Limiting**: 100 req/h (anônimo), 1000 req/h (autenticado)
- ✅ **Headers Seguros**: HSTS, X-Frame-Options, Content-Type-Options
- ✅ **Histórico de Login**: Rastreamento de IP e tentativas falhadas
- ✅ **Validação de Senha**: Mínimo 8 caracteres obrigatório

---

## �🛠️ Instalação

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

### 4. Testar Endpoints JWT
```bash
# Registrar novo usuário
curl -X POST http://localhost:8000/users/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user@example.com","password":"pass123","password_confirm":"pass123"}'

# Login e obter tokens
curl -X POST http://localhost:8000/users/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}'

# Usar token para acessar perfil
MY_TOKEN="eyJ0eXAiOi..." # Token obtido acima
curl -H "Authorization: Bearer $MY_TOKEN" http://localhost:8000/users/api/profile/

# Trocar senha
curl -X POST http://localhost:8000/users/api/change-password/ \
  -H "Authorization: Bearer $MY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"pass123","new_password":"newpass123","confirm_password":"newpass123"}'

# Ver histórico de login
curl -H "Authorization: Bearer $MY_TOKEN" \
  http://localhost:8000/users/api/login-history/

# Fazer logout
curl -X POST http://localhost:8000/users/api/logout/ \
  -H "Authorization: Bearer $MY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

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

### Melhorias Implementadas (v2.0)

#### 1️⃣ Tratamento de Negação
Evita **falsos positivos** quando HPV/lesão é negada:
- Detecta: "negativo para HPV", "ausência de lesão", "sem HSIL"
- Resultado: Entity revogada = Score 0
- Janela: Analisa 5 palavras antes da entidade

Exemplo:
```
❌ "DNA-HPV negativo para HPV 16" → BAIXO RISCO (score 0)
✅ "DNA-HPV positivo para HPV 16" → ALTO RISCO (score 3+)
```

#### 2️⃣ Matriz de Risco Refinada
Classificação baseada em **combinações clínicas**:
- **🔴 RED (10)**: HPV 16 + HSIL + Vulnerabilidade = Urgente
- **🟡 YELLOW (6-7)**: HPV alto risco + lesão moderada
- **🟢 GREEN (1-2)**: Negativo ou achados benignos

#### 3️⃣ Detecção de Persistência
Identifica **lesões crônicas** (risco aumentado):
- Padrões: "há 3 anos", "positivo em 2021 e 2024"
- Resultado: +2 pontos automáticos se > 2 anos
- Multiplica risco em idade > 30 anos

Exemplo:
```
Score base: 5
+ Persistência 3 anos: +2
= SCORE FINAL: 7 (YELLOW/Risco moderado-alto)
```

#### 4️⃣ EntityRuler com Gazetteers
**100% accuracy** para termos conhecidos (ANTES do modelo):
- **HPV**: 16, 18, 31, 33, 45, 52, 58 (20+ variações)
- **Lesões**: HSIL, LSIL, NIC I-III, Carcinoma (15+ variações)
- **Procedimentos**: CAF, Conização, LEEP, Histerectomia (10+)
- **Localizações**: 30+ bairros de Salvador + regiões (Nordeste, Norte)
- **Exames**: DNA-HPV, Citopatológico, Colposcopia, Ultrassom

Vantagem: Conhecimento clínico puro = sem incerteza estatística

#### 5️⃣ Extração de Idade
Múltiplos padrões de extração:
- "Paciente 35 anos"
- "Nascida em 1990"
- "Idade 42"

Impacto: Idade > 30 multiplica risco social (prognóstico pior)

### Dados de Treinamento Aumentados

- **Dataset original**: 120 exemplos
- **Dataset aumentado**: 200+ exemplos (+67%)
- **Cobertura**: 5 categorias de exemplos
  - Negação: "negativo", "sem HSIL", "desfrenhância"
  - Persistência: "há 3 anos", "crônico", "recorrente"
  - Variações regionais: Bairros de Salvador, Bahia
  - Exemplos complexos: Múltiplas entidades aninhadas
  - Textos ruidosos: Variações reais de relatórios médicos

---

## 🔄 Reclassificar Pacientes Existentes

```bash
# Simular reclassificação (dry-run)
python manage.py reclassificar_pacientes --dry-run

# Reclassificar todos os pacientes
python manage.py reclassificar_pacientes

# Reclassificar um paciente específico
python manage.py reclassificar_pacientes --paciente-id 1
```

## 🧪 Testes Automatizados

### Testar NER v2.0 (Melhorias)
```bash
# Suite completa de testes NER
python manage.py test_ner_improvements

# Com output verboso
python manage.py test_ner_improvements --verbose

# Modo rápido (testes essenciais)
python manage.py test_ner_improvements --quick
```

### Testar Endpoints JWT
```bash
# Suite completa de testes JWT (19 testes)
python manage.py test users.test_jwt --verbosity=2

# Testes específicos
python manage.py test users.test_jwt.JWTLoginTestCase
python manage.py test users.test_jwt.JWTSecurityTestCase
```

---

## 🤖 Sistema de Classificação Anterior



## 🧪 Testes Automatizados

### Testar NER v2.0 (Melhorias)
```bash
# Suite completa de testes NER
python manage.py test_ner_improvements

# Com output verboso
python manage.py test_ner_improvements --verbose

# Modo rápido (testes essenciais)
python manage.py test_ner_improvements --quick
```

### Testar Endpoints JWT
```bash
# Suite completa de testes JWT (19 testes)
python manage.py test users.test_jwt --verbosity=2

# Testes específicos
python manage.py test users.test_jwt.JWTLoginTestCase
python manage.py test users.test_jwt.JWTSecurityTestCase
```

---



## 📦 Dependências Principais

- **Django 5.2**: Framework web
- **spaCy 3.7+**: NER (único engine de classificação)
- **PyPDF2 3.0+**: Extração de texto de PDFs
- **djangorestframework>=3.14.0**: REST API
- **djangorestframework-simplejwt>=5.3.0**: JWT tokens
- **PyJWT>=2.8.0**: Validação de tokens
- **negspacy>=1.0.0**: Detecção de negação (v2.0)
- **python-dateutil>=2.8.0**: Parsing de datas (persistência)
- **regex>=2024.0.0**: Padrões regex robustos

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

**Última atualização**: Março de 2026

