# 🏠 Carta Contemplada API

Uma solução elegante e simples para gerenciar cotas contempladas usando uma planilha como CMS.

**Arquitetura:** Planilha (Excel/CSV) → Backend Python (FastAPI) → Frontend (HTML/CSS/JS)

## 🎯 Visão Geral

Este projeto implementa um site dinâmico de cotas contempladas sem necessidade de banco de dados ou painel administrativo tradicional. A planilha Excel/CSV é o único "painel de administração" do sistema:

- ✅ Adiciona, remove ou edita cotas diretamente na planilha
- ✅ Backend Python automáticamente valida e expõe os dados via API REST
- ✅ Frontend consome a API e renderiza as cotas em tempo real
- ✅ Cache inteligente para otimizar performance
- ✅ Filtro automático para mostrar apenas cotas disponíveis

## 📋 Estrutura do Projeto

```
Carta contemplada API/
├── backend/
│   ├── main.py                      # Aplicação FastAPI (núcleo do projeto)
│   ├── criar_exemplo_cotas.py       # Script para gerar dados de teste
│   └── requirements.txt             # Dependências Python
│
├── frontend/
│   └── index.html                   # Site completo (HTML + CSS + JS)
│
├── dados/
│   └── cotas.xlsx                   # Planilha de dados (gerada automaticamente)
│
└── README.md                        # Este arquivo
```

## 🚀 Quick Start (5 minutos)

### Pré-requisitos

- Python 3.9+
- pip (gerenciador de pacotes Python)

### Passo 1: Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### Passo 2: Criar Arquivo de Exemplo (Opcional)

```bash
python criar_exemplo_cotas.py
```

Este comando cria um arquivo `cotas.xlsx` em `../dados/` com 8 cotas de exemplo.

Se preferir usar um arquivo existente, copie seu arquivo `.xlsx` ou `.csv` para a pasta `dados/` e nomeie como `cotas.xlsx`.

### Passo 3: Iniciar Backend

```bash
python main.py
```

Você verá algo assim:
```
======================================================================
🚀 Carta Contemplada API - Iniciando...
======================================================================
📁 Diretório de dados: C:\...\dados
📄 Planilha esperada: C:\...\dados\cotas.xlsx
⏱️  Cache: 60 segundos
======================================================================
✅ Lidas 6 cotas válidas da planilha
✅ Inicialização bem-sucedida com 6 cotas
======================================================================
📍 API rodando em: http://localhost:8000
📚 Documentação: http://localhost:8000/docs
======================================================================
```

### Passo 4: Acessar Frontend

Abra seu navegador e acesse:
- **Site:** http://localhost:8000/index.html ❌ (CORS issue)
- **Correto:** Abra o arquivo `frontend/index.html` diretamente no navegador

Ou use um servidor HTTP simples:

```bash
# Python 3
cd frontend
python -m http.server 8080

# Depois acesse: http://localhost:8080
```

## 📊 Modelo da Planilha

Crie um arquivo Excel/CSV com as seguintes colunas (ordem não importa):

| id | tipo | credito | parcela | entrada | status | administradora | grupo |
|---|---|---|---|---|---|---|---|
| COT001 | Imóvel | 250000 | 120 | 25000 | disponivel | ABC Imóveis | Grupo A |
| COT002 | Imóvel | 300000 | 180 | 30000 | disponivel | XYZ Crédito | Grupo B |
| COT003 | Imóvel | 180000 | 84 | 18000 | vendida | ABC Imóveis | Grupo A |

### Regras de Validação

- ✅ **id**: Obrigatório, identificador único da cota
- ✅ **tipo**: Tipo de bem (Imóvel, Veículo, etc)
- ✅ **credito**: Valor numérico do crédito
- ✅ **parcela**: Número de parcelas (inteiro)
- ✅ **entrada**: Valor da entrada (numérico)
- ✅ **status**: Apenas "disponivel" ou "vendida"
- ✅ **administradora**: Nome da administradora
- ✅ **grupo**: Grupo ou categoria da cota

### Comportamento

- Cotas com status = `"vendida"` **NÃO aparecem** no site
- Se uma linha for **apagada**, a cota some do site
- Se um valor for **alterado**, o site reflete automaticamente após reload
- Valores monetários aceitam pontos ou vírgulas como separador decimal

## 🔌 API REST

### Endpoints Disponíveis

#### 1. Listar Cotas Disponíveis (Padrão)
```
GET /cotas
```

Retorna todas as cotas com status = "disponivel"

**Resposta:**
```json
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
    }
  ],
  "timestamp": "2025-01-29T10:30:45.123456"
}
```

#### 2. Filtrar por Status
```
GET /cotas?status=vendida
```

Retorna cotas vendidas:
```json
{
  "total": 2,
  "cotas": [...]
}
```

#### 3. Obter Cota por ID
```
GET /cotas/{id}
```

Exemplo: `GET /cotas/COT001`

**Resposta:**
```json
{
  "id": "COT001",
  "tipo": "Imóvel",
  "credito": 250000.0,
  "parcela": 120,
  "entrada": 25000.0,
  "status": "disponivel",
  "administradora": "ABC Imóveis",
  "grupo": "Grupo A"
}
```

#### 4. Recarregar Cache
```
POST /reload-cache
```

Force a leitura da planilha novamente (útil após editar a planilha).

**Resposta:**
```json
{
  "status": "sucesso",
  "mensagem": "Cache recarregado",
  "total_cotas": 6,
  "timestamp": "2025-01-29T10:30:45.123456"
}
```

#### 5. Status da API
```
GET /status
```

