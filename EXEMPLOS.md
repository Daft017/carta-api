# 📖 EXEMPLOS DE USO - Carta Contemplada API

## Exemplo 1: Listar Todas as Cotas Disponíveis

### URL
```
GET http://localhost:8000/cotas
```

### cURL
```bash
curl -X GET "http://localhost:8000/cotas" \
  -H "accept: application/json"
```

### JavaScript
```javascript
fetch('http://localhost:8000/cotas')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Erro:', error));
```

### Resposta (200 OK)
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
    },
    {
      "id": "COT002",
      "tipo": "Imóvel",
      "credito": 300000.0,
      "parcela": 180,
      "entrada": 30000.0,
      "status": "disponivel",
      "administradora": "XYZ Crédito",
      "grupo": "Grupo B"
    }
  ],
  "timestamp": "2025-01-29T10:30:45.123456"
}
```

---

## Exemplo 2: Buscar Cotas Vendidas

### URL
```
GET http://localhost:8000/cotas?status=vendida
```

### cURL
```bash
curl -X GET "http://localhost:8000/cotas?status=vendida" \
  -H "accept: application/json"
```

### Python (requests)
```python
import requests

response = requests.get('http://localhost:8000/cotas', params={'status': 'vendida'})
data = response.json()
print(f"Total de cotas vendidas: {data['total']}")

for cota in data['cotas']:
    print(f"- {cota['id']}: {cota['tipo']} ({cota['administradora']})")
```

### Resposta
```json
{
  "total": 2,
  "cotas": [
    {
      "id": "COT003",
      "tipo": "Imóvel",
      "credito": 180000.0,
      "parcela": 84,
      "entrada": 18000.0,
      "status": "vendida",
      "administradora": "ABC Imóveis",
      "grupo": "Grupo A"
    }
  ],
  "timestamp": "2025-01-29T10:30:45.123456"
}
```

---

## Exemplo 3: Obter Detalhe de Uma Cota

### URL
```
GET http://localhost:8000/cotas/COT001
```

### cURL
```bash
curl -X GET "http://localhost:8000/cotas/COT001" \
  -H "accept: application/json"
```

### JavaScript
```javascript
async function obterCota(id) {
  try {
    const response = await fetch(`http://localhost:8000/cotas/${id}`);
    
    if (!response.ok) {
      throw new Error(`Cota ${id} não encontrada`);
    }
    
    const cota = await response.json();
    console.log('Cota encontrada:', cota);
    return cota;
  } catch (error) {
    console.error(error);
  }
}

obterCota('COT001');
```

### Resposta
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

### Erro 404
```json
{
  "detail": "Cota com ID 'INEXISTENTE' não encontrada"
}
```

---

## Exemplo 4: Recarregar Cache

### URL
```
POST http://localhost:8000/reload-cache
```

### cURL
```bash
curl -X POST "http://localhost:8000/reload-cache" \
  -H "accept: application/json"
```

### JavaScript
```javascript
async function recarregarCache() {
  try {
    const response = await fetch('http://localhost:8000/reload-cache', {
      method: 'POST'
    });
    
    const data = await response.json();
    console.log(`Cache recarregado com ${data.total_cotas} cotas`);
  } catch (error) {
    console.error('Erro ao recarregar:', error);
  }
}

recarregarCache();
```

### Python
```python
import requests

response = requests.post('http://localhost:8000/reload-cache')
data = response.json()

print(f"Status: {data['status']}")
print(f"Total de cotas: {data['total_cotas']}")
print(f"Atualizado em: {data['timestamp']}")
```

### Resposta
```json
{
  "status": "sucesso",
  "mensagem": "Cache recarregado",
  "total_cotas": 6,
  "timestamp": "2025-01-29T10:30:45.123456"
}
```

---

## Exemplo 5: Verificar Status da API

### URL
```
GET http://localhost:8000/status
```

### cURL
```bash
curl -X GET "http://localhost:8000/status" \
  -H "accept: application/json"
```

### JavaScript
```javascript
async function verificarStatus() {
  try {
    const response = await fetch('http://localhost:8000/status');
    const status = await response.json();
    
    console.log('Status da API:', status.status);
    console.log('Cache ativo:', status.cache.ativo);
    console.log('Tempo restante:', status.cache.tempo_restante_segundos, 's');
  } catch (error) {
    console.error('API indisponível:', error);
  }
}

