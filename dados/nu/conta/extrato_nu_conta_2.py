import os
import pandas as pd
from datetime import datetime
import time

# Diretório da pasta onde estão os CSVs
pasta_csv = os.getcwd()
arquivo_saida = os.path.join(pasta_csv, 'extrato_nu_conta.xlsx')

def ler_csv_nubank(caminho_csv, competencia):
    df = pd.read_csv(caminho_csv, sep=',', encoding='utf-8')

    # Verifica se contém as colunas esperadas
    colunas_esperadas = {'Data', 'Valor', 'Identificador', 'Descrição'}
    if not colunas_esperadas.issubset(df.columns):
        raise ValueError(f'O arquivo {os.path.basename(caminho_csv)} não contém as colunas esperadas.')

    # Formatação e limpeza
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date
    df['Competência'] = competencia
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    df = df.dropna(subset=['Data', 'Valor', 'Descrição'])

    df['Receita/Despesa'] = df['Valor'].apply(lambda x: 'Receita' if x >= 0 else 'Despesa')
    df = df[['Data', 'Competência', 'Descrição', 'Receita/Despesa', 'Valor']]

    return df

def main():
    # Carrega dados existentes do Excel (se houver)
    if os.path.exists(arquivo_saida):
        df_existente = pd.read_excel(arquivo_saida)
        df_existente['Data'] = pd.to_datetime(df_existente['Data']).dt.date
        competencias_existentes = set(df_existente['Competência'].unique())
    else:
        df_existente = pd.DataFrame()
        competencias_existentes = set()

    todos_dados = []

    # arquivo = 'NU_445802081_01JAN2020_31DEZ2020.csv'

    # Processa todos os CSVs válidos
    for arquivo in os.listdir(pasta_csv):
        # if arquivo.endswith('.csv') and arquivo.startswith('dados_'):
        if arquivo.endswith('.csv'):
            match = pd.Series(arquivo).str.extract(r'dados_(\d{4})[-_](\d{2})')
            if match.empty or match.isnull().values.any():
                print(f'Nome de arquivo inesperado: {arquivo}')
                continue

            ano, mes = match.iloc[0]
            competencia = f'{ano}-{mes}'

            if competencia in competencias_existentes:
                print(f'Ignorado (já importado): {arquivo}')
                continue

            caminho = os.path.join(pasta_csv, arquivo)
            try:
                df = ler_csv_nubank(caminho, competencia)
                todos_dados.append(df)
                print(f'Processado: {arquivo} - {len(df)} registros')
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")

    if not todos_dados:
        print('Nenhum novo dado foi importado.')
        return

    df_novos = pd.concat(todos_dados, ignore_index=True)
    df_novos = df_novos.sort_values(by='Data')

    # Junta com dados existentes
    if not df_existente.empty:
        df_final = pd.concat([df_existente, df_novos], ignore_index=True)
    else:
        df_final = df_novos

    # Converte valores para positivos
    df_final['Valor'] = df_final['Valor'].abs()

    # Converte 'Data' para datetime.date
    df_final['Data'] = pd.to_datetime(df_final['Data']).dt.date

    # Ordena e salva no Excel
    df_final = df_final.sort_values(by='Data')
    df_final.to_excel(arquivo_saida, index=False, sheet_name='Extrato')

    print(f'Dados salvos em: {arquivo_saida}')
    print(f'Total de registros no arquivo: {len(df_final)}')
    print(f'Novos registros adicionados: {len(df_novos)}')

if __name__ == '__main__':
    main()
    time.sleep(10)
