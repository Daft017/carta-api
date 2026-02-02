"""
DOCUMENTAÇÃO TÉCNICA - CARTA CONTEMPLADA API
=============================================

Visão técnica profunda do sistema.
"""

# ============================================================================
# ARQUITETURA E DESIGN
# ============================================================================

"""
PADRÃO ARQUITETURAL: MVC Simplificado

┌─────────────────────────────────────────────────────────────┐
│                      MODELO (Data)                          │
│  Planilha Excel/CSV (Única fonte de verdade)                │
│  - Colunas: id, tipo, credito, parcela, entrada,            │
│             status, administradora, grupo                   │
└─────────────────────────────────────────────────────────────┘
                            ↓ Pandas lê
┌─────────────────────────────────────────────────────────────┐
│                    CONTROLLER (Backend)                      │
│  FastAPI + Uvicorn (http://localhost:8000)                  │
│  - Validação de dados                                       │
│  - Cache em memória (TTL 60s)                               │
│  - API REST JSON                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓ Fetch API
┌─────────────────────────────────────────────────────────────┐
│                    VISÃO (Frontend)                          │
│  HTML/CSS/JavaScript (http://localhost:8080)                │
│  - Renderização dinâmica                                    │
│  - Busca/Filtro em tempo real                               │
│  - Responsive design                                        │
└─────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# DECISÕES ARQUITETURAIS
# ============================================================================

"""
1. POR QUE PLANILHA COMO CMS?
   ✅ Acesso fácil e intuitivo (Excel/CSV familiar)
   ✅ Sem banco de dados (simplicidade máxima)
   ✅ Sem necessidade de UI complexa (painel admin)
   ✅ Versionamento com Git (backup natural)
   ✅ Compatível com ferramentas de BI

2. POR QUE FASTAPI?
   ✅ Framework moderno e rápido (async/await)
   ✅ Documentação automática (Swagger/OpenAPI)
   ✅ Type hints (segurança de tipos)
   ✅ Validação automática (Pydantic)
   ✅ Pronto para produção (ASGI compliant)

3. POR QUE CACHE EM MEMÓRIA?
   ✅ Performance (elimina I/O de disco)
   ✅ Simplicidade (sem Redis/Memcached)
   ✅ TTL automático (60s default)
   ✅ Invalidação manual (endpoint /reload-cache)
   ✅ Suficiente para MVP

4. POR QUE HTML/CSS/JS PURO?
   ✅ Zero dependências frontend
   ✅ Funciona offline (arquivo local)
   ✅ Download rápido
   ✅ Sem build/compilação
   ✅ Fácil customização
"""

# ============================================================================
# FLUXO DE DADOS
# ============================================================================

"""
LEITURA DE DADOS:

1. Inicialização (Startup)
   main.py → ler_planilha() → Pandas lê Excel/CSV
          → validar_colunas() → Verifica estrutura
          → validar_dados_linha() → Valida cada cota
          → cache.set() → Armazena em memória

2. Request da API
   GET /cotas → cache.is_valid()? 
             ├─ SIM (< 60s) → retorna cache.get()
             └─ NÃO (≥ 60s) → ler_planilha() → cache.set()

3. Modificação de Dados (Manual)
   Usuario edita Excel → salva
                      → Frontend click "Recarregar" (ou aguarda 60s)
                      → POST /reload-cache
                      → cache.clear() → ler_planilha() → cache.set()
                      → GET /cotas → retorna dados novos

FLUXO VISUAL:

┌─────────────────┐
│ Browser Request │ GET /cotas?status=disponivel
└────────┬────────┘
         │
         ↓
    ┌────────────────────────┐
    │ Cache válido? (< 60s)  │
    └────┬────────────────┬──┘
         │ SIM           │ NÃO
         ↓               ↓
    ┌────────┐    ┌──────────────────┐
    │ Hit    │    │ Miss: Ler Excel  │
    │(Rápido)│    │ + Validar + Cache│
    └────┬───┘    └────────┬─────────┘
         │                  │
         └────────┬─────────┘
                  ↓
         ┌────────────────┐
         │ Filter Status  │
         │ disponivel=1   │
         └────────┬───────┘
                  ↓
         ┌────────────────┐
         │ Return JSON    │
         └────────────────┘
