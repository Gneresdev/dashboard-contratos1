import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Contacta",
    page_icon="📋",
    layout="wide",
)

# --- Carregamento dos dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dadoslimpos.csv", sep=';')  # separador correto
    df['Data_Fim'] = pd.to_datetime(df['Data_Fim'], dayfirst=True, errors='coerce')

    siglas = {
        'AC': 'Assistente Comercial',
        'LG': 'Logistica',
        'RS': 'Recrutamento e seleção',
        'DP': 'Departamento pessoal',
        'AD': 'Analista de Dados'
    }
    df['Area'] = df['Area'].replace(siglas)
    
    return df

df = carregar_dados()

# --- Seleção da página ---
pagina = st.sidebar.selectbox("Escolha a página", ["Dashboard Geral", "Entrevistas"])

if pagina == "Dashboard Geral":

    # --- Barra Lateral (Filtros) ---
    st.sidebar.header("Filtros")

    areas = sorted(df['Area'].dropna().unique())
    areas_selecionadas = st.sidebar.multiselect("Selecione Área(s)", areas, default=areas)

    df_filtrado = df[df['Area'].isin(areas_selecionadas)]

    # --- Métricas e Indicadores ---
    st.title("Dashboards Contacta 🚀")

    # --- Contratos encerrando em dezembro/2025 por setor
    encerramentos = df_filtrado[
        (df_filtrado['Data_Fim'].dt.year == 2025) & 
        (df_filtrado['Data_Fim'].dt.month == 12)
    ]
    encerramentos_count = encerramentos['Area'].value_counts().reset_index()
    encerramentos_count.columns = ['Area', 'Encerramentos']

    # --- Contratos por área e turno (manhã, tarde, integral)
    contratos_por_turno = df_filtrado[df_filtrado['Data_Fim'].dt.year == 2025]
    contratos_por_turno = contratos_por_turno.groupby(['Area', 'Turno']).size().reset_index(name='Quantidade')

    # --- Contagem de assinaturas pendentes ---
    pendentes = df_filtrado[df_filtrado['Regularizado'] == "NÃO"]
    pendentes_count = pendentes['Area'].value_counts().reset_index()
    pendentes_count.columns = ['Area', 'Pendentes']

    # --- Layout dos KPIs ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Contratos encerrando em Dez/2025 por Área ⌛")
        if not encerramentos_count.empty:
            # Gráfico de barras empilhadas
            fig1 = px.bar(
                contratos_por_turno,
                x='Area', y='Quantidade', color='Turno',
                color_discrete_map={"Manhã": "#A7390E", "Tarde": "#DA03F7", "Integral": "#99F099"},
                labels={'Area': 'Setor', 'Quantidade': 'Quantidade de Contratos', 'Turno': 'Turno de Trabalho'},
                template="plotly_dark"
            )
            fig1.update_layout(
                showlegend=True,
                xaxis_title=None,
                yaxis_title="Quantidade",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig1, use_container_width=True)

        else:
            st.write("Nenhum contrato encerrando em Dezembro de 2025 nas áreas selecionadas.")

    with col2:
        st.subheader("Assinaturas Pendentes por Área ⚠️")
        if not pendentes_count.empty:
            fig2 = px.pie(
                pendentes_count, names='Area', values='Pendentes', 
                color='Area', color_discrete_sequence=px.colors.qualitative.Set1,
                template="plotly_dark"
            )
            fig2.update_traces(textinfo="percent+label", pull=[0.1, 0.1, 0.1, 0.1])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.write("Nenhuma assinatura pendente nas áreas selecionadas.")

    st.markdown("---")

    st.subheader("Setores com Mais Contratos Ativos 🟢")
    # Contagem de estagiários por setor
    estagiarios_count = df_filtrado['Area'].value_counts().reset_index()
    estagiarios_count.columns = ['Area', 'Quantidade de Estagiários']

    # Gráfico de barras horizontais para mostrar os setores com mais estagiários
    if not estagiarios_count.empty:
        fig4 = px.bar(
            estagiarios_count, x='Quantidade de Estagiários', y='Area', color='Area', text='Quantidade de Estagiários',
            color_discrete_sequence=px.colors.sequential.Viridis,
            template="plotly_dark"
        )
        fig4.update_layout(
            showlegend=False,
            xaxis_title="Quantidade de Estagiários",
            yaxis_title=None,
            xaxis_tickangle=0
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.write("Não há dados sobre estagiários ou contratos nas áreas selecionadas.")

    st.markdown("---")

    st.subheader("Dados Detalhados")
    st.dataframe(df_filtrado.reset_index(drop=True))

elif pagina == "Entrevistas":
    st.title("Dashboard de Entrevistas por Mês")

    # Carregando os dados de entrevistas
    entrevistas_df = pd.read_csv("entrevistas_total.csv", sep=';')  # ajuste se usar outro separador

    # Verificar se a coluna "Mês" existe
    if "Mês" not in entrevistas_df.columns:
        st.warning("A planilha entrevistas_total.csv não tem a coluna 'Mês'. Gráfico por mês não será exibido.")
    else:
        st.markdown("### Total de Entrevistas por Mês")
        entrevistas_por_mes = entrevistas_df.groupby("Mês")["Total"].sum().reset_index()

        fig = px.bar(entrevistas_por_mes, x="Mês", y="Total", text="Total", color="Mês")
        fig.update_layout(showlegend=False, yaxis_title="Entrevistas", xaxis_title="Mês")
        st.plotly_chart(fig, use_container_width=True)

    # Gráfico de entrevistas por semana
    st.markdown("---")
    st.markdown("### Total de Entrevistas por Semana")

    semanas = ["1° Semana", "2° Semana", "3° Semana", "4° Semana", "5° Semana"]
    totais_semanas = entrevistas_df[semanas].sum().reset_index()
    totais_semanas.columns = ["Semana", "Total de Entrevistas"]

    fig_semana = px.bar(totais_semanas, x="Semana", y="Total de Entrevistas",
                       text="Total de Entrevistas", title="Entrevistas por Semana")
    fig_semana.update_layout(yaxis_title="Quantidade")
    st.plotly_chart(fig_semana, use_container_width=True)

    st.markdown("---")
    st.markdown("### Dados Detalhados")
    st.dataframe(entrevistas_df)
