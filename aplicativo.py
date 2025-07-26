
# --- Minhas Finanças - Aplicativo Streamlit --- #

# Carregar de bibliotecas
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import altair as alt
import openpyxl


# Configurações do Streamlit
st.set_page_config(
    page_title='Dashboard Financeiro',
    page_icon='💲',
    layout='wide',
    initial_sidebar_state='expanded'
)


# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel('dados.xlsx', engine='openpyxl')
    df['Data'] = pd.to_datetime(df['Data'])
    df['AnoMes'] = df['Data'].dt.to_period('M').astype(str)
    return df

dados = carregar_dados()


# Sidebar de navegação
with st.sidebar:

    menu = option_menu(
        menu_title = 'Opções',
        menu_icon='cast',
        options=['Conta Corrente', 'Cartão de Crédito', 'Despesas Mensais'],
        icons=['currency-dollar','credit-card', 'calendar-fill'],
        orientation='vertical',
        styles={
        'container': {'padding': '0!important', 'background-color': '#3b4733'},
        'icon': {'color': 'orange', 'font-size': '16px'},
        'nav-link-selected': {'background-color': 'green'},
        'nav-link': {
            'font-size': '16px',
            'text-align': 'left',
            'margin': '1px',
            '--hover-color': '#f8f4ec',
            },
        },
    )


### Página  Conta Corrente ###
if menu == 'Conta Corrente':
    
    # Print título da página
    st.title('Conta Corrente')

    # Selecao competencia
    competencia_mes_atual = st.selectbox('Competência', sorted(dados['Competência'].unique()))
    competencia_mes_anterior = competencia_mes_atual[:-2] + str(int(competencia_mes_atual[-2:]) - 1).zfill(2)
    if competencia_mes_anterior == '2019-11': competencia_mes_anterior = '2019-12'
    
    # Filtro de dados da conta corrente por competência
    df_mes_atual = dados[(dados['Competência'] == competencia_mes_atual) & (dados['Origem'] == 'Conta Corrente')]
    df_mes_anterior = dados[(dados['Competência'] == competencia_mes_anterior) & (dados['Origem'] == 'Conta Corrente')]

    # Métricas
    receita_mes_atual = df_mes_atual[df_mes_atual['Receita/Despesa'] == 'Receita']['Valor'].sum()
    receita_mes_anterior = df_mes_anterior[df_mes_anterior['Receita/Despesa'] == 'Receita']['Valor'].sum()
    despesa_mes_atual = df_mes_atual[df_mes_atual['Receita/Despesa'] == 'Despesa']['Valor'].sum()
    despesa_mes_anterior = df_mes_anterior[df_mes_anterior['Receita/Despesa'] == 'Despesa']['Valor'].sum()
    saldo_mes_atual = receita_mes_atual - despesa_mes_atual
    saldo_mes_anterior = receita_mes_anterior - despesa_mes_anterior
    
    # Print de métricas
    col1, col2, col3 = st.columns(3, gap='large')
    col1.metric('Receitas', f'R$ {receita_mes_atual:.2f}', delta=round(receita_mes_anterior, 2), border=True)
    col2.metric('Despesas', f'R$ {despesa_mes_anterior:.2f}', delta=round(despesa_mes_anterior, 2), border=True)
    col3.metric('Saldo', f'R$ {saldo_mes_atual:.2f}', delta=round(saldo_mes_anterior, 2), border=True)

    # Print Gráfico
    tabela = pd.DataFrame({
        'Receita/Despesa': ['Receitas', 'Despesas', 'Saldo'],
        'Valor': [receita_mes_atual, despesa_mes_atual, saldo_mes_atual]
    })
    grafico = alt.Chart(tabela).mark_bar().encode(
        x = alt.X('Receita/Despesa', title='', 
                  axis=alt.Axis(labelAngle=0), 
                  scale=alt.Scale(paddingInner=0.5)
                  ),
        y = alt.Y('Valor', title='Valor (R$)')
    )
    st.altair_chart(grafico)



### Página  Conta Corrente ###
if menu == 'Cartão de Crédito':
    
    # Print título da página
    st.title('Cartão de Crédito')

    # Selecao competencia
    competencia_mes_atual = st.selectbox('Competência', sorted(dados['Competência'].unique()))
    competencia_mes_anterior = competencia_mes_atual[:-2] + str(int(competencia_mes_atual[-2:]) - 1).zfill(2)
    if competencia_mes_anterior == '2019-11': competencia_mes_anterior = '2019-12'
    
    # Filtro de dados do cartão de crédito por competência
    df_mes_atual = dados[(dados['Competência'] == competencia_mes_atual) & (dados['Origem'] == 'Cartão de Crédito')]
    df_mes_anterior = dados[(dados['Competência'] == competencia_mes_anterior) & (dados['Origem'] == 'Cartão de Crédito')]

    # Métricas
    receita_mes_atual = df_mes_atual[df_mes_atual['Receita/Despesa'] == 'Receita']['Valor'].sum()
    receita_mes_anterior = df_mes_anterior[df_mes_anterior['Receita/Despesa'] == 'Receita']['Valor'].sum()
    despesa_mes_atual = df_mes_atual[df_mes_atual['Receita/Despesa'] == 'Despesa']['Valor'].sum()
    despesa_mes_anterior = df_mes_anterior[df_mes_anterior['Receita/Despesa'] == 'Despesa']['Valor'].sum()
    saldo_mes_atual = receita_mes_atual - despesa_mes_atual
    saldo_mes_anterior = receita_mes_anterior - despesa_mes_anterior
    
    # Print de métricas
    col1, col2, col3 = st.columns(3, gap='large')
    col1.metric('Receitas', f'R$ {receita_mes_atual:.2f}', delta=round(receita_mes_anterior, 2), border=True)
    col2.metric('Despesas', f'R$ {despesa_mes_anterior:.2f}', delta=round(despesa_mes_anterior, 2), border=True)
    col3.metric('Saldo', f'R$ {saldo_mes_atual:.2f}', delta=round(saldo_mes_anterior, 2), border=True)

    # Print Gráfico
    tabela = pd.DataFrame({
        'Receita/Despesa': ['Receitas', 'Despesas', 'Saldo'],
        'Valor': [receita_mes_atual, despesa_mes_atual, saldo_mes_atual]
    })



