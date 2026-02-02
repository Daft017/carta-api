import pandas as pd
from pathlib import Path

# Ler CSV
csv_path = Path('dados/cotas_exemplo.csv')
df = pd.read_csv(csv_path)

# Salvar como Excel
xlsx_path = Path('dados/cotas.xlsx')
df.to_excel(xlsx_path, index=False, engine='openpyxl')
print(f'✅ Criado: {xlsx_path}')
print(f'📊 Dimensões: {df.shape[0]} linhas, {df.shape[1]} colunas')
print(f'🔍 Colunas: {list(df.columns)}')
