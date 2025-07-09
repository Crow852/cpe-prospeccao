import streamlit as st
import pandas as pd
from scraping_google import buscar_empresas_google_maps
from PIL import Image

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(
    page_title="Prospecção de Clientes – Parceiros Licenciados",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CORES PERSONALIZADAS ==========
PRIMARY_COLOR = "#f5b821"  # Amarelo da logo
TEXT_COLOR = "#ffffff"     # Texto branco
BACKGROUND_COLOR = "#1c1c1c"  # Fundo escuro

# ========== LOGO ==========
logo = Image.open("Logo_Parceiro_Licenciados_Original.png")
st.image(logo, width=300)

# ========== TÍTULO ==========
st.markdown(
    "<h1 style='color: white; font-size: 32px;'>Prospecção de Clientes – Parceiros Licenciados</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# ========== FORMULÁRIO ==========
tipo_busca = st.radio("Você quer buscar por:", ["Estado", "Cidade"])
local = st.text_input("Digite o nome do Estado ou Cidade:")

filtros = [
    "Empresas de agrimensura", "Topógrafos", "Empresas de Topografia",
    "Empresas de construção civil", "Empresas de engenharia", "Arquitetos",
    "Empresas de geotecnia e sondagem", "Empresas de mineração", "Empresas de geofísica",
    "Empresas de terraplanagem", "Construtoras de rodovias e ferrovias",
    "Empresas de infraestrutura urbana", "Empresas de georreferenciamento",
    "Empresas de mapeamento por drone", "Startups de geotecnologia",
    "Cooperativas agrícolas com foco em precisão", "Empresas de reflorestamento e monitoramento ambiental",
    "Empresas de SIG", "Empresas de fotogrametria", "Consultorias ambientais",
    "Bureaus de cartografia", "Empresas de regularização fundiária",
    "Universidades de engenharia civil e agrimensura"
]

filtro_escolhido = st.selectbox("Escolha o tipo de empresa que deseja buscar:", filtros)
quantidade = st.slider("Quantos resultados você deseja buscar?", min_value=5, max_value=100, step=5, value=25)

status = st.empty()

# ========== BUSCA ==========
if st.button("🔍 Buscar empresas"):
    if not local.strip():
        st.warning("Por favor, digite o nome do estado ou cidade.")
    else:
        termo = f"{filtro_escolhido} em {local}"
        st.info(f"Buscando por: **{termo}** — até {quantidade} empresas...")

        def feedback_callback(msg):
            status.info(msg)

        dados = buscar_empresas_google_maps(termo, limite=quantidade, feedback_callback=feedback_callback)

        if dados:
            df = pd.DataFrame(dados)

            # Nome com link clicável
            df["Nome"] = df.apply(lambda row: f"<a href='{row['Link']}' target='_blank'>{row['Nome']}</a>", axis=1)

            # Visualização formatada
            df_visual = df[["Nome", "Telefone", "Endereço"]]

            # Tabela estilizada
            st.markdown("### 🗂️ Resultados encontrados")
            st.write(df_visual.to_html(escape=False, index=False), unsafe_allow_html=True)

            # Armazena resultado na sessão
            st.session_state["df_resultados"] = df
        else:
            st.warning("Nenhuma empresa encontrada.")

# ========== MARCAÇÃO DE CLIENTES CONTATADOS ========== 
if "df_resultados" in st.session_state:
    df_resultados = st.session_state["df_resultados"]
    st.markdown("---")
    st.markdown("### 📌 Marcar clientes contatados")

    contatados = []
    
    # Cabeçalho da tabela
    header_col1, header_col2, header_col3, header_col4 = st.columns([1, 5, 2, 5])
    header_col1.markdown("**✓**")
    header_col2.markdown("**Nome**")
    header_col3.markdown("**Telefone**")
    header_col4.markdown("**Endereço**")

    for i, row in df_resultados.iterrows():
        col1, col2, col3, col4 = st.columns([1, 5, 2, 5])
        with col1:
            marcado = st.checkbox("", key=f"chk_{i}")
        with col2:
            st.markdown(f"<a href='{row['Link']}' target='_blank'>{row['Nome']}</a>", unsafe_allow_html=True)
        with col3:
            st.write(row.get("Telefone", ""))
        with col4:
            endereco = row.get("Endereço", "").replace("\n", "").replace("", "").strip()
            st.write(endereco)
        if marcado:
            contatados.append(row)

    if st.button("✅ Incluir contatados"):
        if contatados:
            df_novos = pd.DataFrame(contatados)
            if "clientes_contatados" in st.session_state:
                st.session_state["clientes_contatados"] = pd.concat(
                    [st.session_state["clientes_contatados"], df_novos]
                ).drop_duplicates("Link")
            else:
                st.session_state["clientes_contatados"] = df_novos
            st.success(f"{len(contatados)} cliente(s) marcado(s) como contatado(s).")
        else:
            st.info("Nenhum novo cliente marcado.")


# ========== EXIBIR CLIENTES CONTATADOS ==========
st.markdown("---")
if st.button("📋 Ver clientes contatados"):
    if "clientes_contatados" in st.session_state and not st.session_state["clientes_contatados"].empty:
        df_contatados = st.session_state["clientes_contatados"].copy()
        df_contatados["Nome"] = df_contatados.apply(lambda row: f"<a href='{row['Link']}' target='_blank'>{row['Nome']}</a>", axis=1)
        df_visual = df_contatados[["Nome", "Telefone", "Endereço"]]
        st.markdown("### 👥 Clientes já contatados")
        st.write(df_visual.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("Nenhum cliente contatado ainda.")
