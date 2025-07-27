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
    # initial_sidebar_height=500
)


# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel('dados.xlsx', engine='openpyxl')
    df['Data'] = pd.to_datetime(df['Data'])
    return df
dados = carregar_dados()


# Sidebar de navegação
with st.sidebar:

    menu = option_menu(
        menu_title = 'Opções',
        menu_icon='cast',
        options=[
            'Conta corrente', 
            'Cartão de crédito', 
            'Despesas por categoria',
            'Despesas por mês'
            ],
        icons=[
            'currency-dollar',
            'credit-card', 
            'cup-hot', 
            'calendar-fill'
            ],
        orientation='vertical',
        styles={ 
        'container': {'padding': '0!important', 'background-color': "#2c4731"},
        'icon': {'color': 'orange', 'font-size': '14px'},
        'nav-link-selected': {'background-color': 'green'},
        'nav-link': {
            'font-size': '14px',
            'text-align': 'left',
            'margin': '1px',
            '--hover-color': "#679750",
            },
        }
    )

######################################
### Página  Conta Corrente ###########
######################################
if menu == 'Conta corrente':
    
    # Título da página
    st.title('Conta Corrente')

    # Seleção compêtencia
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

    # Gráfico Receitas/Despesas/Saldo ----
    
    # Subtítulo
    st.subheader('Gráfico Saldo')
    
    # Tabela para o gráfico
    tabela_saldo = pd.DataFrame({
        'Receita/Despesa': ['Receitas', 'Despesas', 'Saldo'],
        'Valor': [receita_mes_atual, despesa_mes_atual, saldo_mes_atual]
    })
    
    # Gráfico
    grafico_saldo = alt.Chart(tabela_saldo).mark_bar().encode(
        x = alt.X('Receita/Despesa', title='', 
                  axis=alt.Axis(labelAngle=0), 
                  scale=alt.Scale(paddingInner=0.5)
                  ),
        y = alt.Y('Valor', title='Valor (R$)')
    )
    rotulo_grafico_saldo = grafico_saldo.mark_text(
        align='center',
        baseline='middle',
        size=12,
        dy=-10,
        color='white'
    ).encode(
        text=alt.Text('Valor:Q', format='.2f'),
        size=alt.value(20)
    )
    
    # Print
    st.altair_chart(grafico_saldo+rotulo_grafico_saldo, use_container_width=True)
    
    

    

######################################
### Página  Conta Corrente ###########
######################################
if menu == 'Cartão de crédito':
    
    # Print título da página
    st.title('Cartão de Crédito')



######################################
### Página  Despesas por categoria ###
######################################
if menu == 'Despesas por categoria':
    
    # Título da página
    st.title('Despesas por categoria')
    
    # Seleção compêtencia
    competencia = st.selectbox('Competência', sorted(dados['Competência'].unique()))
    
    # Gráfico de despesas por categoria ----
    
    # Filtrar dados de despesas
    df_despesas = dados[(dados['Receita/Despesa'] == 'Despesa') & (dados['Competência'] == competencia)]
    
    # Agregar valores por categoria
    tabela_despesas = df_despesas.groupby('Categoria')['Valor'].sum().reset_index()

    # Gráfico de pizza
    grafico_pizza = alt.Chart(tabela_despesas).mark_arc(
        innerRadius=50,
        outerRadius=150
        ).encode(
        theta=alt.Theta('Valor:Q', title='Valor (R$)', stack=True),
        # color=alt.Color('Categoria:N', title='Categoria', legend=alt.Legend(orient='top-right')),
        color=alt.Color('Categoria:N', title='Categoria', legend=None, scale=alt.Scale(scheme='category20')),
        tooltip=[alt.Tooltip('Categoria:N', title='Categoria'), alt.Tooltip('Valor:Q', title='Valor (R$)', format='.2f')]
    ).properties(
        width=700,
        height=400
    )
    
    # Configurar o gráfico para exibir os rótulos
    rotulo_grafico_pizza_nome = grafico_pizza.mark_text(radius=200, size=12).encode(text=alt.Text('Categoria:N'))
    rotulo_grafico_pizza_valor = grafico_pizza.mark_text(radius=170, size=12).encode(text=alt.Text('Valor:Q', format='.2f'))
    
    # Print
    st.altair_chart(grafico_pizza+rotulo_grafico_pizza_nome+rotulo_grafico_pizza_valor, use_container_width=True)


######################################
### Página  Conta Corrente ###########
######################################
if menu == 'Despesas por mês':
    
    # Título da página
    st.title('Despesas Mensais')

    # Gráfico de despesas mensais ----
    
    # Filtrar dados de despesas
    df_despesas_mensais = dados[(dados['Receita/Despesa'] == 'Despesa') & (dados['Origem'] == 'Conta Corrente')]

    # Agregar valores por competência
    tabela_despesas = df_despesas_mensais.groupby('Competência')['Valor'].sum().reset_index()

    # Criar índice numérico para simular o scroll
    tabela_despesas['indice'] = range(len(tabela_despesas))

    # Slider para selecionar faixa de Competência
    inicio = st.slider(
        'Intervalo',
        min_value=0,
        max_value=max(tabela_despesas['indice']) - 6,
        value=0,
        step=1,
    )

    # Filtrar os dados para mostrar apenas uma parte (como se fosse um scroll)
    tabela_filtrada = tabela_despesas[(tabela_despesas['indice'] >= inicio) & (tabela_despesas['indice'] < inicio + 6)]

    # Gráfico 
    grafico_despesas = alt.Chart(tabela_filtrada).mark_bar().encode(
        x=alt.X('Competência:N', title='', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Valor:Q', title='Valor (R$)')
    ).properties(
        width=700,
        height=400
    )

    # Print
    st.altair_chart(grafico_despesas, use_container_width=True)


