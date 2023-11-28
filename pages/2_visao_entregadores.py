# Libraries

from haversine import haversine
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title= "Visão Entregadores", page_icon="🚚", layout= "wide")

# ---------------------------------------------------------------
# Funções
# ---------------------------------------------------------------
def top_deliveries(df1, top_asc):
  df_rapido = (df1.loc[:, ["Delivery_person_ID", "City", "Time_taken(min)"]]
                  .groupby(["City", "Delivery_person_ID"])
                  .max().sort_values(["Time_taken(min)","City"], ascending = top_asc)
                  .reset_index())

  df_aux01 = df_rapido.loc[df_rapido["City"] == "Metropolitian", :].head(10)
  df_aux02 = df_rapido.loc[df_rapido["City"] == "Semi-Urban", :].head(10)
  df_aux03 = df_rapido.loc[df_rapido["City"] == "Urban", :].head(10)
  df_aux = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index()
  return df_aux
# -------------------------------------------------------------------
def clean_code(df1):
  '''Esta função tem a responsabilidade de limpar o dataframe
  
  Tipos de limpeza:
  1. Remoção dos dados NaN
  2. Mudança do tipo da coluna de dados
  3. Remoção dos espaços das variáveis de texto
  4. Formatação da coluna de datas
  5. limpeza da coluna de tempo (remoção do texto da variável numérica)
  
  Input: Dataframe
  Output: Dataframe'''

  # 1. Convertendo a coluna Age de texto para número
  linhas_sel = df1.loc[:, "Delivery_person_Age"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)

  # 2. Convertendo a coluna Ratings de texto para número decimal (float)
  linhas_sel_rate = df1["Delivery_person_Ratings"] != "NaN "
  df1 = df1.loc[linhas_sel_rate, :].copy()
  df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)

  # 3. Limpando os NaN
  linhas_sel = df1["Road_traffic_density"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  linhas_sel = df1["City"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  linhas_sel = df1.loc[:, "City"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  linhas_sel = df1["Festival"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()

  # 4. Convertendo multiple_deliveries de texto para número inteiro (int)
  linhas_sel = df1.loc[:, "multiple_deliveries"] != "NaN "
  df1 = df1.loc[linhas_sel, :].copy()
  df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)

  # 5. Convertendo a coluna order_date de texto para data
  df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format = "%d-%m-%Y")

  # 6. Removendo os espaços dentro de strings/texto/object
  cols_strip = ["ID", "Delivery_person_ID", "Road_traffic_density", "Type_of_order", "Type_of_vehicle", "City", "Festival"]
  for i in cols_strip:
    df1.loc[:, i] = df1.loc[:, i].str.strip()

  # 7 Limpando a coluna de time taken
  df1["Time_taken(min)"] = df1["Time_taken(min)"].apply(lambda x: x.split( "(min) ")[1])
  df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)

  return df1

#import dataset
df = pd.read_csv("./dataset/train.csv")
df1 = df.copy()

# Limpando o dataset
df1 = clean_code(df)

# ==================================
# Barra lateral
# ===================================
st.header("Marketplace - Visão entregadores")
image_path = "./logo.png"
image = Image.open(image_path )
st.sidebar.image(image, width = 120)
st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fatest delivery in town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Selecione uma data limite")
date_slider = st.sidebar.slider(
  "Até qual valor?", 
  value = pd.datetime(2022, 4, 13),
  min_value = pd.datetime(2022,2,11),
  max_value = pd.datetime(2022, 4, 6),
  format = "DD-MM-YYYY")

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
  "Quais as condições do transito?",
  ["Low", "Medium", "High", "Jam"],
  default = ["Low", "Medium", "High", "Jam"])
st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by Christiano Peres - Comunidade DS")

# Filtro de data
linhas_selecionadas = df1["Order_Date"] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1["Road_traffic_density"].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==================================
# Layout no streamlit
# ===================================
tab1, tab2, tab3 = st.tabs (["Visão Gerencial", "-", "-"])

with tab1: 
    with st.container():
        st.markdown("# Overall Metrics ")
        col1, col2, col3, col4 = st.columns(4, gap = "large")
    with col1:
        # Maior idade dos entregadores
        
        maior_idade = df1["Delivery_person_Age"].max()
        col1.metric("Maior idade", maior_idade)
           
    with col2:
      # Menor idade dos entregadores
      
      menor_idade = df1["Delivery_person_Age"].min()
      col2.metric("Menor idade", menor_idade)
      
    with col3:
      # Melhor condição de veículos
    
      melhor_condicao = df1["Vehicle_condition"].max()
      col3.metric("Melhor condição de veículo", melhor_condicao)
      
    with col4:
      # Pior condição de veículos
      
      pior_condicao = df1["Vehicle_condition"].min()
      col4.metric("Pior condição de veículo", pior_condicao)
      
    with st.container():
      st.markdown("""---""")
      st.title("Avaliações")

      col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Avaliação médias por entregador")
        df_avg_ratings_per_delivery = (df1.loc[:, ["Delivery_person_ID", "Delivery_person_Ratings"]]
                                       .groupby(["Delivery_person_ID"]).mean()
                                       .reset_index()
                                       .round(2)
                                       .sort_values("Delivery_person_Ratings", ascending = False))
        st.dataframe(df_avg_ratings_per_delivery )
    with col2: 
        st.markdown("##### Avaliação média por transito")
        df_avg_rate_by_traffic = (df1.loc[:, ["Delivery_person_Ratings", "Road_traffic_density"]]
                                   .groupby(["Road_traffic_density"])
                                   .agg({"Delivery_person_Ratings": ["mean", "std"]}))
        df_avg_rate_by_traffic.columns = ["delivery_mean", "delivery_std"]
        st.dataframe(df_avg_rate_by_traffic.reset_index())

        st.markdown("##### Avaliação média por clima")
        df_avg_std_weather = (df1.loc[:, ["Delivery_person_Ratings", "Weatherconditions"]]
                                    .groupby(["Weatherconditions"])
                                    .agg({"Delivery_person_Ratings": ["mean", "std"]})
                                    .round(2))

        # mudança de nome das colunas
        df_avg_std_weather.columns = ["delivery_mean", "delivery_std"]
        st.dataframe(df_avg_std_weather.reset_index())

    with st.container():
       st.markdown("""---""")
       st.title("Velocidade de entrega")

       col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Top entregadores mais rápidos")
        df_aux = top_deliveries(df1, top_asc=True)
        st.dataframe(df_aux)
        
    with col2:
        st.markdown("##### Top entregadores mais lentos")
        df_aux = top_deliveries(df1, top_asc=False)
        st.dataframe(df_aux)
        
      