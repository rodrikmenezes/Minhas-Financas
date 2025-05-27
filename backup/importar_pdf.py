
# ---------------------------------------------------------------
# Extrair dados de PDFs e salvar em um arquivo Excel
# ---------------------------------------------------------------

import os
import pandas as pd
import pdfplumber


# Extrair dados do PDF
def extrair_dados_pdf(caminho_pdf):
    dados = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                linhas = texto.split('\n')
                for linha in linhas:
                    
                    # Filtros
                    dados.append(linha)
                    
    return dados

caminho_pasta = r"C:\Users\e018266\OneDrive\Documentos\GitHub\Minhas-Finanças\dados\nu\cartao\Nubank_2023-10-09.pdf"

extrair_dados_pdf(caminho_pasta)
