
# Bibliotecas necessárias
import pandas as pd
from datetime import datetime 
import os

# Bibliotecas IA
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


# Importar o DataFrame consolidado
dados = pd.read_excel(os.path.join(os.getcwd(), 'dados.xlsx'), sheet_name='Extrato')

# Selecionar linhas que não possuem categoria
dados_sem_categoria = dados[dados['Categoria'] == 'Sem Categoria']


_ = load_dotenv(find_dotenv())

instrucao = """

Você é um especialista em finanças pessoais e sua tarefa é classificar transações bancárias em categorias de acordo com a lista abaixo:
- Financiamento Caixa
- Aluguel
- Moradia
- Academia
- Supermercado
- Restaurante
- Lanches
- IFood
- Uber
- Combustível
- Transporte
- Manutenção Carro
- Utencílios
- Farmácia
- Seviços
- Assinaturas
- Saúde
- Viagem
- Educação
- Livros
- Cursos
- Lazer
- Jogos
- Vestuário
- Despesas Financeiras
- Impostos e Taxas
- Presentes
- Investimentos
- Transferências
- Doações
- Cartão de Crédito
- Salário
- Outras Receitas
- Outras Despesas

Todas as transações são de pessoas físicas. 
As transações são de um extrato bancário e podem incluir receitas e despesas.
Escolha uma categoria da lista acima para este item:
{text}

Se você não encontrar uma categoria adequada, responda "Outras Despesas" ou "Outras Receitas".
Responda apenas com a categoria escolhida.

Abaixo estão alguns exemplos de transações e como classificá-las. 
Os exemplos seguem o formato "Descrição > Categoria". 
Se alguma descrição conter a palavra apontada no exemplo, classifique-a na categoria correspondente:
- Ifood > IFood
- Gulla Acai > Lanches
- Wfc > Restaurante
- Havan > Vestuário
- Dtudo > Presentes

"""


# Classificar as transações
prompt = ChatPromptTemplate.from_template(template=instrucao)
chat = ChatGroq(model="llama-3.1-8b-instant")
chain = prompt | chat

# Criar coluna de categoria no DataFrame
# categoria = []
for transacao in list(dados_sem_categoria['Descrição'].values):
    
    try:
        # categoria += [chain.invoke(transacao)]
        resultado = chain.invoke({"text": transacao})
        categoria = resultado.content.strip()
        dados.loc[dados['Descrição'] == transacao, 'Categoria'] = categoria
    except Exception as e:
        print(f"Erro ao classificar a transação '{transacao}': {e}")

# Salvar o DataFrame atualizado
dados.to_excel(os.path.join(os.getcwd(), 'dados.xlsx'), index=False, sheet_name='Extrato')
