
# --- Minhas Finanças - Aplicativo Streamlit --- #

# Carregar de bibliotecas
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import openpyxl

# Configurações do Streamlit
st.set_page_config(
    page_title='Dashboard Financeiro',
    page_icon='💲',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'http://www.meusite.com.br',
        'Report a bug': "http://www.meuoutrosite.com.br",
        'About': "Esse app foi desenvolvido no nosso Curso."
    }
)

# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel('dados.xlsx', engine='openpyxl')
    df['Data'] = pd.to_datetime(df['Data'])
    df['AnoMes'] = df['Data'].dt.to_period('M').astype(str)
    return df

df = carregar_dados()


# Sidebar de navegação
with st.sidebar:

    menu = option_menu(
        menu_title = 'Menu Principal',
        options=['Resumo', 'Saldo Mensal', 'Status','D.board','Suporte'],
        icons=['house','basket', 'android2','bar-chart', 'bell'],
        menu_icon='cast',
        default_index=0,
        orientation='vertical',
        styles={
        'container': {'padding': '0!important', 'background-color': '#3b4733'},
        'icon': {'color': 'orange', 'font-size': '20px'},
        'nav-link-selected': {'background-color': 'green'},
        'nav-link': {
            'font-size': '18px',
            'text-align': 'left',
            'margin': '1px',
            '--hover-color': '#f8f4ec',
        },
    },
    )


# Página: Resumo
if menu == 'Resumo':
    st.title('Resumo Financeiro')

    # Sidebar secundário
    # competencia = st.sidebar.selectbox('Selecione a competência', sorted(df['Competência'].unique()))
    competencia = st.selectbox('Selecione a competência', sorted(df['Competência'].unique()))
    
    # Filtro de dados
    df_filtrado = df[(df['Competência'] == competencia) & (df['Origem'] == 'Conta Corrente')]

    # Métricas
    receitas = df_filtrado[df_filtrado['Receita/Despesa'] == 'Receita']['Valor'].sum()
    despesas = df_filtrado[df_filtrado['Receita/Despesa'] == 'Despesa']['Valor'].sum()
    saldo = receitas - despesas
    
    # Print de métricas
    # st.metric('Receitas', f'R$ {receitas:,.2f}')
    # st.metric('Despesas', f'R$ {despesas:,.2f}')
    # st.metric('Saldo', f'R$ {saldo:,.2f}')
    st.markdown(f'## Competência: *{competencia}*')
    col1, col2, col3 = st.columns(3, gap='large')
    col1.metric('Receitas', f'R$ {receitas:,.2f}')
    col2.metric('Despesas', f'R$ {despesas:,.2f}')
    col3.metric('Saldo', f'R$ {saldo:,.2f}')

    # Gráfico
    fig, ax = plt.subplots()
    ax.bar(['Receitas', 'Despesas', 'Saldo'], [receitas, despesas, saldo], color=['green', 'red', 'blue'])
    ax.set_ylabel('Valor (R$)')
    st.pyplot(fig)
    # st.plotly_chart(fig, use_container_width=True)








