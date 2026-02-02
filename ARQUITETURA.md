# 🏗️ DIAGRAMAS E ARQUITETURA - Carta Contemplada API

## Arquitetura Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUÁRIO FINAL                            │
│                      (Navegador Web)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    Frontend carrega
                      (HTML/CSS/JS)
                           │
       ┌───────────────────┴───────────────────┐
       │                                       │
   JavaScript                          Event Listeners
   fetch()                             (busca, filtro)
       │                                       │
       └──────────────┬──────────────────────┘
                      │
                   HTTP/REST
              (Fetch API in JS)
                      │
       ┌──────────────┴──────────────┐
       │                             │
   GET /cotas                    POST /reload-cache
   GET /cotas/{id}               GET /status
   GET /cotas?status=...         GET /docs
       │                             │
       └──────────────┬──────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
     FastAPI                   FastAPI
    (Backend)              (Server Process)
         │                         │
    ┌────┴─────┬──────────┬───────┴────┐
    │           │          │             │
 Validação  Cache      Logging       Error
  Pydantic  Manager    stdout      Handling
    │           │          │             │
    └────┬──────┴──────────┴──────┬─────┘
         │                        │
      Pandas                 Return JSON
      (Read)                 (Response)
         │                        │
      ┌──┴────────────────────────┴──┐
      │                               │
   Excel/CSV File                     │
   (Planilha - CMS)                   │
      │                               │
      └───────────────────────────────┘
```

## Fluxo de Requisição (GET /cotas)

```
1. Cliente (Browser)
   │
   └─> Clica em "Buscar" ou página carrega
       │
       └─> JavaScript: fetch('http://localhost:8000/cotas')
           │
           └─> HTTP Request: GET /cotas
               │
               ┌───────────────┴──────────────┐
               │                              │
           FastAPI                        Middleware CORS
           Recebe request                 Processa headers
               │                              │
               └──────────────┬───────────────┘
                              │
                    CacheManager.is_valid()?
                              │
                    ┌─────────┴─────────┐
                    │ SIM (< 60s)       │ NÃO (≥ 60s)
                    │                   │
                 return cache       ler_planilha()
                 (muito rápido)        │
                    │              ┌───┴─────────┐
                    │              │              │
                    │          Pandas          validar_
                    │         read Excel       colunas
                    │              │              │
                    │          Parse         validar_
                    │            dados       dados_linha
                    │              │              │
                    │          Loop linhas       │
                    │          Validar each      │
                    │              │              │
                    │          Skip invalid      │
                    │          Create Cota      │
                    │          List[]            │
                    │              │              │
                    │          cache.set()       │
                    │              │              │
                    └──────────┬───┘              │
                               │                  │
                    Filter status=disponivel
                               │
                    ┌──────────┴──────────┐
                    │                     │
                 Build response      Serialize JSON
                 ResponseCotas        Pydantic model
                    │                     │
                    └──────────┬──────────┘
                               │
                        HTTP Response 200
                   { "total": 6, "cotas": [...] }
                               │
                    ┌──────────┴──────────┐
                    │                     │
                Network                JS parse
                Transport          JSON.parse()
                    │                     │
                    └──────────┬──────────┘
                               │
                        Frontend Render
                        HTML Cards
                               │
                     Display para usuário
```

## Estrutura de Cache

```
┌─────────────────────────────────────────┐
│         CacheManager (em memória)       │
├─────────────────────────────────────────┤
│                                         │
│  data: List[Cota] = None               │
│  last_update: datetime = None           │
│  duration_seconds: int = 60             │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  is_valid()                             │
│  ├─ if data is None: return False       │
│  ├─ elapsed = now() - last_update       │
│  └─ return elapsed < duration           │
│                                         │
│  get()                                  │
│  ├─ if is_valid(): return data          │
│  └─ else: return None                   │
│                                         │
│  set(data)                              │
│  ├─ self.data = data                    │
│  └─ self.last_update = now()            │
│                                         │
│  clear()                                │
│  ├─ self.data = None                    │
│  └─ self.last_update = None             │
│                                         │
└─────────────────────────────────────────┘


         Timeline de Cache (exemplo)