Informações sobre cache e saúde da API.

**Resposta:**
```json
{
  "status": "online",
  "cache": {
    "ativo": true,
    "duracao_segundos": 60,
    "ultima_atualizacao": "2025-01-29T10:30:45.123456",
    "tempo_restante_segundos": 45
  },
  "arquivo_dados": "C:\\...\\dados\\cotas.xlsx",
  "arquivo_existe": true,
  "timestamp": "2025-01-29T10:30:45.123456"
}
```

#### 6. Documentação Interativa (Swagger)
```
GET /docs
```

Acesse `http://localhost:8000/docs` para testar todos os endpoints interativamente.

## 🔄 Fluxo de Funcionamento

```
┌─────────────────────────┐
│   Planilha (Excel/CSV)  │
│  (CMS do Sistema)       │
└────────────┬────────────┘
             │
             │ Backend lê a cada 60s
             ↓
┌─────────────────────────┐
│  Backend FastAPI        │
│  - Valida dados         │
│  - Cache simples        │
│  - API REST JSON        │
└────────────┬────────────┘
             │
             │ Fetch API (JavaScript)
             ↓
┌─────────────────────────┐
│  Frontend (Browser)     │
│  - HTML + CSS + JS      │
│  - Renderiza cotas      │
│  - Busca/Filtro         │
└─────────────────────────┘
```

## 🔒 Segurança

- ✅ Sem banco de dados
- ✅ Sem escrita de dados via API
- ✅ Sem autenticação necessária (dados são públicos)
- ✅ Validação de entrada no backend
- ✅ CORS habilitado (modifique em produção)

## ⚙️ Configuração Avançada

### Mudar Duração do Cache

Edite `backend/main.py`:

```python
# Linha ~30
CACHE_DURATION_SECONDS = 120  # Padrão: 60 segundos
```

### Usar CSV em vez de Excel

Edite `backend/main.py`:

```python
# Linha ~32
ARQUIVO_PLANILHA = DADOS_DIR / "cotas.csv"  # Mude para .csv
```

### Habilitar Auto-reload do Backend

Já está habilitado por padrão. O backend reinicia automaticamente quando você salva mudanças em `main.py`.

### Desabilitar em Produção

Em `main.py`, mude:

```python
uvicorn.run(
    "main:app",
    reload=False,  # Desabilitar em produção
)
```

## 🐛 Troubleshooting

### "Planilha não encontrada"

**Problema:** API retorna erro 404 ao iniciar.

**Solução:**
1. Execute `python criar_exemplo_cotas.py` para gerar exemplo
2. Ou copie seu arquivo `.xlsx` para `dados/cotas.xlsx`

### "Colunas obrigatórias faltando"

**Problema:** Erro na leitura da planilha.

**Solução:**
- Verifique se sua planilha tem exatamente estas colunas:
  - id, tipo, credito, parcela, entrada, status, administradora, grupo
- Nomes devem estar em **minúsculas exatas**

### "Conexão recusada" no Frontend

**Problema:** Frontend não consegue conectar com backend.

**Solução:**
1. Verifique se backend está rodando: `http://localhost:8000/status`
2. Abra frontend como arquivo local (não via servidor) ou via HTTP server
3. Se usar servidor externo, ajuste `API_BASE_URL` no HTML

### "CORS error"

**Problema:** Erro de CORS ao fazer requisições.

**Solução:**
- Em produção, mude em `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],  # Especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 Performance

### Cache

O backend implementa cache simples em memória com **TTL de 60 segundos**:

- Primeira requisição: lê a planilha (lenta ~100-500ms)
- Próximas 59s: retorna do cache (muito rápida ~1-5ms)
- Após 60s: lê novamente

### Otimizações

- ✅ Cache simples em memória
- ✅ Validação apenas na leitura
- ✅ Sem queries em banco de dados
- ✅ Compressão GZIP automática (FastAPI)

## 🚢 Deploy em Produção

### Opção 1: Heroku (Grátis)

```bash
# 1. Criar account em heroku.com
# 2. Instalar Heroku CLI
# 3. Criar arquivo Procfile na raiz:
echo "web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile

# 4. Deploy
heroku login
heroku create seu-app
git push heroku main
```

### Opção 2: PythonAnywhere (Grátis)

1. Crie conta em pythonanywhere.com
2. Upload dos arquivos via Web Console
3. Configure Web app pointing para `main.py`

### Opção 3: VPS (Recomendado)

```bash
# No servidor
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Usar Gunicorn em produção
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
```

## 📝 Exemplos de Uso

### Adicionar Nova Cota

1. Abra `dados/cotas.xlsx`
2. Adicione uma nova linha:

| COT010 | Imóvel | 500000 | 240 | 50000 | disponivel | Premium | Grupo D |

3. Salve o arquivo
4. No site, clique "↻ Recarregar" ou aguarde 60s para o cache expirar

### Marcar Cota como Vendida

1. Abra `dados/cotas.xlsx`
2. Mude `status` de uma cota de "disponivel" para "vendida"
3. Salve - cota desaparece automaticamente do site

### Editar Valor de Crédito

1. Abra `dados/cotas.xlsx`
2. Mude o valor em `credito`
3. Salve - novo valor aparece no site após reload ou 60s

## 📚 Referências Úteis

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Pandas Docs:** https://pandas.pydata.org/
- **Fetch API:** https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

## 📄 Licença

MIT - Libre para usar e modificar.

---

**Desenvolvido com ❤️ como MVP pronto para produção.**

**Dúvidas?** Verifique os logs do console do backend ou do browser para mais detalhes.
