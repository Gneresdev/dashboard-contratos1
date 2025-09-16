import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- Configuração da Página (Primeiro comando) ---
st.set_page_config(
    page_title="Contacta",
    page_icon="📋",
    layout="wide",
)

# --- Carregando o CSS Externo ---
with open('assets/css/styles.css') as f:
    css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# --- Adicionando o Logo na Barra Lateral ---
st.sidebar.markdown("""
    <style>
        /* Estilo para centralizar a logo na Sidebar */
        .sidebar-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 40px;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("assets/images/logo.png", width=270)  # Ajuste o caminho se necessário

# --- Carregamento dos dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dadoslimpos.csv", sep=';')  # separador correto
    df['Data_Fim'] = pd.to_datetime(df['Data_Fim'], dayfirst=True, errors='coerce')

    siglas = {
        'AC': 'Assistente Comercial',
        'LG': 'Logística',
        'RS': 'Recrutamento e Seleção',
        'DP': 'Departamento Pessoal',
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
    st.title("Dashboards Contacta🚀")

    st.markdown("---")


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
        st.markdown('<h3 style="text-align: center;">Contratos encerrando em Dez/2025 por Área</h3>', unsafe_allow_html=True)
        if not encerramentos_count.empty:
            fig1 = px.bar(
                contratos_por_turno,
                x='Area', y='Quantidade', color='Turno',
                color_discrete_map={"Manha": "#9B4DFF", "Tarde": "#3C8F8F", "Integral": "#C8B7F7"},
                labels={'Area': 'Setor', 'Quantidade': 'Quantidade de Contratos', 'Turno': 'Turno de Trabalho'},
                template="plotly_dark"
            )
            fig1.update_layout(
                showlegend=True,
                xaxis_title=None,
                yaxis_title="Quantidade",
                xaxis_tickangle=0
            )
            st.plotly_chart(fig1, use_container_width=True)

        else:
            st.write("Nenhum contrato encerrando em Dezembro de 2025 nas áreas selecionadas.")

    with col2:
        st.markdown('<h3 style="text-align: center;">Assinaturas Pendentes</h3>', unsafe_allow_html=True)
        if not pendentes_count.empty:
            # Criando um gráfico de rosca (donut chart)
            fig2 = go.Figure(data=[go.Pie(
                labels=pendentes_count['Area'],
                values=pendentes_count['Pendentes'], 
                hole=0.3,  # Faz o "buraco" no centro, criando o formato de rosca
                textinfo="percent+label",  # Exibe o texto (percentual + label)
                pull=[0.1, 0.1, 0.1, 0.1],  # Opcional: pode afastar as fatias
                marker=dict(colors=["#9B4DFF", "#3C8F8F", "#D985F3", "#FF9B8F"]),  # Cores personalizadas
            )])

            # Customizando a aparência do gráfico
            fig2.update_layout(
                title="Distribuição de Assinaturas Pendentes por Área",
                showlegend=True,
                template="plotly_dark",  # Estilo do gráfico
                title_x=0.5,  # Alinha o título ao centro
                margin=dict(t=50, b=50, l=50, r=50)  # Ajusta as margens para melhorar o espaçamento
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.write("Nenhuma assinatura pendente nas áreas selecionadas.")

    st.markdown("---")

    st.subheader("Setores com Mais Contratos Ativos")
    # Contagem de estagiários por setor
    estagiarios_count = df_filtrado['Area'].value_counts().reset_index()
    estagiarios_count.columns = ['Area', 'Quantidade de Estagiários']

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
    st.title("Dashboard de Entrevistas por Mês📋")

    st.markdown("---")

    entrevistas_df = pd.read_csv("entrevistas_total.csv", sep=';')  # ajuste se usar outro separador

    # Paleta de cores personalizada (mantida)
    paleta_cores = ["#9B4DFF", "#3C8F8F", "#D985F3", "#692AFC", "#392557"]

    if "Mês" not in entrevistas_df.columns:
        st.warning("A planilha entrevistas_total.csv não tem a coluna 'Mês'. Gráfico por mês não será exibido.")
    else:
        st.markdown("### Total de Entrevistas por Mês")
        entrevistas_por_mes = entrevistas_df.groupby("Mês")["Total"].sum().reset_index()

        # Ordenar os meses corretamente, se possível
        try:
            entrevistas_por_mes["Mês"] = pd.Categorical(entrevistas_por_mes["Mês"],
                                                        categories=["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                                                                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
                                                        ordered=True)
            entrevistas_por_mes = entrevistas_por_mes.sort_values("Mês")
        except:
            pass  # caso os nomes não sejam meses, pula ordenação

        # Gráfico de linha com marcadores para melhor visualização temporal
        fig = px.line(entrevistas_por_mes, x="Mês", y="Total", text="Total", markers=True,
                      line_shape="linear", color_discrete_sequence=[paleta_cores[0]])  # Usando só a primeira cor
        fig.update_traces(textposition="top center")
        fig.update_layout(yaxis_title="Entrevistas", xaxis_title="Mês")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Total de Entrevistas por Semana")

    semanas = ["1° Semana", "2° Semana", "3° Semana", "4° Semana", "5° Semana"]
    totais_semanas = entrevistas_df[semanas].sum().reset_index()
    totais_semanas.columns = ["Semana", "Total de Entrevistas"]

    # Gráfico de pizza para mostrar proporção semanal
    fig_semana = px.pie(totais_semanas, names="Semana", values="Total de Entrevistas",
                        title="Distribuição de Entrevistas por Semana",
                        color_discrete_sequence=paleta_cores,
                        hole=0.4)
    fig_semana.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_semana, use_container_width=True)

    st.markdown("---")
    st.markdown("### Dados Detalhados")
    st.dataframe(entrevistas_df)