t=0s:   Request 1 → Ler Excel (200ms) → Cache.set()
        ├─ Cache ativo: SIM (0s/60s)
        └─ Duration: 60s

t=10s:  Request 2 → Cache.get() (2ms) ← Cache HIT
        ├─ Cache ativo: SIM (10s/60s)
        └─ Tempo restante: 50s

t=30s:  Request 3 → Cache.get() (2ms) ← Cache HIT
        ├─ Cache ativo: SIM (30s/60s)
        └─ Tempo restante: 30s

t=60s:  Cache expira! ❌

t=61s:  Request 4 → Ler Excel novamente (200ms) ← Cache MISS
        ├─ Cache ativo: SIM (0s/60s)
        └─ Novo ciclo começa
```

## Estrutura de Validação de Dados

```
ler_planilha()
│
├─ 1. Verifica arquivo existe
│
├─ 2. Pandas read file
│  ├─ .xlsx → pd.read_excel()
│  └─ .csv  → pd.read_csv()
│
├─ 3. validar_colunas()
│  │
│  └─ Verifica se todas colunas obrigatórias existem:
│     id, tipo, credito, parcela, entrada, 
│     status, administradora, grupo
│  
│  └─ Se falta coluna → ValueError 400
│
├─ 4. Loop por cada linha
│  │
│  ├─ validar_dados_linha(row)
│  │  ├─ ID não vazio? ✓
│  │  ├─ Status válido? ✓ (disponivel/vendida)
│  │  ├─ Números parseáveis? ✓
│  │  └─ Sem erros → True
│  │     Com erros → False + mensagem
│  │
│  ├─ Se válido:
│  │  └─ Create Cota(pydantic model)
│  │     └─ Validate tipos (str, float, int)
│  │        └─ Add to List
│  │
│  └─ Se inválido:
│     └─ Log warning (linha N, motivo)
│        └─ Skip linha (continua)
│
└─ Return List[Cota]
   └─ Cache.set()
```

## Integração Frontend-Backend

```
FRONTEND                           BACKEND
────────────────────────────────────────────────────────

index.html
(carrega)
  │
  ├─ DOM pronto
  ├─ Event listeners attached
  ├─ carregarCotas() chamada
  │   │
  │   └─> fetch('/cotas')
  │       │
  │       HTTP GET ────────────────> FastAPI app
  │       │                          │
  │       │                      ler_planilha()
  │       │                      validar dados
  │       │                      filter status
  │       │                      <── Retorna JSON
  │       │
  │   <─────────────────────────
  │       │
  │   Recebe JSON
  │   JSON.parse()
  │   │
  │   ├─> renderizarCotas()
  │   │   ├─ Clear DOM
  │   │   ├─ Loop cotas
  │   │   ├─ Create card HTML
  │   │   └─ Inject in page
  │   │
  │   └─> atualizarStatus()
  │       └─ Fetch /status
  │           └─ Update footer
  │
  ├─ User vê cotas
  │
  └─ Event: User digita busca
      │
      ├─> filtrarCotas()
      │   ├─ Get input value
      │   ├─ Filter local array
      │   └─ renderizarCotas() novamente
      │
      └─ Resultado em tempo real (0 delay)


FLUXO DE EDIÇÃO:
  │
  └─ User edita planilha
     │
     ├─ Fecha Excel
     │
     ├─ User vê site
     │
     ├─ Clica "↻ Recarregar"
     │
     └─> fetch('/reload-cache', {POST})
         │
         ├────────────────────> Cache.clear()
         │                      ler_planilha()
         │                      Ler Excel novo
         │                      Cache.set()
         │
         <────────────────────
         │
         ├─ Recebe response
         │
         └─> carregarCotas()
             └─> renderizarCotas()
                 └─ Novos dados aparecem!
```

## Estados da Aplicação

```
ESTADO 1: Inicialização
  Backend inicia
  ├─ Tenta ler planilha
  ├─ Se sucesso: Cache.set()
  │            └─ Status: READY ✓
  └─ Se erro:    ERRO! 
                └─ Frontend mostra mensagem


