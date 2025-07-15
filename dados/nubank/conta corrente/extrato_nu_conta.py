import os
import pandas as pd
from datetime import datetime
import time

# Diretório atual e nome do arquivo final
pasta_csv = os.getcwd()
arquivo_saida = os.path.join(pasta_csv, 'extrato_nu_conta.xlsx')

# Lista para armazenar todos os DataFrames
todos_dados = []

# Percorre todos os arquivos .csv da pasta
for arquivo in os.listdir(pasta_csv):
    if arquivo.endswith('.csv'):
        caminho = os.path.join(pasta_csv, arquivo)
        try:
            df = pd.read_csv(caminho, sep=',', encoding='utf-8')

            # Verifica colunas obrigatórias
            colunas_esperadas = {'Data', 'Valor', 'Identificador', 'Descrição'}
            if not colunas_esperadas.issubset(df.columns):
                print(f'Arquivo ignorado (colunas ausentes): {arquivo}')
                continue

            # Converte tipos e limpa
            df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            df = df.dropna(subset=['Data', 'Valor', 'Descrição'])

            # Nova coluna: Competência (AAAA-MM)
            df['Competência'] = pd.to_datetime(df['Data']).dt.strftime('%Y-%m')

            # Receita ou Despesa
            df['Receita/Despesa'] = df['Valor'].apply(lambda x: 'Receita' if x >= 0 else 'Despesa')
            
            # Converte todos os valores para absolutos (positivos)
            df['Valor'] = df['Valor'].abs()

            # Adiciona coluna Banco
            df['Banco'] = 'Nubank'
            
            # Adiciona coluna Origem
            df['Origem'] = 'Conta Corrente'

            # Seleciona e ordena colunas
            df = df[['Data', 'Competência', 'Banco', 'Origem', 'Descrição', 'Receita/Despesa', 'Valor']]

            todos_dados.append(df)
            print(f'Processado: {arquivo} - {len(df)} registros')
            time.sleep(0.2)

        except Exception as e:
            print(f'Erro ao processar {arquivo}: {e}')

# Se nenhum dado foi lido, encerra
if not todos_dados:
    print('Nenhum dado foi importado.')
else:
    df_final = pd.concat(todos_dados, ignore_index=True)
    df_final = df_final.sort_values(by='Data')
    df_final.to_excel(arquivo_saida, index=False, sheet_name='Extrato')
    print(f'Dados salvos em: {arquivo_saida}')
    print(f'Total de registros: {len(df_final)}')

time.sleep(10)
