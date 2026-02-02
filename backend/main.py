"""
Carta Contemplada API - Backend FastAPI
Aplicação para ler cotas contempladas de uma planilha Excel/CSV
e expor os dados via API REST JSON.

Arquitetura:
- Planilha (Excel/CSV) é a única fonte de dados
- Backend Python apenas LÊ e valida os dados
- Frontend consome a API e renderiza dinamicamente
- Cache simples para otimizar leituras frequentes
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Caminho do arquivo de dados (Excel ou CSV)
ARQUIVO_PLANILHA = Path(__file__).parent / "cotas.xlsx"  # Mude para .csv se necessário

# Configuração de cache (em segundos)
CACHE_DURATION_SECONDS = 60

# Colunas obrigatórias na planilha
COLUNAS_OBRIGATORIAS = ["id", "tipo", "credito", "parcela", "entrada", "status", "administradora", "grupo"]

# ============================================================================
# MODELS (Pydantic)
# ============================================================================

class Cota(BaseModel):
    """Modelo de uma cota contemplada."""
    id: str
    tipo: str
    credito: float
    parcela: int
    entrada: float
    status: str
    administradora: str
    grupo: str

    class Config:
        schema_extra = {
            "example": {
                "id": "COT001",
                "tipo": "Imóvel",
                "credito": 250000.00,
                "parcela": 120,
                "entrada": 25000.00,
                "status": "disponivel",
                "administradora": "ABC Imóveis",
                "grupo": "Grupo A"
            }
        }

class ResponseCotas(BaseModel):
    """Resposta da API com lista de cotas."""
    total: int
    cotas: List[Cota]
    timestamp: str

# ============================================================================
# CACHE SIMPLES
# ============================================================================

class CacheManager:
    """Gerenciador de cache simples em memória."""
    
    def __init__(self, duration_seconds: int = 60, file_path: Path = None):
        self.duration_seconds = duration_seconds
        self.file_path = file_path
        self.data = None
        self.last_update = None
        self.file_mtime = None
    
    def is_valid(self) -> bool:
        """Verifica se o cache ainda é válido."""
        if self.data is None or self.last_update is None or self.file_path is None:
            return False
        
        # Verifica se o arquivo foi modificado
        try:
            current_mtime = self.file_path.stat().st_mtime
            if current_mtime != self.file_mtime:
                return False
        except (OSError, FileNotFoundError):
            return False
        
        elapsed = datetime.now() - self.last_update
        return elapsed < timedelta(seconds=self.duration_seconds)
    
    def get(self):
        """Retorna dados do cache se válido."""
        if self.is_valid():
            return self.data
        return None
    
    def set(self, data):
        """Armazena dados no cache."""
        self.data = data
        self.last_update = datetime.now()
        if self.file_path:
            try:
                self.file_mtime = self.file_path.stat().st_mtime
            except (OSError, FileNotFoundError):
                self.file_mtime = None
    
    def clear(self):
        """Limpa o cache."""
        self.data = None
        self.last_update = None
        self.file_mtime = None

# ============================================================================
# FUNÇÕES DE LEITURA E VALIDAÇÃO
# ============================================================================

def validar_colunas(df: pd.DataFrame) -> None:
    """
    Valida se o DataFrame contém todas as colunas obrigatórias.
    
    Args:
        df: DataFrame do pandas
        
    Raises:
        ValueError: Se faltarem colunas obrigatórias
    """
    colunas_faltantes = set(COLUNAS_OBRIGATORIAS) - set(df.columns)
    
    if colunas_faltantes:
        raise ValueError(
            f"Colunas obrigatórias faltando na planilha: {colunas_faltantes}\n"
            f"Colunas esperadas: {COLUNAS_OBRIGATORIAS}"
        )

def validar_dados_linha(row: pd.Series) -> tuple[bool, Optional[str]]:
    """
    Valida uma linha de dados da planilha.
    
    Args:
        row: Linha do DataFrame
        
    Returns:
        Tupla (é_válido, mensagem_erro)
    """
    # Validar campos obrigatórios não vazios
    if pd.isna(row["id"]) or str(row["id"]).strip() == "":
        return False, f"ID não pode estar vazio"
    
    if pd.isna(row["status"]):
        return False, f"Status obrigatório para cota {row['id']}"
    
    # Validar status permitido
    status_permitidos = ["disponivel", "vendida"]
    if str(row["status"]).strip().lower() not in status_permitidos:
        return False, f"Status inválido para {row['id']}: {row['status']}. Permitido: {status_permitidos}"
    
    # Validar tipos numéricos
    try:
        float(row["credito"])
        float(row["parcela"])
        float(row["entrada"])
    except (ValueError, TypeError):
        return False, f"Valores numéricos inválidos para cota {row['id']}"
    
    return True, None

def ler_planilha() -> List[Cota]:
    """
    Lê a planilha de cotas (Excel ou CSV) e retorna lista de cotas válidas.
    
    Returns:
        Lista de objetos Cota
        
    Raises:
        FileNotFoundError: Se a planilha não existir
        ValueError: Se houver problemas na leitura ou validação
    """
    
    if not ARQUIVO_PLANILHA.exists():
        raise FileNotFoundError(
            f"Planilha não encontrada em: {ARQUIVO_PLANILHA}\n"
            f"Por favor, crie um arquivo de dados em {DADOS_DIR}"
        )
    
    # Detectar tipo de arquivo e ler
    try:
        if str(ARQUIVO_PLANILHA).endswith('.xlsx'):
            df = pd.read_excel(ARQUIVO_PLANILHA)
        elif str(ARQUIVO_PLANILHA).endswith('.csv'):
            df = pd.read_csv(ARQUIVO_PLANILHA)
        else:
            raise ValueError("Arquivo deve ser .xlsx ou .csv")
    except Exception as e:
        raise ValueError(f"Erro ao ler planilha: {str(e)}")
    
    # Validar colunas
    validar_colunas(df)
    
    # Processar e validar linhas
    cotas = []
    erros = []
    
    for idx, row in df.iterrows():
        # Pular linhas vazias
        if pd.isna(row["id"]):
            continue
        
        # Validar dados
        é_válido, msg_erro = validar_dados_linha(row)
        if not é_válido:
            erros.append(f"Linha {idx + 2}: {msg_erro}")
            continue
        
        # Criar objeto Cota
        try:
            cota = Cota(
                id=str(row["id"]).strip(),
                tipo=str(row["tipo"]).strip() if not pd.isna(row["tipo"]) else "",
                credito=float(row["credito"]),
                parcela=int(float(row["parcela"])),
                entrada=float(row["entrada"]),
                status=str(row["status"]).strip().lower(),
                administradora=str(row["administradora"]).strip() if not pd.isna(row["administradora"]) else "",
                grupo=str(row["grupo"]).strip() if not pd.isna(row["grupo"]) else ""
            )
            cotas.append(cota)
        except Exception as e:
            erros.append(f"Linha {idx + 2}: Erro ao processar - {str(e)}")
    
    # Log de erros (opcional)
    if erros:
        print("⚠️  AVISOS NA LEITURA DA PLANILHA:")
        for erro in erros:
            print(f"  {erro}")
    
    print(f"✅ Lidas {len(cotas)} cotas válidas da planilha")
    return cotas

# ============================================================================
# APLICAÇÃO FastAPI
# ============================================================================

app = FastAPI(
    title="Carta Contemplada API",
    description="API para consulta de cotas contempladas (CMS baseado em planilha)",
    version="1.0.0"
)

# CORS - permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar cache
cache = CacheManager(duration_seconds=CACHE_DURATION_SECONDS, file_path=ARQUIVO_PLANILHA)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "aplicacao": "Carta Contemplada API",
        "versao": "1.0.0",
        "endpoints": {
            "GET /cotas": "Retorna todas as cotas disponíveis",
            "GET /cotas?status=disponivel": "Filtrar por status",
            "GET /status": "Status da API e informações de cache"
        }
    }

@app.get("/cotas", response_model=ResponseCotas)
async def get_cotas(
    status: Optional[str] = Query(None, description="Filtrar por status: 'disponivel' ou 'vendida'")
):
    """
    Retorna lista de cotas da planilha.
    
    Por padrão, retorna TODAS as cotas.
    Use o parâmetro status para filtrar por 'disponivel' ou 'vendida'.
    
    Query Parameters:
        - status: Filtro opcional por status. Se não informado, retorna todas
    
    Returns:
        ResponseCotas com lista de cotas e total
    """
    try:
        # Tentar usar cache
        dados_cached = cache.get()
        
        if dados_cached is None:
            # Cache expirado ou vazio, ler da planilha
            cotas = ler_planilha()
            cache.set(cotas)
        else:
            cotas = dados_cached
        
        # Filtrar por status
        if status is None:
            # Padrão: retornar todas as cotas
            cotas_filtradas = cotas
        else:
            status = status.lower().strip()
            cotas_filtradas = [c for c in cotas if c.status == status]
        
        return ResponseCotas(
            total=len(cotas_filtradas),
            cotas=cotas_filtradas,
            timestamp=datetime.now().isoformat()
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/cotas/{cota_id}")
async def get_cota(cota_id: str):
    """
    Retorna detalhes de uma cota específica pelo ID.
    
    Path Parameters:
        - cota_id: ID da cota
    
    Returns:
        Objeto Cota ou erro 404
    """
    try:
        dados_cached = cache.get()
        
        if dados_cached is None:
            cotas = ler_planilha()
            cache.set(cotas)
        else:
            cotas = dados_cached
        
        cota = next((c for c in cotas if c.id == cota_id), None)
        
        if cota is None:
            raise HTTPException(status_code=404, detail=f"Cota com ID '{cota_id}' não encontrada")
        
        return cota
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/reload-cache")
async def reload_cache():
    """
    Força o recarregamento do cache (lê a planilha novamente).
    Útil após editar a planilha.
    """
    try:
        cache.clear()
        cotas = ler_planilha()
        cache.set(cotas)
        
        return {
            "status": "sucesso",
            "mensagem": "Cache recarregado",
            "total_cotas": len(cotas),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recarregar: {str(e)}")

@app.get("/status")
async def get_status():
    """Retorna status da API e informações de cache."""
    cache_valido = cache.is_valid()
    
    return {
        "status": "online",
        "cache": {
            "ativo": cache_valido,
            "duracao_segundos": CACHE_DURATION_SECONDS,
            "ultima_atualizacao": cache.last_update.isoformat() if cache.last_update else None,
            "tempo_restante_segundos": (
                int((cache.last_update + timedelta(seconds=CACHE_DURATION_SECONDS) - datetime.now()).total_seconds())
                if cache_valido else 0
            )
        },
        "arquivo_dados": str(ARQUIVO_PLANILHA),
        "arquivo_existe": ARQUIVO_PLANILHA.exists(),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 Carta Contemplada API - Iniciando...")
    print("=" * 70)
    print(f"📁 Diretório de dados: {DADOS_DIR}")
    print(f"📄 Planilha esperada: {ARQUIVO_PLANILHA}")
    print(f"⏱️  Cache: {CACHE_DURATION_SECONDS} segundos")
    print("=" * 70)
    
    # Tentar ler a planilha na inicialização
    try:
        cotas = ler_planilha()
        cache.set(cotas)
        print(f"✅ Inicialização bem-sucedida com {len(cotas)} cotas")
    except FileNotFoundError:
        print("⚠️  AVISO: Planilha não encontrada. Crie 'cotas.xlsx' em ./dados/")
    except Exception as e:
        print(f"❌ ERRO na inicialização: {str(e)}")
        # Não parar o servidor por erro na planilha
    
    print("=" * 70)
    print("📍 API rodando em: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("=" * 70)
    
    # Iniciar servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Desabilitado para evitar reinicializações
        log_level="info"
    )