ESTADO 2: Operação Normal
  Cache válido (< 60s)
  ├─ Request → return cache (2ms)
  ├─ HIT rate: 98%+
  └─ Performance: Ótima


ESTADO 3: Cache Expirando
  Cache válido (próximo a 60s)
  ├─ Request → return cache (2ms)
  ├─ Próxima request fará reload
  └─ TTL: ~5-10s


ESTADO 4: Cache Expirado
  Cache inválido (≥ 60s)
  ├─ Request → Ler planilha (200ms)
  ├─ Validação completa
  ├─ Cache.set() novo
  └─ HIT rate: volta alta


ESTADO 5: Erro
  Planilha não encontrada / inválida
  ├─ Frontend: Mensagem de erro
  ├─ Backend: Log detalhado
  ├─ HTTP: 400 ou 404
  └─ User: Ação corretiva necessária


ESTADO 6: Recarregar Manual
  User clica "↻ Recarregar"
  ├─ POST /reload-cache
  ├─ Cache.clear() force
  ├─ ler_planilha() novo
  ├─ Cache.set() atualizado
  ├─ Response: {"status": "sucesso"}
  └─ Frontend: Recarrega automaticamente
```

## Deployment: Produção vs Desenvolvimento

```
DESENVOLVIMENTO
  │
  ├─ python main.py
  │   └─ Uvicorn com reload=True
  │       ├─ Auto-reload on file change
  │       ├─ Debug info verboso
  │       └─ Hot reload rápido
  │
  ├─ Frontend: Arquivo local (index.html)
  │   └─ Sem servidor, open browser
  │
  └─ Dados: ./dados/cotas.xlsx
      └─ Local file


PRODUÇÃO
  │
  ├─ gunicorn -w 4 main:app
  │   └─ Múltiplos workers
  │       ├─ Load balancing
  │       ├─ Produção-ready
  │       └─ reload=False
  │
  ├─ Frontend: Nginx estático
  │   └─ Servir /frontend via HTTP
  │       ├─ Cache headers
  │       └─ Compressão GZIP
  │
  ├─ Dados: /var/data/cotas.xlsx
  │   └─ Sincronizado (Git/Cloud)
  │
  ├─ Reverse proxy: Nginx
  │   ├─ HTTPS/SSL
  │   ├─ Rate limiting
  │   └─ Logging
  │
  ├─ Monitoramento:
  │   ├─ Uptime checker
  │   ├─ Error logging
  │   └─ Metrics (opcional)
  │
  └─ Backup:
      ├─ Git repository
      ├─ Cloud sync
      └─ Scheduler automático
```

## Escalabilidade: Aumentar performance

```
PASSO 1: Cache atual (60s TTL)
  ├─ Capacidade: ~1.000 cotas
  ├─ Throughput: 100+ req/s
  ├─ Latência P95: <20ms
  └─ Memória: ~10MB

PASSO 2: Aumentar TTL
  ├─ Cache: 300s (5 minutos)
  ├─ HIT rate: 99%+
  ├─ Freshness: Sacrificada
  └─ Recomendado: Se dados mudam < 1x/dia

PASSO 3: Redis
  ├─ Cache distribuído
  ├─ Múltiplos workers
  ├─ TTL gerenciado
  └─ Produção: Altamente recomendado

PASSO 4: Database
  ├─ PostgreSQL + SQLAlchemy
  ├─ Índices em id, status, grupo
  ├─ Query optimization
  └─ Para 10.000+ cotas

PASSO 5: CDN
  ├─ Frontend: Cloudflare, AWS CloudFront
  ├─ API: Não é cacheable (realtime)
  └─ Latência global: Reduzida drasticamente
```

## Ciclo de Deploy

```
1. DESENVOLVIMENTO
   git commit → local testing

2. STAGING
   git push → deploy test server
            → test endpoints
            → test UI
            → test data

3. PRODUÇÃO
   git push → deploy main
            → backend restart
            → health check
            → monitor logs

4. ROLLBACK (se necessário)
   git revert → redeploy
             → verificar


[Tempo: ~5 minutos]
```

---

**Veja estes diagramas em visão real visitando `/docs` (Swagger) ou `/status` (Health Check)**
