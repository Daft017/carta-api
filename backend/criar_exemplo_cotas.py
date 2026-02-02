"""
Script para criar arquivo de exemplo 'cotas.xlsx' com dados de teste.
Execute este arquivo uma vez para gerar o exemplo de dados.
"""

import pandas as pd
from pathlib import Path

# Dados de exemplo
dados = {
    "id": ["COT001", "COT002", "COT003", "COT004", "COT005", "COT006", "COT007", "COT008"],
    "tipo": ["Imóvel", "Imóvel", "Imóvel", "Imóvel", "Imóvel", "Imóvel", "Veículo", "Veículo"],
    "credito": [250000.00, 300000.00, 180000.00, 420000.00, 150000.00, 280000.00, 45000.00, 65000.00],
    "parcela": [120, 180, 84, 240, 60, 120, 48, 60],
    "entrada": [25000.00, 30000.00, 18000.00, 42000.00, 15000.00, 28000.00, 4500.00, 6500.00],
    "status": ["disponivel", "disponivel", "vendida", "disponivel", "disponivel", "vendida", "disponivel", "disponivel"],
    "administradora": ["ABC Imóveis", "XYZ Crédito", "ABC Imóveis", "Premium Consórcios", "ABC Imóveis", "XYZ Crédito", "AutoFlex", "AutoFlex"],
    "grupo": ["Grupo A", "Grupo B", "Grupo A", "Grupo C", "Grupo A", "Grupo B", "Grupo D", "Grupo D"],
}

# Criar DataFrame
df = pd.DataFrame(dados)

# Caminho do arquivo
arquivo = Path(__file__).parent / "cotas.xlsx"

# Salvar arquivo
df.to_excel(arquivo, index=False, engine='openpyxl')

print(f"✅ Arquivo '{arquivo}' criado com sucesso!")
print(f"\nPlanilha de exemplo com {len(df)} cotas:")
print(df.to_string())
