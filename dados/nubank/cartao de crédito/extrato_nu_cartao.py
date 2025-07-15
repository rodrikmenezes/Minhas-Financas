import os
import re
import pandas as pd
import pdfplumber
from datetime import datetime
import logging
import time

# Suprime o warning CropBox missing from /Page, defaulting to MediaBox
logging.getLogger('pdfminer').setLevel(logging.ERROR)

# Diretórios e arquivo de saída
pasta_pdf = os.getcwd()
arquivo_saida = os.path.join(pasta_pdf, 'extrato_nu_cartao.xlsx')

# Expressão regular ajustada
padrao_linha = re.compile(r'^(\d{2})\s+([A-Z]{3})\s+(.+?)\s+([\d.,\\s]+)$')


def extrair_dados_pdf(caminho_pdf, competencia, ano):
    dados = []
    comecar = False

    meses = {
        'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
        'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
        'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
    }

    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            try:
                texto = pagina.extract_text()
            except Exception:
                continue
            if not texto:
                continue

            linhas = texto.split('\n')
            for linha in linhas:
                if not comecar:
                    if linha.startswith('TRANSAÇÕES DE '):
                        comecar = True
                    continue

                match = padrao_linha.match(linha.strip())
                if match:
                    dia, mes_num, descricao, valor = match.groups()
                    mes = meses.get(mes_num.upper())
                    if not mes:
                        continue

                    data_str = f'{ano}-{mes}-{dia}'
                    data_formatada = datetime.strptime(data_str, '%Y-%m-%d').date()
                    valor_float = float(valor.replace('.', '').replace(',', '.'))

                    descricao = descricao.strip()
                    
                    # Tratamento de receitas
                    receita_keywords = [
                        
                        'Pagamento recebido', 
                        'Pagamento em',
                        'Transferência recebida'
                        
                        ]
                    
                    tipo = 'Receita' if any(descricao.startswith(k) for k in receita_keywords) else 'Despesa'

                    dados.append({
                        'Data': data_formatada,
                        'Competência': competencia,
                        'Banco': 'Nubank',
                        'Origem': 'Cartão de Crédito',
                        'Descrição': descricao,
                        'Receita/Despesa': tipo,
                        'Valor': valor_float
                    })
    return dados

# Execução principal
def main():
    
    # Carrega dados existentes
    if os.path.exists(arquivo_saida):
        df_existente = pd.read_excel(arquivo_saida)
        competencias_existentes = set(df_existente['Competência'].unique())
    else:
        df_existente = pd.DataFrame()
        competencias_existentes = set()

    todos_dados = []

    for arquivo in os.listdir(pasta_pdf):
        
        if arquivo.endswith('.pdf') and arquivo.startswith('Nubank_'):
            match = re.search(r'Nubank_(\d{4})[_-](\d{2})', arquivo)
            if not match:
                print(f'Nome de arquivo inesperado: {arquivo}')
                continue

            ano, mes = match.groups()
            competencia = f'{ano}-{mes}'

            if competencia in competencias_existentes:
                print(f'Já Importado: {arquivo}')
                time.sleep(0.05)
                continue

            caminho = os.path.join(pasta_pdf, arquivo)
            dados_pdf = extrair_dados_pdf(caminho, competencia, ano)
            todos_dados.extend(dados_pdf)
            print(f'Processando: {arquivo}')

    if not todos_dados:
        print('Nenhum novo dado foi importado.')
        return

    df_novos = pd.DataFrame(todos_dados)
    df_novos = df_novos.sort_values(by='Data')

    if not df_existente.empty:
        df_final = pd.concat([df_existente, df_novos], ignore_index=True)
    else:
        df_final = df_novos

    # Converte todos os valores para absolutos, exceto estornos
    df_final['Valor'] = df_final['Valor'].abs()
    
    # Tratamento de estornos e outros ajustes
    df_final['Valor'] = df_final.apply(lambda row: -row['Valor'] if 'Estorno de' in row['Descrição'] else row['Valor'], axis=1)  
    df_final['Valor'] = df_final.apply(lambda row: -row['Valor'] if row['Descrição'].startswith('Crédito de ') else row['Valor'], axis=1)  

    # Ordena e salva
    df_final.to_excel(arquivo_saida, index=False, sheet_name='Extrato')
    print(f'Dados salvos em: {arquivo_saida}')
    print(f'Total de registros no arquivo: {len(df_final)}')
    print(f'Novos registros adicionados: {len(df_novos)}')

if __name__ == '__main__':
    main()
    time.sleep(10)