"""

# ============================================================================
# ESTRUTURA DO CÓDIGO
# ============================================================================

"""
FILE: backend/main.py

├── IMPORTS
│   ├── pathlib (Path manipulation)
│   ├── datetime (Cache TTL)
│   ├── pandas (Excel/CSV reading)
│   └── fastapi (REST API)
│
├── CONFIGURAÇÃO
│   ├── DADOS_DIR (diretório de dados)
│   ├── ARQUIVO_PLANILHA (path do Excel/CSV)
│   ├── CACHE_DURATION_SECONDS (TTL)
│   └── COLUNAS_OBRIGATORIAS (schema)
│
├── MODELS (Pydantic)
│   ├── Cota (estrutura de uma cota)
│   └── ResponseCotas (resposta da API)
│
├── CACHE MANAGER
│   ├── is_valid() (TTL check)
│   ├── get() (retorna dados)
│   ├── set() (armazena dados)
│   └── clear() (limpa cache)
│
├── FUNÇÕES DE VALIDAÇÃO
│   ├── validar_colunas() (estrutura Excel)
│   ├── validar_dados_linha() (dados por linha)
│   └── ler_planilha() (orquestra leitura)
│
├── APP FASTAPI
│   ├── Middleware CORS
│   └── ENDPOINTS
│       ├── GET / (info)
│       ├── GET /cotas (lista com cache)
│       ├── GET /cotas/{id} (detalhe)
│       ├── POST /reload-cache (invalida)
│       └── GET /status (saúde)
│
└── MAIN (inicialização)
    ├── Print status
    ├── Carrega cache inicial
    └── Inicia Uvicorn
"""

# ============================================================================
# PERFORMANCE
# ============================================================================

"""
BENCHMARKS (Estimados com dados reais):

1. Primeira requisição (cold cache):
   ├─ Ler Excel: 50-200ms
   ├─ Validar: 10-50ms
   ├─ Criar objetos: 5-20ms
   ├─ Serializar JSON: 5-15ms
   └─ TOTAL: 70-285ms

2. Requisições subsequentes (hot cache):
   ├─ Hit cache: 1-5ms
   ├─ Filtrar: 1-5ms
   ├─ Serializar: 5-10ms
   └─ TOTAL: 7-20ms

3. Efeito de cache (1.000 cotas):
   ├─ Sem cache: 285ms × 60 req/min = 17.1s overhead/min
   ├─ Com cache: 15ms × 60 req/min = 0.9s overhead/min
   └─ Economia: 94% redução de latência

OTIMIZAÇÕES:

✅ Cache em memória (elimina I/O)
✅ Validação na leitura (não em cada request)
✅ Índices (busca por ID = O(n) → O(1) com dict se necessário)
✅ Compressão GZIP (automática via FastAPI)
✅ Async/await (non-blocking)

LIMITES RECOMENDADOS:

- Máximo de cotas: 10.000+ (antes de considerar otimizações)
- Máximo de requisições/min: 1.000+ (CPU bound)
- Tamanho Excel: 10MB+ (sem degradação)
"""

# ============================================================================
# VALIDAÇÃO DE DADOS
# ============================================================================

"""
REGRAS DE VALIDAÇÃO:

1. Colunas (validar_colunas)
   ├─ id ..................... OBRIGATÓRIO
   ├─ tipo ................... Obrigatório
   ├─ credito ................ Número (float)
   ├─ parcela ................ Inteiro
   ├─ entrada ................ Número (float)
   ├─ status ................. Enum: [disponivel, vendida]
   ├─ administradora ......... Texto
   └─ grupo .................. Texto

2. Valores por Linha (validar_dados_linha)
   ├─ ID não vazio
   ├─ Status válido (case-insensitive)
   ├─ Números parseáveis
   └─ Sem crash em valores NULL

3. Comportamento de Erro
   ├─ Coluna faltando → ValueError + HTTP 400
   ├─ Linha inválida → SKIP + log warning
   ├─ Arquivo não existe → FileNotFoundError + HTTP 404
   └─ Permissões → OSError + HTTP 500

EXEMPLOS DE DADOS VÁLIDOS:

✅ Números:
   250000, 250000.0, 250000.50, 25000,00 (pt-BR)

