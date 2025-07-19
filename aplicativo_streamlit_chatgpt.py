
import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel("dados.xlsx")
    df["Data"] = pd.to_datetime(df["Data"])
    df["AnoMes"] = df["Data"].dt.to_period("M").astype(str)
    return df

df = carregar_dados()

# Sidebar de navegação
st.sidebar.title("📊 Menu")
pagina = st.sidebar.radio("Ir para", ["Resumo", "Evolução Temporal", "Cartão de Crédito", "Classificações", "Tabela Bruta"])

# Funções auxiliares
def resumo_financeiro(df):
    total_receitas = df[df["Receita/Despesa"] == "Receita"]["Valor"].sum()
    total_despesas = df[df["Receita/Despesa"] == "Despesa"]["Valor"].sum()
    saldo = total_receitas - total_despesas
    return total_receitas, total_despesas, saldo

# Página: Resumo
if pagina == "Resumo":
    st.title("💰 Resumo Financeiro")

    receitas, despesas, saldo = resumo_financeiro(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas", f"R$ {receitas:,.2f}")
    col2.metric("Despesas", f"R$ {despesas:,.2f}")
    col3.metric("Saldo", f"R$ {saldo:,.2f}", delta_color="inverse")

    st.subheader("Receitas e Despesas Mensais")
    df_mensal = df.groupby(["AnoMes", "Receita/Despesa"])["Valor"].sum().reset_index()
    fig = px.bar(df_mensal, x="AnoMes", y="Valor", color="Receita/Despesa", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# Página: Evolução Temporal
elif pagina == "Evolução Temporal":
    st.title("📈 Evolução das Despesas ao Longo do Tempo")
    despesas = df[df["Receita/Despesa"] == "Despesa"]
    df_temp = despesas.groupby("AnoMes")["Valor"].sum().reset_index()
    fig = px.line(df_temp, x="AnoMes", y="Valor", title="Despesas Mensais")
    st.plotly_chart(fig, use_container_width=True)

# Página: Cartão de Crédito
elif pagina == "Cartão de Crédito":
    st.title("💳 Análise do Cartão de Crédito")
    cartao = df[df["tipo_fonte"] == "cartao"]
    df_cartao = cartao.groupby("AnoMes")["Valor"].sum().reset_index()
    fig = px.bar(df_cartao, x="AnoMes", y="Valor", title="Gastos no Cartão por Mês")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 maiores gastos no cartão")
    top10 = cartao.sort_values("Valor", ascending=False).head(10)
    st.dataframe(top10[["Data", "Descrição", "Valor", "classificação"]])

# Página: Classificações
elif pagina == "Classificações":
    st.title("🧾 Análise por Categoria de Gastos")

    cat = df[df["Receita/Despesa"] == "Despesa"].groupby("classificação")["Valor"].sum().reset_index()
    cat = cat.sort_values("Valor", ascending=False)
    fig = px.pie(cat, values="Valor", names="classificação", title="Distribuição das Despesas por Categoria")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tabela por Classificação")
    st.dataframe(cat)

# Página: Tabela Bruta
elif pagina == "Tabela Bruta":
    st.title("📋 Base de Dados")
    st.dataframe(df)

    st.download_button("📥 Baixar Excel", data=df.to_excel(index=False), file_name="dados_filtrados.xlsx")
