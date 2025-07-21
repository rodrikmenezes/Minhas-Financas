
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
        options=['Resumo', 'Saldo', 'Status'],
        icons=['house','basket', 'bar-chart'],
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


# Página: Resumo
if menu == 'Resumo':
    
    # Print título da página
    st.title('Resumo Financeiro')

    # Sidebar secundário
    competencia = st.selectbox('Selecione a competência', sorted(dados['Competência'].unique()))
    
    # Filtro de dados da conta corrente por competência
    dados_1_ = dados[(dados['Competência'] == competencia) & (dados['Origem'] == 'Conta Corrente')]

    # Métricas
    receitas = dados_1_[dados_1_['Receita/Despesa'] == 'Receita']['Valor'].sum()
    despesas = dados_1_[dados_1_['Receita/Despesa'] == 'Despesa']['Valor'].sum()
    saldo = receitas - despesas
    
    # Print de métricas
    st.markdown(f'## Competência: *{competencia}*')
    col1, col2, col3 = st.columns(3, gap='large')
    col1.metric('Receitas', f'R$ {receitas:,.2f}')
    col2.metric('Despesas', f'R$ {despesas:,.2f}')
    col3.metric('Saldo', f'R$ {saldo:,.2f}')

    # Print Gráfico
    tabela = pd.DataFrame({
        'Receita/Despesa': ['Receitas', 'Despesas', 'Saldo'],
        'Valor': [receitas, despesas, saldo]
    })
    grafico = alt.Chart(tabela).mark_bar().encode(
        x = alt.X('Receita/Despesa', title='Tipo'),
        y = alt.Y('Valor', title='Valor (R$)')
    )
    st.altair_chart(grafico)








