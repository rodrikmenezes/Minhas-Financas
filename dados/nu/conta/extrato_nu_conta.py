import os
import pandas as pd
import time

# Diretório da pasta onde estão os CSVs
pasta_csv = os.getcwd()
arquivo_saida = os.path.join(pasta_csv, 'extrato_nu_conta.xlsx')
# pasta_csv = r'C:\Users\rodri\OneDrive\Documentos\GitHub\Minhas-Finanças\dados\nu\conta'
# arquivo_saida = r'C:\Users\rodri\OneDrive\Documentos\GitHub\Minhas-Finanças\dados\nu\conta\extrato_nu_conta.xlsx'

# Função para ler e padronizar um CSV do Nubank
def ler_csv_nubank(caminho_csv):
    df = pd.read_csv(caminho_csv, sep=',', encoding='utf-8')

    # Verifica e adapta nomes de colunas esperadas
    colunas_esperadas = {'Data', 'Valor', 'Identificador', 'Descrição'}
    colunas = set(df.columns)

    if not colunas_esperadas.issubset(colunas):
        raise ValueError(f'O arquivo {os.path.basename(caminho_csv)} não contém as colunas esperadas.')

    # Formata a data
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y').dt.date

    # Extrai competência
    df['Competência'] = pd.to_datetime(df['Data']).dt.strftime('%Y-%m')

    # Garante que valor seja numérico
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

    # Remove linhas inválidas
    df = df.dropna(subset=['Data', 'Valor', 'Descrição'])

    # Adiciona coluna Receita/Despesa
    df['Receita/Despesa'] = df['Valor'].apply(lambda x: 'Receita' if x >= 0 else 'Despesa')

    # Reorganiza colunas
    df = df[['Data', 'Competência', 'Descrição', 'Receita/Despesa', 'Valor']]

    return df

# Execução principal
def main():
    todos_csvs = [os.path.join(pasta_csv, f) for f in os.listdir(pasta_csv) if f.endswith('.csv')]
    if not todos_csvs:
        print('Nenhum arquivo CSV encontrado na pasta.')
        return

    # Concatena todos os arquivos CSV
    dfs = []
    for arquivo in todos_csvs:
        try:
            df = ler_csv_nubank(arquivo)
            dfs.append(df)
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")
    
    if not dfs:
        print("Nenhum dado válido foi extraído dos arquivos.")
        return

    df_novos = pd.concat(dfs, ignore_index=True)

    # Carrega dados existentes
    if os.path.exists(arquivo_saida):
        df_existente = pd.read_excel(arquivo_saida)
        df_existente['Data'] = pd.to_datetime(df_existente['Data']).dt.date
    else:
        df_existente = pd.DataFrame()

    # Filtra registros novos
    if not df_existente.empty:
        df_novos_filtrado = pd.merge(df_novos, df_existente,
                                     on=['Data', 'Descrição', 'Valor'],
                                     how='left', indicator=True)
        df_novos_filtrado = df_novos_filtrado[df_novos_filtrado['_merge'] == 'left_only']
        df_novos_filtrado = df_novos_filtrado.drop(columns=['_merge'])
    else:
        df_novos_filtrado = df_novos

    if df_novos_filtrado.empty:
        print('Nenhum novo dado foi importado.')
        return

    # Junta com os dados antigos
    if not df_existente.empty:
        df_final = pd.concat([df_existente, df_novos_filtrado], ignore_index=True)
    else:
        df_final = df_novos_filtrado

    # Converte todos os valores para absolutos (positivos)
    df_final['Valor'] = df_final['Valor'].abs()
    
    # Converte a coluna 'Data' para o tipo datetime
    df_final['Data'] = pd.to_datetime(df_final['Data'], format='%d/%m/%Y').dt.date

    # Reordena e salva
    df_final = df_final.sort_values(by='Data')
    df_final.to_excel(arquivo_saida, index=False, sheet_name='Extrato')
    print(f'Arquivo atualizado: {arquivo_saida}')
    print(f'Total de registros no arquivo: {len(df_final)}')
    print(f'Novos registros adicionados: {len(df_novos_filtrado)}')

if __name__ == '__main__':
    main()
    time.sleep(10)