✅ Status:
   "disponivel", "DISPONIVEL", " disponivel "

✅ Valores NULL:
   Campos texto podem estar vazios, numéricos causam erro

❌ Valores inválidos:
   "disponivel$", "VEND1DA", números não parseáveis
"""

# ============================================================================
# ENDPOINTS E EXEMPLOS
# ============================================================================

"""
1. GET / (Raiz)

   Descrição: Informações gerais da API
   Autenticação: Não
   Cache: Não
   
   Resposta:
   {
     "aplicacao": "Carta Contemplada API",
     "versao": "1.0.0",
     "endpoints": {...}
   }

2. GET /cotas [PRINCIPAL]

   Descrição: Lista cotas (default: status=disponivel)
   Parâmetros:
     - status: "disponivel" | "vendida" (opcional)
   Cache: SIM (60s TTL)
   
   Query: GET /cotas
   Resposta:
   {
     "total": 6,
     "cotas": [
       {
         "id": "COT001",
         "tipo": "Imóvel",
         "credito": 250000.0,
         "parcela": 120,
         "entrada": 25000.0,
         "status": "disponivel",
         "administradora": "ABC Imóveis",
         "grupo": "Grupo A"
       },
       ...
     ],
     "timestamp": "2025-01-29T10:30:45.123456"
   }

3. GET /cotas/{id}

   Descrição: Detalhe de uma cota
   Parâmetros:
     - id: String (path)
   Cache: SIM (60s)
   
   Query: GET /cotas/COT001
   Resposta: {Cota object}
   Erro 404: Se ID não existe

4. POST /reload-cache

   Descrição: Força recarregamento de dados
   Body: Vazio
   Cache: Limpo e refeito
   
   Query: POST /reload-cache
   Resposta:
   {
     "status": "sucesso",
     "mensagem": "Cache recarregado",
     "total_cotas": 6,
     "timestamp": "..."
   }

5. GET /status

   Descrição: Status da API e cache
   Cache: Não
   
   Query: GET /status
   Resposta:
   {
     "status": "online",
     "cache": {
       "ativo": true,
       "duracao_segundos": 60,
       "ultima_atualizacao": "...",
       "tempo_restante_segundos": 45
     },
     "arquivo_dados": "...",
     "arquivo_existe": true
   }

6. GET /docs

   Descrição: Documentação Swagger interativa
   Auto-gerada: SIM (por FastAPI)
   URL: http://localhost:8000/docs
"""

# ============================================================================
# CÓDIGOS DE ERRO
# ============================================================================

"""
HTTP STATUS CODES:

200 OK
   └─ Request bem-sucedido
      GET /cotas → lista de cotas
      GET /cotas/COT001 → detalhe
      GET /status → informações
      POST /reload-cache → sucesso

400 BAD REQUEST
   └─ Erro de validação nos dados
      └─ Colunas obrigatórias faltando na planilha
      └─ Formato de dados inválido

404 NOT FOUND
   └─ Recurso não encontrado
      └─ GET /cotas/INEXISTENTE → cota não existe
      └─ Arquivo de dados não existe

500 INTERNAL SERVER ERROR
   └─ Erro no servidor
      └─ Erro ao ler arquivo (permissões)
      └─ Erro ao processar Excel/CSV
      └─ Erro não previsto

TRATAMENTO DE ERRO FRONTEND:

try {
  const response = await fetch(`${API_BASE_URL}/cotas`);
  
  if (!response.ok) {
    if (response.status === 404) {
      // Arquivo não encontrado
    } else if (response.status === 400) {
      // Dados inválidos na planilha
    } else if (response.status === 500) {
      // Erro do servidor
    }
  }
  
  const data = await response.json();
} catch (erro) {
  // Conexão falhou (servidor não está rodando)
}
"""

# ============================================================================
# EXTENSÕES E CUSTOMIZAÇÕES
# ============================================================================

"""
Como estender o sistema:

1. ADICIONAR COLUNA NA PLANILHA
   ├─ Adicione coluna "observacoes" no Excel
   ├─ Adicione em COLUNAS_OBRIGATORIAS (ou deixe opcional)
   ├─ Adicione campo em class Cota (Pydantic)
   ├─ Adicione em validar_dados_linha() se necessário
   └─ Recarregue a API

