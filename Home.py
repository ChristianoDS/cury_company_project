import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = "Home",
    page_icon = "🎲")

#image_path = "./logo.png"
image = Image.open("./logo.png")
st.sidebar.image(image, width = 120)
st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fatest delivery in town")
st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by Christiano Peres - Comunidade DS")
st.sidebar.markdown("""---""")
st.write("# Cury Company Growth Dashboard")
st.markdown("""
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de Geolocalização
    - Visão entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for help
    - Time de Data Science no Discord
        - christianoperes""")