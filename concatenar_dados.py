import pandas as pd
import os
import time

# Caminhos dos arquivos de entrada
arquivo_cartao = os.path.join(os.getcwd(), 'dados', 'nubank', 'cartao de crédito', 'extrato_nu_cartao.xlsx')
arquivo_conta = os.path.join(os.getcwd(), 'dados', 'nubank', 'conta corrente', 'extrato_nu_conta.xlsx')

# Caminho do arquivo de saída
arquivo_consolidado = os.path.join(os.getcwd(), 'dados.xlsx')

# Carrega os dados dos arquivos de cartão e conta
df_cartao = pd.read_excel(arquivo_cartao)
df_conta = pd.read_excel(arquivo_conta)

# Combina os dois DataFrames
df_novos = pd.concat([df_cartao, df_conta], ignore_index=True)

# Ordena os dados pela data
df_novos['Data'] = pd.to_datetime(df_novos['Data'])
df_novos = df_novos.sort_values(by='Data')

# Cria coluna 'Categoria' com valor 'Sem Categoria' se não existir
if 'Categoria' not in df_novos.columns:
    df_novos['Categoria'] = 'Sem Categoria'

# Importa o arquivo dados.xlsx, se houver
if os.path.exists(arquivo_consolidado):
    df_base = pd.read_excel(arquivo_consolidado)
    
    # Garante que as colunas de comparação existem
    for col in ['Data', 'Competência', 'Banco', 'Origem']:
        if col not in df_base.columns:
            df_base[col] = None
            
    # Converte as colunas para comparação
    df_novos['Data'] = pd.to_datetime(df_novos['Data'])
    df_base['Data'] = pd.to_datetime(df_base['Data'])
    for col in ['Competência', 'Banco', 'Origem']:
        df_novos[col] = df_novos[col].astype(str)
        df_base[col] = df_base[col].astype(str)
        
    # Faz o merge anti para pegar apenas os dados novos
    mask = ~df_novos.set_index(['Data', 'Competência', 'Banco', 'Origem']).index.isin(
        df_base.set_index(['Data', 'Competência', 'Banco', 'Origem']).index
    )
    df_para_adicionar = df_novos[mask]
    
    # Concatena apenas os dados novos
    df_final = pd.concat([df_base, df_para_adicionar], ignore_index=True)
else:
    df_final = df_novos

# Salva o arquivo consolidado
df_final.to_excel(arquivo_consolidado, index=False, sheet_name='Extrato')

print(f"✅ Arquivo consolidado gerado: {arquivo_consolidado}")

time.sleep(5)