2. ADICIONAR FILTRO
   ├─ Frontend: No JavaScript, adicione outro campo input
   ├─ Backend: Adicione parâmetro a GET /cotas
   ├─ Filtre em Python: cotas_filtradas = [c for c in cotas if ...]
   └─ Retorne resposta

3. AUTENTICAÇÃO (se necessário)
   ├─ Adicione FastAPI security (JWT)
   ├─ Proteja endpoints com @app.get(..., dependencies=[Depends(...)])
   ├─ No frontend: Adicione header Authorization ao fetch

4. INTEGRAÇÃO COM BD
   ├─ Mantendo CSV como "export":
   ├─ Adicione SQLAlchemy + PostgreSQL
   ├─ Na leitura, sincronize: CSV → DB
   ├─ Retorne dados do DB
   └─ Mantém planilha como backup

5. NOTIFICAÇÕES EM TEMPO REAL
   ├─ Substitua HTTP polling por WebSocket
   ├─ Dentro de ler_planilha(), broadcast changes
   ├─ No frontend, setup ws://localhost:8000/ws
   └─ Atualiza automaticamente quando planilha muda
"""

# ============================================================================
# TROUBLESHOOTING TÉCNICO
# ============================================================================

"""
PROBLEMA: "ModuleNotFoundError: No module named 'pandas'"

Causa: Dependências não instaladas
Solução:
  $ pip install -r backend/requirements.txt

---

PROBLEMA: "FileNotFoundError: dados/cotas.xlsx"

Causa: Arquivo não existe
Solução:
  $ python backend/criar_exemplo_cotas.py
  
  Ou copie seu arquivo para dados/cotas.xlsx

---

PROBLEMA: "Colunas obrigatórias faltando"

Causa: Excel tem nomes de colunas diferentes
Verificar:
  - Nomes exatos: id, tipo, credito, parcela, entrada, status, administradora, grupo
  - Minúsculas (não "ID" ou "ID ")
  - Sem espaços extras

---

PROBLEMA: "Status inválido para COT001: ativado"

Causa: Valor de status não é "disponivel" ou "vendida"
Solução:
  - Edite Excel, corrija para "disponivel" ou "vendida"
  - Case-insensitive, mas deve ser exato

---

PROBLEMA: "API conectando, depois retorna erro"

Causa: Arquivo Excel está aberto em outro programa
Solução:
  - Feche Excel antes de rodar a API
  - Pandas tem dificuldade em ler arquivo locked

---

PROBLEMA: "Mudei Excel mas site não atualizou"

Causa: Cache ainda válido (< 60s)
Solução 1: Aguarde 60 segundos
Solução 2: Clique "Recarregar" no site
Solução 3: Reduzir CACHE_DURATION_SECONDS em main.py
"""

# ============================================================================
# DEPLOYMENT
# ============================================================================

"""
PRODUÇÃO - RECOMENDAÇÕES:

1. HOSPEDAGEM (Opções)
   a) Heroku (grátis com limitações)
   b) PythonAnywhere (hosting Python)
   c) AWS Lambda (serverless)
   d) DigitalOcean (VPS $4-6/mês)
   e) Render.com (alternativa Heroku)

2. SERVIDOR WEB
   ❌ Não usar: python main.py (development only)
   ✅ Usar: gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app

3. VARIÁVEIS DE AMBIENTE
   - DADOS_DIR=/var/data
   - CACHE_DURATION=120
   - ARQUIVO_PLANILHA=/var/data/cotas.xlsx

4. MONITORAMENTO
   - Logs (stdout → /var/log/app.log)
   - Métricas (Prometheus opcional)
   - Alertas (Datadog, New Relic)

5. BACKUP
   - Git: versione cotas.xlsx
   - Cloud: S3, Google Drive, Dropbox
   - Scheduler: commit automático a cada alteração

6. SSL/HTTPS
   - Usar reverse proxy (Nginx)
   - Certificado Let's Encrypt (grátis)

7. FIREWALL
   - POST /reload-cache: Proteger com secretkey
   - GET /docs: Desabilitar em produção

EXEMPLO docker-compose.yml:

version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./dados:/app/dados
    environment:
      - CACHE_DURATION=120
    command: gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
"""

print(__doc__)
