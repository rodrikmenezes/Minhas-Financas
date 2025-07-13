### Etapa 1: Importar bibliotecas necessárias

import os
import re
import pandas as pd
import pdfplumber
from datetime import datetime
import logging
import shutil
import time

# Suprime o warning "CropBox missing from /Page"
logging.getLogger('pdfminer').setLevel(logging.ERROR)

### Etapa 2: Definir o diretório de trabalho e nome do arquivo de saída

# Define o diretório atual onde estão os arquivos PDF
pasta_pdf = os.getcwd()

# Define o nome do arquivo de saída Excel
arquivo_saida = os.path.join(pasta_pdf, 'extrato_nu_cartao.xlsx')

### Etapa 3: Criar um backup do arquivo existente (se houver)

if os.path.exists(arquivo_saida):
    backup_path = arquivo_saida.replace('.xlsx', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    shutil.copy(arquivo_saida, backup_path)
    print(f'Backup criado: {backup_path}')

### Etapa 4: Carregar dados existentes e identificar competências já importadas

if os.path.exists(arquivo_saida):
    df_existente = pd.read_excel(arquivo_saida)
    competencias_existentes = set(df_existente['Competência'].unique())
else:
    df_existente = pd.DataFrame()
    competencias_existentes = set()

### Etapa 5: Inicializar a extração de dados

todos_dados = []

# Mapeamento de meses abreviados para números
meses = {
    'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
    'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
    'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
}

# Expressão regular para identificar linhas de transações
padrao_linha = re.compile(r'^(\d{2})\s+([A-Z]{3})\s+(.+?)\s+([\d.,\s]+)$')

### Etapa 6: Iterar sobre os arquivos PDF e extrair dados

for arquivo in os.listdir(pasta_pdf):

    if arquivo.endswith('.pdf') and arquivo.startswith('Nubank_'):
        match = re.search(r'Nubank_(\d{4})[_-](\d{2})', arquivo)
        if not match:
            print(f'Nome de arquivo inesperado: {arquivo}')
            continue

        ano, mes = match.groups()
        competencia = f'{ano}-{mes}'

        if competencia in competencias_existentes:
            print(f'Ignorado (já importado): {arquivo}')
            continue

        caminho = os.path.join(pasta_pdf, arquivo)

        with pdfplumber.open(caminho) as pdf:
            comecar = False
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
                        dia, mes_str, descricao, valor = match.groups()
                        mes_num = meses.get(mes_str.upper())
                        if not mes_num:
                            continue

                        data_str = f'{ano}-{mes_num}-{dia}'
                        data_formatada = datetime.strptime(data_str, '%Y-%m-%d').date()
                        valor_float = float(valor.replace('.', '').replace(',', '.').strip())
                        descricao = descricao.strip()

                        receita_keywords = ['Estorno de', 'Crédito de Confiança de', 'Pagamento recebido', 'Transferência recebida']
                        tipo = 'Receita' if any(descricao.startswith(k) for k in receita_keywords) else 'Despesa'

                        todos_dados.append({
                            'Data': data_formatada,
                            'Competência': competencia,
                            'Descrição': descricao,
                            'Receita/Despesa': tipo,
                            'Valor': valor_float
                        })
        print(f'Processado: {arquivo}')

### Etapa 7: Consolidar e salvar os dados em Excel

if not todos_dados:
    print('Nenhum novo dado foi importado.')
else:
    df_novos = pd.DataFrame(todos_dados)
    df_novos = df_novos.sort_values(by='Data')

    if not df_existente.empty:
        df_final = pd.concat([df_existente, df_novos], ignore_index=True)
    else:
        df_final = df_novos

    # Valores absolutos (positivos)
    df_final['Valor'] = df_final['Valor'].abs()

    # Ordenar por data e salvar
    df_final = df_final.sort_values(by='Data')
    df_final.to_excel(arquivo_saida, index=False, sheet_name='Extrato')
    print(f'Dados salvos em: {arquivo_saida}')
    print(f'Total de registros no arquivo: {len(df_final)}')
    print(f'Novos registros adicionados: {len(df_novos)}')

### Etapa 8: Aguardar 10 segundos antes de encerrar

time.sleep(10)
