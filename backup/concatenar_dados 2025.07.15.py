import pandas as pd
import os
import time

# Caminhos dos arquivos de entrada
arquivo_cartao = os.path.join(os.getcwd(), 'dados', 'nubank', 'cartao', 'extrato_nu_cartao.xlsx')
arquivo_conta = os.path.join(os.getcwd(), 'dados', 'nubank', 'conta', 'extrato_nu_conta.xlsx')

# Caminho do arquivo de saída
arquivo_consolidado = os.path.join(os.getcwd(), 'dados.xlsx')

# Verifica se os arquivos existem
if not os.path.exists(arquivo_cartao):
    raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_cartao}")
if not os.path.exists(arquivo_conta):
    raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_conta}")

# Carrega os dados dos arquivos
df_cartao = pd.read_excel(arquivo_cartao)
df_conta = pd.read_excel(arquivo_conta)

# Combina os dois DataFrames
df_consolidado = pd.concat([df_cartao, df_conta], ignore_index=True)

# Ordena os dados pela data
df_consolidado['Data'] = pd.to_datetime(df_consolidado['Data'])
df_consolidado = df_consolidado.sort_values(by='Data')

# Criar coluna 'Categoria' com valor 'Sem Categoria'
df_consolidado['Categoria'] = 'Sem Categoria'

# Salva o arquivo consolidado
df_consolidado.to_excel(arquivo_consolidado, index=False, sheet_name='Extrato')

print(f"✅ Arquivo consolidado gerado: {arquivo_consolidado}")

time.sleep(5) 



