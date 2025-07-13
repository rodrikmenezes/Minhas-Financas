import os
import pandas as pd
from datetime import datetime
import time

# Diretório atual
pasta_csv = os.getcwd()
arquivo_saida = os.path.join(pasta_csv, 'extrato_nu_conta.xlsx')

def ler_csv_nubank(caminho_csv):
    df = pd.read_csv(caminho_csv, sep=',', encoding='utf-8')

    # Validação de colunas esperadas
    colunas_esperadas = {'Data', 'Valor', 'Identificador', 'Descrição'}
    if not colunas_esperadas.issubset(df.columns):
        raise ValueError(f'O arquivo {os.path.basename(caminho_csv)} não contém as colunas esperadas.')

    # Ajustes de formato
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    df = df.dropna(subset=['Data', 'Valor', 'Descrição'])

    # Criar coluna Competência (formato AAAA-MM)
    df['Competência'] = pd.to_datetime(df['Data']).dt.strftime('%Y-%m')

    # Receita ou Despesa
    df['Receita/Despesa'] = df['Valor'].apply(lambda x: 'Receita' if x >= 0 else 'Despesa')

    # Apenas as colunas finais que queremos
    df = df[['Data', 'Competência', 'Descrição', 'Receita/Despesa', 'Valor']]

    return df

def main():
    # Carrega o histórico existente, se houver
    if os.path.exists(arquivo_saida):
        df_existente = pd.read_excel(arquivo_saida)
        df_existente['Data'] = pd.to_datetime(df_existente['Data']).dt.date
    else:
        df_existente = pd.DataFrame()

    todos_dados = []

    arquivo = 'NU_445802081_01JAN2020_31DEZ2020.csv'


    # Procura por todos os CSVs na pasta
    for arquivo in os.listdir(pasta_csv):
        if arquivo.endswith('.csv'):
            caminho = os.path.join(pasta_csv, arquivo)
            try:
                df = ler_csv_nubank(caminho)
                todos_dados.append(df)
                print(f'Processado: {arquivo} - {len(df)} registros')
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")

    if not todos_dados:
        print('Nenhum novo dado foi importado.')
        return

    df_novos = pd.concat(todos_dados, ignore_index=True)
    df_novos = df_novos.sort_values(by='Data')

    # Junta com o histórico existente
    if not df_existente.empty:
        df_final = pd.concat([df_existente, df_novos], ignore_index=True)
    else:
        df_final = df_novos

    # Converte valores para positivos
    df_final['Valor'] = df_final['Valor'].abs()

    # Converte 'Data' para datetime.date
    df_final['Data'] = pd.to_datetime(df_final['Data']).dt.date

    # Ordena e salva
    df_final = df_final.sort_values(by='Data')
    df_final.to_excel(arquivo_saida, index=False, sheet_name='Extrato')

    print(f'Dados salvos em: {arquivo_saida}')
    print(f'Total de registros no arquivo: {len(df_final)}')
    print(f'Novos registros adicionados: {len(df_novos)}')

if __name__ == '__main__':
    main()
    time.sleep(10)
