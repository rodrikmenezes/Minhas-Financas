import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados
df = pd.read_excel("dados.xlsx", sheet_name="Extrato", engine="openpyxl")

# Converter a coluna de data para datetime
df["Data"] = pd.to_datetime(df["Data"])

# Página principal
st.title("Dashboard Financeiro Pessoal")

# Menu lateral
menu = st.sidebar.selectbox("Selecione a tela", [
    "Conta Corrente",
    "Cartão de Crédito",
    "Resumo Mensal",
    "Categorias de Gastos",
    "Evolução do Saldo"
])

# Tela 1: Conta Corrente
if menu == "Conta Corrente":
    competencia = st.sidebar.selectbox("Selecione a competência", sorted(df["Competência"].unique()))
    df_filtrado = df[(df["Competência"] == competencia) & (df["Origem"] == "Conta Corrente")]

    receitas = df_filtrado[df_filtrado["Receita/Despesa"] == "Receita"]["Valor"].sum()
    despesas = df_filtrado[df_filtrado["Receita/Despesa"] == "Despesa"]["Valor"].sum()
    saldo = receitas - despesas

    st.subheader(f"Resumo da Conta Corrente - {competencia}")
    st.metric("Receitas", f"R$ {receitas:,.2f}")
    st.metric("Despesas", f"R$ {despesas:,.2f}")
    st.metric("Saldo", f"R$ {saldo:,.2f}")

    # Gráfico de barras
    fig, ax = plt.subplots()
    ax.bar(["Receitas", "Despesas", "Saldo"], [receitas, despesas, saldo], color=["green", "red", "blue"])
    ax.set_ylabel("Valor (R$)")
    st.pyplot(fig)

# Tela 2: Cartão de Crédito
elif menu == "Cartão de Crédito":
    df_cartao = df[df["Origem"] == "Cartão de Crédito"]
    uso_mensal = df_cartao.groupby("Competência")["Valor"].sum()

    st.subheader("Utilização Mensal do Cartão de Crédito")
    fig, ax = plt.subplots()
    uso_mensal.plot(kind="bar", ax=ax, color="purple")
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Competência")
    st.pyplot(fig)

# Tela 3: Resumo Mensal
elif menu == "Resumo Mensal":
    resumo = df.groupby(["Competência", "Receita/Despesa"])["Valor"].sum().unstack().fillna(0)
    resumo["Saldo"] = resumo.get("Receita", 0) - resumo.get("Despesa", 0)

    st.subheader("Resumo Mensal")
    st.dataframe(resumo.style.format("R$ {:,.2f}"))

# Tela 4: Categorias de Gastos
elif menu == "Categorias de Gastos":
    df_despesas = df[df["Receita/Despesa"] == "Despesa"]
    categorias = df_despesas.groupby("Descrição")["Valor"].sum().sort_values(ascending=False).head(10)

    st.subheader("Top 10 Categorias de Gastos")
    fig, ax = plt.subplots()
    categorias.plot(kind="barh", ax=ax, color="orange")
    ax.set_xlabel("Valor (R$)")
    st.pyplot(fig)

# Tela 5: Evolução do Saldo
elif menu == "Evolução do Saldo":
    df_sorted = df.sort_values("Data")
    df_sorted["Valor Ajustado"] = df_sorted.apply(lambda row: row["Valor"] if row["Receita/Despesa"] == "Receita" else -row["Valor"], axis=1)
    df_sorted["Saldo Acumulado"] = df_sorted["Valor Ajustado"].cumsum()

    st.subheader("Evolução do Saldo ao Longo do Tempo")
    fig, ax = plt.subplots()
    ax.plot(df_sorted["Data"], df_sorted["Saldo Acumulado"], color="blue")
    ax.set_ylabel("Saldo Acumulado (R$)")
    ax.set_xlabel("Data")
    st.pyplot(fig)

