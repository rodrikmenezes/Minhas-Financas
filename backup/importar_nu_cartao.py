import os
import re
import pandas as pd
import pdfplumber
from datetime import datetime

# Pasta com os PDFs
# pasta_pdf = os.path.join(os.getcwd(), 'cartao')
pasta_pdf = r'C:\Users\e018266\OneDrive\Documentos\GitHub\Minhas-Finanças\dados\nu\cartao'
# pasta_saida = os.getcwd()
pasta_saida = r'C:\Users\e018266\OneDrive\Documentos\GitHub\Minhas-Finanças\dados\nu'

# Mapeamento de meses abreviados em português
meses = {
    'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
    'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
    'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
}

# Expressão para capturar linhas com formato: 02 SET Descrição R$123,45
padrao_linha = re.compile(r'^(\d{2})\s([A-Z]{3})\s+(.+?)\s+R\$ ?([\d.,]+)$')

# Função para extrair dados de um único PDF
def extrair_dados_pdf(caminho_pdf, ano):
    dados = []
    comecar = False
    
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue
            linhas = texto.split('\n')
            
            for linha in linhas:
                if not comecar:
                    if linha.startswith("TRANSAÇÕES DE "):
                        comecar = True
                    continue

                match = padrao_linha.match(linha.strip())
                if match:
                    dia, mes_abrev, descricao, valor = match.groups()
                    mes = meses.get(mes_abrev.upper())
                    if not mes:
                        continue
                    
                    # Data no formato completo
                    data_str = f"{ano}-{mes}-{dia}"
                    data_formatada = datetime.strptime(data_str, "%Y-%m-%d").date()

                    # Converte valor para float
                    valor_float = float(valor.replace('.', '').replace(',', '.'))

                    dados.append({
                        "Data": data_formatada,
                        "Descrição": descricao.strip(),
                        "Valor (R$)": valor_float
                    })
    
    return dados

# Lista todos os PDFs na pasta
todos_dados = []

for arquivo in os.listdir(pasta_pdf):
    if arquivo.endswith(".pdf") and arquivo.startswith("Nubank_"):
        caminho = os.path.join(pasta_pdf, arquivo)
        
        # Extrai ano do nome do arquivo
        match_ano = re.search(r'Nubank_(\d{4})', arquivo)
        if match_ano:
            ano = match_ano.group(1)
            dados_pdf = extrair_dados_pdf(caminho, ano)
            todos_dados.extend(dados_pdf)

# Converte para DataFrame
df_final = pd.DataFrame(todos_dados)

# Ordena por data
df_final = df_final.sort_values(by='Data')

# Salva no Excel
caminho_saida = os.path.join(pasta_saida, "extrato_nubank.xlsx")
df_final.to_excel(caminho_saida, index=False)

print(f"Arquivo Excel gerado: {caminho_saida}")


print(f"Total de registros extraídos: {len(todos_dados)}")