verificarStatus();
```

### Resposta
```json
{
  "status": "online",
  "cache": {
    "ativo": true,
    "duracao_segundos": 60,
    "ultima_atualizacao": "2025-01-29T10:30:00.000000",
    "tempo_restante_segundos": 45
  },
  "arquivo_dados": "C:\\...\\dados\\cotas.xlsx",
  "arquivo_existe": true,
  "timestamp": "2025-01-29T10:30:45.123456"
}
```

---

## Exemplo 6: Filtrar por Administradora (Frontend)

### HTML/JavaScript
```html
<input type="text" id="adminFilter" placeholder="Buscar administradora...">

<script>
document.getElementById('adminFilter').addEventListener('keyup', function() {
  const termo = this.value.toLowerCase();
  
  fetch('http://localhost:8000/cotas')
    .then(res => res.json())
    .then(data => {
      const cotasFiltradas = data.cotas.filter(cota =>
        cota.administradora.toLowerCase().includes(termo)
      );
      
      console.log(`Encontradas ${cotasFiltradas.length} cotas`);
      cotasFiltradas.forEach(cota => {
        console.log(`- ${cota.id}: ${cota.administradora}`);
      });
    });
});
</script>
```

---

## Exemplo 7: Calcular Totais e Estatísticas

### JavaScript
```javascript
async function obterEstatisticas() {
  const response = await fetch('http://localhost:8000/cotas');
  const { cotas } = await response.json();
  
  const totalCredito = cotas.reduce((sum, c) => sum + c.credito, 0);
  const totalEntrada = cotas.reduce((sum, c) => sum + c.entrada, 0);
  const media = totalCredito / cotas.length;
  
  console.log(`
    📊 ESTATÍSTICAS
    ================
    Total de cotas: ${cotas.length}
    Crédito total: R$ ${totalCredito.toLocaleString('pt-BR')}
    Entrada total: R$ ${totalEntrada.toLocaleString('pt-BR')}
    Média de crédito: R$ ${media.toLocaleString('pt-BR')}
  `);
}

obterEstatisticas();
```

---

## Exemplo 8: Monitorar Alterações (Polling)

### JavaScript
```javascript
// Verifica a cada 30 segundos se há mudanças
let ultimaAtualizacao = null;

setInterval(async () => {
  const response = await fetch('http://localhost:8000/status');
  const status = await response.json();
  
  const dataAtualizacao = status.cache.ultima_atualizacao;
  
  if (ultimaAtualizacao && dataAtualizacao !== ultimaAtualizacao) {
    console.log('⚠️  Dados foram alterados!');
    // Recarregar a lista
  }
  
  ultimaAtualizacao = dataAtualizacao;
}, 30000);
```

---

## Exemplo 9: Tratamento de Erros Completo

### JavaScript
```javascript
async function buscarCotasSeguro(status = null) {
  try {
    // Montar URL
    const url = new URL('http://localhost:8000/cotas');
    if (status) {
      url.searchParams.append('status', status);
    }
    
    // Fazer requisição
    const response = await fetch(url);
    
    // Verificar status HTTP
    if (response.status === 404) {
      console.error('Arquivo de dados não encontrado');
      return null;
    } else if (response.status === 400) {
      console.error('Dados inválidos na planilha');
      return null;
    } else if (response.status === 500) {
      console.error('Erro no servidor');
      return null;
    } else if (!response.ok) {
      console.error(`Erro HTTP ${response.status}`);
      return null;
    }
    
    // Parsear JSON
    const data = await response.json();
    console.log(`✅ ${data.total} cotas carregadas`);
    return data.cotas;
    
  } catch (erro) {
    if (erro instanceof TypeError) {
      console.error('❌ Não conseguiu conectar com a API');
      console.error('Verifique se o backend está rodando em http://localhost:8000');
    } else {
      console.error('❌ Erro inesperado:', erro);
    }
    return null;
  }
}

// Usar
await buscarCotasSeguro();
await buscarCotasSeguro('vendida');
```

---

## Exemplo 10: Integração com Formulário HTML

### HTML
```html
<form id="cotaForm">
  <input type="text" id="searchInput" placeholder="Buscar ID...">
  <button type="submit">Buscar</button>
