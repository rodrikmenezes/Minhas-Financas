import pandas as pd
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Categorias para classificação
CATEGORIAS = [
    "Financiamento Caixa",
    "Aluguel",
    "Moradia",
    "Academia",
    "Supermercado",
    "Restaurante",
    "Alimentação",
    "Transporte",
    "Combustível",
    "Utencílios",
    "Farmácia",
    "Seviços",
    "Assinaturas",
    "Saúde",
    "Viagem",
    "Educação",
    "Lazer",
    "Vestuário",
    "Despesas Financeiras",
    "Impostos e Taxas",
    "Presentes",
    "Investimentos"
]

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

# Adiciona colunas de identificação
df_cartao['Origem'] = 'Cartão'
df_conta['Origem'] = 'Conta'

# Combina os dois DataFrames
df_novos = pd.concat([df_cartao, df_conta], ignore_index=True)

# Ordena os dados pela data
df_novos['Data'] = pd.to_datetime(df_novos['Data'])
df_novos = df_novos.sort_values(by='Data')

# Importa o arquivo consolidado existente, se houver
if os.path.exists(arquivo_consolidado):
    df_existente = pd.read_excel(arquivo_consolidado)
    
    # Considera como chave única: Data, Descrição, Valor, Origem
    chaves = ['Data', 'Descrição', 'Valor', 'Origem']
    
    # Garante que as datas estejam no mesmo formato
    df_existente['Data'] = pd.to_datetime(df_existente['Data'])
    
    # Remove duplicatas dos novos dados que já existem no consolidado
    df_novos = df_novos.merge(df_existente[chaves], on=chaves, how='left', indicator=True)
    df_novos = df_novos[df_novos['_merge'] == 'left_only']
    df_novos = df_novos.drop(columns=['_merge'])
    
    # Junta os dados existentes com os novos
    df_consolidado = pd.concat([df_existente, df_novos], ignore_index=True)
else:
    df_consolidado = df_novos.copy()

# Função simples de classificação baseada em palavras-chave
def classificar_descricao(descricao):
    desc = str(descricao).lower()
    if any(p in desc for p in ['aluguel', 'condomínio', 'energia', 'água', 'luz', 'gás']):
        return "Moradia"
    if any(p in desc for p in ['supermercado', 'mercado', 'padaria', 'restaurante', 'pizza', 'lanche', 'bar', 'bebida', 'ifood']):
        return "Alimentação"
    if any(p in desc for p in ['uber', '99', 'ônibus', 'metrô', 'combustível', 'gasolina', 'transporte', 'passagem']):
        return "Transporte"
    if any(p in desc for p in ['farmácia', 'remédio', 'médico', 'dentista', 'plano de saúde', 'exame']):
        return "Saúde"
    if any(p in desc for p in ['escola', 'faculdade', 'curso', 'livro', 'material escolar']):
        return "Educação"
    if any(p in desc for p in ['cinema', 'show', 'teatro', 'lazer', 'entretenimento', 'netflix', 'spotify']):
        return "Lazer e Entretenimento"
    if any(p in desc for p in ['roupa', 'calçado', 'vestuário', 'moda']):
        return "Vestuário"
    if any(p in desc for p in ['escola infantil', 'creche', 'filho', 'criança']):
        return "Despesas com Filhos"
    if any(p in desc for p in ['pet', 'veterinário', 'ração', 'animal']):
        return "Despesas com Animais de Estimação"
    if any(p in desc for p in ['juros', 'tarifa', 'taxa', 'anuidade', 'banco']):
        return "Despesas Financeiras"
    if any(p in desc for p in ['iptu', 'ipva', 'imposto', 'taxa']):
        return "Impostos e Taxas"
    if any(p in desc for p in ['doação', 'presente']):
        return "Doações e Presentes"
    if any(p in desc for p in ['investimento', 'poupança', 'reserva', 'tesouro', 'cdb', 'lci', 'lca']):
        return "Reserva e Investimentos"
    return "Outros"

# Aplica a classificação
df_consolidado['Classificação'] = df_consolidado['Descrição'].apply(classificar_descricao)

# Salva o arquivo consolidado
df_consolidado.to_excel(arquivo_consolidado, index=False, sheet_name='Extrato')

print(f"✅ Arquivo consolidado gerado: {arquivo_consolidado}")