</form>

<div id="resultado"></div>

<script>
document.getElementById('cotaForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const id = document.getElementById('searchInput').value.trim();
  
  if (!id) {
    alert('Digite um ID para buscar');
    return;
  }
  
  try {
    const response = await fetch(`http://localhost:8000/cotas/${id}`);
    
    if (response.ok) {
      const cota = await response.json();
      
      document.getElementById('resultado').innerHTML = `
        <h3>${cota.id}</h3>
        <p><strong>Tipo:</strong> ${cota.tipo}</p>
        <p><strong>Crédito:</strong> R$ ${cota.credito.toLocaleString('pt-BR')}</p>
        <p><strong>Entrada:</strong> R$ ${cota.entrada.toLocaleString('pt-BR')}</p>
        <p><strong>Parcelas:</strong> ${cota.parcela}x</p>
        <p><strong>Status:</strong> ${cota.status}</p>
        <p><strong>Administradora:</strong> ${cota.administradora}</p>
        <p><strong>Grupo:</strong> ${cota.grupo}</p>
      `;
    } else {
      document.getElementById('resultado').innerHTML = 
        '<p style="color: red;">Cota não encontrada</p>';
    }
  } catch (error) {
    document.getElementById('resultado').innerHTML = 
      '<p style="color: red;">Erro ao conectar com API</p>';
  }
});
</script>
```

---

## Exemplo 11: Export para CSV (Frontend)

### JavaScript
```javascript
async function exportarCotas() {
  const response = await fetch('http://localhost:8000/cotas');
  const { cotas } = await response.json();
  
  // Criar CSV
  let csv = 'id,tipo,credito,parcela,entrada,administradora,grupo\n';
  
  cotas.forEach(cota => {
    csv += `${cota.id},${cota.tipo},${cota.credito},${cota.parcela},`;
    csv += `${cota.entrada},${cota.administradora},${cota.grupo}\n`;
  });
  
  // Download
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cotas.csv';
  a.click();
}

// Usar
exportarCotas();
```

---

## Exemplo 12: Sincronizar com Banco de Dados (Python)

### Python
```python
import requests
import sqlalchemy as sa

# Conectar com API
response = requests.get('http://localhost:8000/cotas')
cotas_data = response.json()

# Conectar com BD
engine = sa.create_engine('postgresql://user:pass@localhost/db')

with engine.connect() as conn:
  for cota_dict in cotas_data['cotas']:
    # INSERT ou UPDATE
    stmt = sa.text("""
      INSERT INTO cotas (id, tipo, credito, parcela, entrada, 
                         status, administradora, grupo)
      VALUES (:id, :tipo, :credito, :parcela, :entrada, 
              :status, :administradora, :grupo)
      ON CONFLICT (id) DO UPDATE SET
        tipo = EXCLUDED.tipo,
        credito = EXCLUDED.credito,
        parcela = EXCLUDED.parcela,
        entrada = EXCLUDED.entrada,
        status = EXCLUDED.status
    """)
    
    conn.execute(stmt, cota_dict)
  
  conn.commit()

print(f"✅ {len(cotas_data['cotas'])} cotas sincronizadas com BD")
```

---

## Teste Rápido com Curl

```bash
# Listar cotas disponíveis
curl http://localhost:8000/cotas

# Listar cotas vendidas
curl "http://localhost:8000/cotas?status=vendida"

# Obter uma cota
curl http://localhost:8000/cotas/COT001

# Status da API
curl http://localhost:8000/status

# Recarregar cache
curl -X POST http://localhost:8000/reload-cache

# Documentação Swagger
curl http://localhost:8000/docs
```

---

## Performance: Benchmarks

```python
import requests
import time

url = 'http://localhost:8000/cotas'

# Primeira requisição (cold cache)
start = time.time()
requests.get(url)
primeiro = time.time() - start
print(f"Cold cache: {primeiro*1000:.2f}ms")

# Segundo (hot cache)
start = time.time()
requests.get(url)
segundo = time.time() - start
print(f"Hot cache: {segundo*1000:.2f}ms")

# Ganho de performance
print(f"Melhoria: {(primeiro/segundo):.1f}x mais rápido")
```

---

Todos esses exemplos funcionam com o projeto completo. Teste diretamente no navegador ou terminal!
